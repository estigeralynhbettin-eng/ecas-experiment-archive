"""Scope-bound local tooling. No network or model calls in this module."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / 'EXECUTION_CONFIG.json').read_text(encoding='utf-8'))
LANE = Path(CONFIG['runtime_lane'])
sys.path.insert(0, str(LANE / 'runtime/scripts'))
from ec_field_security_engine_v3 import compile_model_ir, compile_policy, evaluate as evaluate_ecas, PolicyError

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify_inputs():
    for item in read(ROOT / 'EXECUTION_INPUT_MANIFEST.json'):
        if sha(item['path']) != item['sha256']:
            raise RuntimeError('Frozen input changed: ' + item['path'])

def tool(argv, folder, name, timeout=25):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    process = subprocess.run([str(x) for x in argv], capture_output=True, text=True, encoding='utf-8', timeout=timeout)
    (folder / (name + '.stdout.txt')).write_text(process.stdout, encoding='utf-8')
    (folder / (name + '.stderr.txt')).write_text(process.stderr, encoding='utf-8')
    return process

def adapt(task, envelope):
    packet = read(ROOT / 'generation_inputs' / task / 'packet.json')
    value = json.loads(json.dumps(envelope))
    abi = packet['common_adapter']
    value.update(subject={'id': abi['subject_id'], 'role': abi['subject_role']}, action=packet['target']['operation'],
                 resource={'id': abi['resource_id'], 'system': packet['target']['system'], 'version': packet['target']['version']})
    return value

def capabilities(folder):
    result = tool([LANE / 'tools/opa', 'capabilities', '--current'], folder, 'capabilities')
    if result.returncode:
        raise RuntimeError('Cannot discover OPA capabilities')
    value = json.loads(result.stdout)
    forbidden = {'http.send', 'net.lookup_ip_addr', 'opa.runtime', 'rand.intn', 'time.now_ns', 'print', 'internal.print'}
    value['builtins'] = [x for x in value['builtins'] if x['name'] not in forbidden]
    value['allow_net'] = []
    dump(Path(folder) / 'restricted_capabilities.json', value)

def strip_location(value):
    if isinstance(value, dict):
        return {k: strip_location(v) for k, v in value.items() if k not in ('location', 'Location')}
    if isinstance(value, list):
        return [strip_location(v) for v in value]
    return value

def policy_checks(rego, folder, do_lint):
    """Preserve original, fmt deterministic copy, prove AST equality, then check/lint."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    original = folder / 'original.rego'
    original.write_text(rego, encoding='utf-8')
    policy = folder / 'external_pilot/policy.rego'
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(rego, encoding='utf-8')
    before = tool([LANE / 'tools/opa', 'parse', '--format=json', original], folder, 'ast_before')
    formatting = tool([LANE / 'tools/opa', 'fmt', '--write', policy], folder, 'format')
    after = tool([LANE / 'tools/opa', 'parse', '--format=json', policy], folder, 'ast_after')
    same = before.returncode == after.returncode == formatting.returncode == 0 and strip_location(json.loads(before.stdout)) == strip_location(json.loads(after.stdout))
    if before.returncode == after.returncode == formatting.returncode == 0 and not same:
        raise RuntimeError('OPA fmt changed AST semantics; stop instead of model repair')
    receipt = {'original_sha256': sha(original), 'formatted_sha256': sha(policy), 'parse_before_exit': before.returncode,
               'format_exit': formatting.returncode, 'parse_after_exit': after.returncode, 'ast_semantics_equal_without_location': same,
               'classification': 'DETERMINISTIC_FORMAT_ONLY_NOT_MODEL_REPAIR'}
    dump(folder / 'FORMAT_RECEIPT.json', receipt)
    checked = tool([LANE / 'tools/opa', 'check', '--strict', '--capabilities', LANE / 'outputs/t0/restricted_capabilities.json', policy], folder, 'compile')
    value = {'policy_path': str(policy), 'original_path': str(original), 'compile_exit': checked.returncode,
             'compile_error': checked.stderr[:4000], 'format_receipt': receipt, 'lint_exit': None, 'lint_report': None}
    if do_lint:
        lint = tool([LANE / 'tools/regal', 'lint', '--disable', 'directory-package-mismatch', '--format', 'json', '--timeout', '20s', policy], folder, 'lint')
        value['lint_exit'] = lint.returncode
        try:
            value['lint_report'] = json.loads(lint.stdout)
        except ValueError:
            value['lint_report'] = {'error': lint.stderr[:3000]}
    value['accepted'] = same and checked.returncode == 0 and (not do_lint or value['lint_exit'] == 0)
    dump(folder / 'CHECKS.json', value)
    return value

