"""Prepare all-operation semantics from the frozen engine, not from evaluation feedback."""
import json
from pathlib import Path
from pilot_lib import ROOT,CONFIG,LANE,read,dump,sha,verify_inputs
verify_inputs()
dest=ROOT/'DOCUMENTED_OPERATOR_SEMANTICS.json'
if dest.exists():raise RuntimeError('Documentation prepared already')
meaning={
 'content_type_allowlist':'Allow string media types in the documented allowlist, ignoring parameters after a semicolon.',
 'request_size_limit':'The path contains a trusted nonnegative integer byte count; allow if it is <=max_bytes.',
 'allowed_fields':'The path must be an object; reject keys outside fields.',
 'required':'Require the path to exist; reject null unless allow_null is true.',
 'strict_type':'Require the declared type with no coercion. Integer excludes booleans and floating-point values.',
 'length_cardinality':'Require string/list/object length within inclusive min/max.',
 'number_range_precision':'Require a finite number within optional inclusive bounds and decimal scale; exclude booleans.',
 'enum_allowlist':'Require membership in values.',
 'named_validator':'Require a registered validator to accept the value.',
 'canonical_form':'Require string to equal its specified Unicode/whitespace-normalized form.',
 'date_order':'Require earlier ISO date < later ISO date, or <= when allow_equal.',
 'age_matches_dob':'Require integer age to match age derived from dob/as_of ISO dates within tolerance_years.',
 'state_transition':'Require (current_state,requested_state) to occur in transitions.',
 'server_derived_reject':'Reject whenever the path EXISTS, regardless of its value, to forbid client submission of a server-owned field. It is not a boolean-state permission test.',
 'bounded_guard_dnf':'ALLOW when ANY alternative has ALL clauses true. Otherwise reject. Missing values follow on_missing; comparisons use registered request/trusted paths or typed literals.'}
schema=read(ROOT/'execution_inputs/ecas_prompt_schema.json')
ops=[x[0] for x in schema['rule_variants']];assert set(ops)==set(meaning)
docs={'policy_semantics':'Every rule is a constraint. Allow only when all rules have no violation; these are not deny-trigger predicates. Missing inputs reject unless the operation explicitly supports skip.','operation_columns':['op','runtime_meaning'],'operations':[[op,meaning[op]] for op in ops]}
dump(dest,docs)
dump(ROOT/'DOCUMENTATION_SOURCE_RECEIPT.json',{'classification':'ALL_OPERATION_INTERFACE_DOCUMENTATION_NOT_CASE_FEEDBACK','engine_v2_path':str(LANE/'runtime/scripts/ec_field_security_engine_v2.py'),'engine_v2_sha256':sha(LANE/'runtime/scripts/ec_field_security_engine_v2.py'),'engine_v3_path':str(LANE/'runtime/scripts/ec_field_security_engine_v3.py'),'engine_v3_sha256':sha(LANE/'runtime/scripts/ec_field_security_engine_v3.py'),'all_ops':ops,'source_functions':['v2._evaluate_rule','v2._evaluate_value_rule','v3._evaluate_rule'],'new_business_sources':0,'first_candidates_in_prompt':False,'final_fixtures_in_prompt':False})
print(json.dumps({'all_operations':len(ops),'docs_bytes':len(json.dumps(docs,separators=(',',':')).encode())}))