def rego_decision(policy, envelope, folder, name):
    path = Path(folder) / (name + '.input.json')
    dump(path, envelope)
    result = tool([LANE / 'tools/opa', 'eval', '--capabilities', LANE / 'outputs/t0/restricted_capabilities.json', '--format=json', '--data', policy,
                   '--input', path, 'data.external_pilot.allow'], folder, name)
    if result.returncode:
        return {'status': 'EVALUATION_ERROR', 'decision': None, 'exit_code': result.returncode}
    expressions = json.loads(result.stdout).get('result', [])
    if len(expressions) != 1 or len(expressions[0].get('expressions', [])) != 1:
        return {'status': 'UNDEFINED_OR_AMBIGUOUS', 'decision': None, 'exit_code': 0}
    decision = expressions[0]['expressions'][0]['value']
    if type(decision) is not bool:
        return {'status': 'NON_BOOLEAN', 'decision': None, 'exit_code': 0}
    return {'status': 'EXECUTED', 'decision': 'allow' if decision else 'deny', 'exit_code': 0}

def run_tests(task, policy, tests, folder):
    rows = []
    for index, test in enumerate(tests):
        if not isinstance(test, dict) or test.get('expected') not in ('allow', 'deny') or not isinstance(test.get('input'), dict):
            raise ValueError('Malformed developer test')
        actual = rego_decision(policy, adapt(task, test['input']), folder, 'dev_%02d' % index)
        rows.append({'id': test.get('id', str(index)), 'expected': test['expected'], 'actual': actual,
                     'pass': actual['status'] == 'EXECUTED' and actual['decision'] == test['expected']})
    if not rows or not {'allow', 'deny'}.issubset({x['expected'] for x in rows}):
        raise ValueError('Developer tests lack positive/negative coverage')
    result = {'passed': all(x['pass'] for x in rows), 'rows': rows}
    dump(Path(folder) / 'DEVELOPER_RESULTS.json', result)
    return result

def ground_extraction(task, extraction):
    """Only exact declared neutral objects become IDs; conditions cannot change."""
    packet = read(ROOT / 'generation_inputs' / task / 'packet.json')
    org = read(ROOT / 'generation_inputs' / task / 'organization_schema.json')
    output = json.loads(json.dumps(extraction))
    mappings = []
    exact = {'subject': packet['common_adapter']['envelope_representation']['subject'],
             'resource': packet['common_adapter']['envelope_representation']['resource']}
    for index, component in enumerate(output.get('components', [])):
        for field in ('subject', 'action', 'resource'):
            original = component.get(field)
            if isinstance(original, dict) and field in exact and original == exact[field]:
                component[field] = original['id']
                mappings.append({'index': index, 'field': field, 'original': original, 'declared_id': original['id']})
            if component.get(field) not in org[field]:
                return output, {'accepted': False, 'reason': field + ' outside declared organization schema', 'mappings': mappings}
    return output, {'accepted': True, 'mappings': mappings, 'conditions_changed': False}

def source_reference_check(packet, reference):
    """Validate a visible ID and optional text/title fragment without rewriting it."""
    result={'original_reference':reference,'accepted':False,'binding_kind':None}
    if not isinstance(reference,str) or not reference:
        return dict(result,reason='SOURCE_REFERENCE_NOT_NONEMPTY_STRING')
    base,separator,fragment=reference.partition('#')
    result.update(base_evidence_id=base,original_fragment=fragment if separator else None)
    sources={x['evidence_id']:x for x in packet['visible_sources']}
    if base not in sources:return dict(result,reason='UNKNOWN_BASE_EVIDENCE_ID')
    source=sources[base]
    result.update(source_id=source.get('source_id'),source_metadata_sha256=source.get('source_sha256'))
    if not separator:return dict(result,accepted=True,binding_kind='VISIBLE_BASE_ID')
    def normalized(text):return re.sub(r'\s+',' ',text).strip().casefold()
    needle=normalized(fragment)
    if not needle:return dict(result,reason='EMPTY_FRAGMENT')
    content=source['content']
    text=content if isinstance(content,str) else json.dumps(content,ensure_ascii=False,sort_keys=True)
    result['visible_text_sha256']=hashlib.sha256(text.encode('utf-8')).hexdigest()
    result['normalized_fragment']=needle
    headings=[]
    for line_number,line in enumerate(text.splitlines(),1):
        heading=re.match(r'^\s*#{1,6}\s+(.+?)\s*#*\s*$',line)
        if heading and normalized(heading.group(1))==needle:
            headings.append({'line_number':line_number,'original_heading':heading.group(1)})
    if headings:
        return dict(result,accepted=True,binding_kind='EXACT_NORMALIZED_VISIBLE_HEADING',heading_locations=headings,
                    original_source_reference_preserved=True)
    haystack=normalized(text)
    position=haystack.find(needle)
    if position>=0:
        return dict(result,accepted=True,binding_kind='NORMALIZED_VISIBLE_TEXT_FRAGMENT',normalized_text_offset=position,
                    original_source_reference_preserved=True)
    return dict(result,reason='FRAGMENT_NOT_IN_VISIBLE_SOURCE')
