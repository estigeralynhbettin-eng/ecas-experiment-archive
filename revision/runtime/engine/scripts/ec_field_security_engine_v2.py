#!/usr/bin/env python3
"""Schema-validated, evidence-admitted, fail-closed EC field-security runtime V2.

The engine executes only a closed registry of deterministic operations. Model
output is data, never code, regex, SQL, templates, or dynamically imported
validators.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import math
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Iterable

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
POLICY_SCHEMA_PATH = ROOT / "EC_FIELD_SECURITY_POLICY_SCHEMA_V2.json"
CONTRACT_SCHEMA_PATH = ROOT / "EC_EVIDENCE_CONTRACT_SCHEMA_V2.json"
PROPOSAL_SCHEMA_PATH = ROOT / "EC_FIELD_SECURITY_PROPOSAL_SCHEMA_V2.json"
CATALOG_PATH = ROOT / "security_knowledge" / "SECURITY_PRIMITIVE_CATALOG_V1.json"
MODEL_IR_SCHEMA_PATH = ROOT / "EC_FIELD_SECURITY_MODEL_IR_SCHEMA_V2.json"

POLICY_VERSION = "EC-FIELD-SECURITY-V2"
CONTRACT_VERSION = "EC-EVIDENCE-CONTRACT-V2"
PROPOSAL_VERSION = "EC-FIELD-PROPOSAL-V2"
MISSING = object()

EMAIL_BASIC = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
E164 = re.compile(r"^\+[1-9][0-9]{7,14}$")


class PolicyError(ValueError):
    """Malformed policy, contract, proposal, or unsupported operation."""


def _load_json(path: Path) -> Any:
    def reject_constant(value: str) -> None:
        raise PolicyError(f"non-standard numeric constant is forbidden: {value}")

    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)


def _schema(path: Path) -> dict[str, Any]:
    value = _load_json(path)
    Draft202012Validator.check_schema(value)
    return value


POLICY_SCHEMA = _schema(POLICY_SCHEMA_PATH)
CONTRACT_SCHEMA = _schema(CONTRACT_SCHEMA_PATH)
PROPOSAL_SCHEMA = _schema(PROPOSAL_SCHEMA_PATH)
CATALOG = _load_json(CATALOG_PATH)
MODEL_IR_SCHEMA = _schema(MODEL_IR_SCHEMA_PATH)


def _format_errors(validator: Draft202012Validator, value: Any) -> str:
    errors = sorted(validator.iter_errors(value), key=lambda e: (list(e.absolute_path), e.message))
    if not errors:
        return ""
    rendered = []
    for err in errors[:8]:
        location = "/" + "/".join(str(x) for x in err.absolute_path)
        rendered.append(f"{location}: {err.message}")
    if len(errors) > 8:
        rendered.append(f"... {len(errors) - 8} more schema errors")
    return "; ".join(rendered)


POLICY_VALIDATOR = Draft202012Validator(POLICY_SCHEMA)
CONTRACT_VALIDATOR = Draft202012Validator(CONTRACT_SCHEMA)
PROPOSAL_SHAPE_SCHEMA = copy.deepcopy(PROPOSAL_SCHEMA)
PROPOSAL_SHAPE_SCHEMA["oneOf"][0]["properties"]["policy"] = {"type": "object"}
PROPOSAL_VALIDATOR = Draft202012Validator(PROPOSAL_SHAPE_SCHEMA)
MODEL_IR_VALIDATOR = Draft202012Validator(MODEL_IR_SCHEMA)


def _reject_nonfinite(value: Any, location: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise PolicyError(f"non-finite number at {location}")
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_nonfinite(item, f"{location}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_nonfinite(item, f"{location}[{index}]")


def _decode_pointer_token(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def _resolve(root: dict[str, Any], pointer: str) -> list[Any]:
    """Resolve a restricted JSON Pointer with '*' list/object wildcard."""
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise PolicyError(f"invalid JSON pointer: {pointer!r}")
    tokens = [_decode_pointer_token(token) for token in pointer[1:].split("/")]
    if not tokens or tokens[0] not in {"request", "trusted"}:
        raise PolicyError(f"pointer must start with /request or /trusted: {pointer}")
    current: list[Any] = [root]
    for token in tokens:
        nxt: list[Any] = []
        for value in current:
            if token == "*":
                if isinstance(value, dict):
                    nxt.extend(value.values())
                elif isinstance(value, list):
                    nxt.extend(value)
                continue
            if isinstance(value, dict) and token in value:
                nxt.append(value[token])
            elif isinstance(value, list) and token.isdigit() and int(token) < len(value):
                nxt.append(value[int(token)])
        current = nxt
        if not current:
            return []
    return current


def _rule_paths(rule: dict[str, Any]) -> set[str]:
    return {
        value
        for key, value in rule.items()
        if (key == "path" or key.endswith("_path")) and isinstance(value, str)
    }


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and not (
        isinstance(value, float) and not math.isfinite(value)
    )


def _is_strict_type(value: Any, expected: str) -> bool:
    checks: dict[str, Callable[[Any], bool]] = {
        "object": lambda x: isinstance(x, dict),
        "array": lambda x: isinstance(x, list),
        "string": lambda x: isinstance(x, str),
        "boolean": lambda x: isinstance(x, bool),
        "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
        "number": _is_number,
        "null": lambda x: x is None,
    }
    if expected not in checks:
        raise PolicyError(f"unsupported strict type: {expected}")
    return checks[expected](value)


def _email_basic(value: Any) -> bool:
    return isinstance(value, str) and len(value) <= 254 and bool(EMAIL_BASIC.fullmatch(value))


def _e164_phone(value: Any) -> bool:
    """Structural E.164 check only; it does not claim allocation or reachability."""
    return isinstance(value, str) and bool(E164.fullmatch(value))


def _iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _cn_resident_id(value: Any) -> bool:
    """Public 18-character checksum and embedded birth-date validation only."""
    if not isinstance(value, str) or not re.fullmatch(r"[1-9][0-9]{16}[0-9Xx]", value):
        return False
    try:
        dt.date.fromisoformat(f"{value[6:10]}-{value[10:12]}-{value[12:14]}")
    except ValueError:
        return False
    weights = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    checks = "10X98765432"
    expected = checks[sum(int(n) * w for n, w in zip(value[:17], weights)) % 11]
    return value[-1].upper() == expected


VALIDATORS: dict[str, Callable[[Any], bool]] = {
    "email_basic_v1": _email_basic,
    "e164_phone_v1": _e164_phone,
    "cn_resident_id_v1": _cn_resident_id,
    "iso_date_v1": _iso_date,
}

VALIDATOR_CONTEXT_REQUIREMENTS: dict[str, dict[str, Any]] = {
    "email_basic_v1": {"visible_format_identity": "email"},
    "e164_phone_v1": {"visible_format_identity": "phone", "phone_format": "E.164"},
    "cn_resident_id_v1": {
        "visible_format_identity": "identity_document",
        "jurisdiction": "CN",
        "identifier_type": "resident_identity_number",
    },
    "iso_date_v1": {"visible_format_identity": "date", "date_format": "ISO-8601-date"},
}

PRIMITIVE_TO_OPS: dict[str, set[str]] = {
    "SP-CONTENT-TYPE-ALLOWLIST": {"content_type_allowlist"},
    "SP-REQUEST-SIZE-LIMIT": {"request_size_limit"},
    "SP-OBJECT-PROPERTY-ALLOWLIST": {"allowed_fields"},
    "SP-PRESENCE-NULLABILITY": {"required"},
    "SP-STRICT-TYPE": {"strict_type"},
    "SP-LENGTH-CARDINALITY-BOUNDS": {"length_cardinality"},
    "SP-NUMERIC-RANGE-PRECISION": {"number_range_precision"},
    "SP-ENUM-ALLOWLIST": {"enum_allowlist"},
    "SP-STRUCTURED-FORMAT": {"named_validator"},
    "SP-CANONICAL-FORM": {"canonical_form"},
    "SP-CROSS-FIELD-INVARIANT": {"date_order", "age_matches_dob"},
    "SP-SERVER-AUTHORITY-WORKFLOW": {"state_transition", "server_derived_reject"},
}

CATALOG_REQUIREMENTS: dict[str, set[str]] = {
    item["primitive_id"]: set(item["required_binding_evidence"])
    for item in CATALOG["primitives"]
}


def validate_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    _reject_nonfinite(proposal)
    errors = _format_errors(PROPOSAL_VALIDATOR, proposal)
    if errors:
        raise PolicyError(f"proposal schema rejected: {errors}")
    if proposal["decision"] == "propose":
        _validate_policy_shape(proposal["policy"])
    return proposal


def _validate_policy_shape(policy: dict[str, Any]) -> None:
    _reject_nonfinite(policy)
    errors = _format_errors(POLICY_VALIDATOR, policy)
    if errors:
        raise PolicyError(f"policy schema rejected: {errors}")
    rule_ids = [rule["rule_id"] for rule in policy["rules"]]
    if len(rule_ids) != len(set(rule_ids)):
        raise PolicyError("duplicate rule_id")
    for rule in policy["rules"]:
        if rule["primitive_id"] not in PRIMITIVE_TO_OPS:
            raise PolicyError(f"unknown primitive_id: {rule['primitive_id']}")
        if rule["op"] not in PRIMITIVE_TO_OPS[rule["primitive_id"]]:
            raise PolicyError(
                f"operation {rule['op']} is not admitted for primitive {rule['primitive_id']}"
            )
        if not set(rule["evidence_refs"]).issubset(set(policy["evidence_refs"])):
            raise PolicyError(f"rule {rule['rule_id']} references evidence outside policy.evidence_refs")
        if rule["op"] == "length_cardinality" and rule["max"] < rule["min"]:
            raise PolicyError(f"invalid length/cardinality bounds in {rule['rule_id']}")
        if rule["op"] == "number_range_precision":
            if "min" in rule and "max" in rule and rule["max"] < rule["min"]:
                raise PolicyError(f"invalid numeric bounds in {rule['rule_id']}")


def _validate_contract_shape(contract: dict[str, Any]) -> None:
    _reject_nonfinite(contract)
    errors = _format_errors(CONTRACT_VALIDATOR, contract)
    if errors:
        raise PolicyError(f"evidence contract schema rejected: {errors}")
    ids = [item["evidence_id"] for item in contract["evidence"]]
    if len(ids) != len(set(ids)):
        raise PolicyError("duplicate evidence_id")


def compile_policy(policy: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    """Admit a policy only when rule semantics are bound to visible evidence."""
    _validate_policy_shape(policy)
    _validate_contract_shape(contract)
    if policy["policy_version"] != POLICY_VERSION or contract["contract_version"] != CONTRACT_VERSION:
        raise PolicyError("unsupported protocol version")
    if policy["target"] != contract["target"]:
        raise PolicyError("policy target does not match evidence contract target")

    evidence_by_id = {item["evidence_id"]: item for item in contract["evidence"]}
    if not set(policy["evidence_refs"]).issubset(evidence_by_id):
        raise PolicyError("policy references evidence absent from the contract")

    target = policy["target"]
    for rule in policy["rules"]:
        items = [evidence_by_id[eid] for eid in rule["evidence_refs"]]
        if any(item["visibility"] != "visible" for item in items):
            raise PolicyError(f"rule {rule['rule_id']} references non-visible evidence")
        if any(item["relation"] != "supports" for item in items):
            raise PolicyError(f"rule {rule['rule_id']} has contradictory or insufficient evidence")
        if any(item["system"] not in {target["system"], "EC-GLOBAL"} for item in items):
            raise PolicyError(f"rule {rule['rule_id']} evidence system mismatch")
        if any(target["version"] not in item["versions"] and "*" not in item["versions"] for item in items):
            raise PolicyError(f"rule {rule['rule_id']} evidence version mismatch")
        if any(target["operation"] not in item["operations"] and "*" not in item["operations"] for item in items):
            raise PolicyError(f"rule {rule['rule_id']} evidence operation mismatch")
        if any(rule["primitive_id"] not in item["supports_primitives"] for item in items):
            raise PolicyError(f"rule {rule['rule_id']} evidence does not support its primitive")

        bound_paths = set().union(*(set(item["bound_paths"]) for item in items))
        missing_paths = _rule_paths(rule) - bound_paths
        if missing_paths:
            raise PolicyError(f"rule {rule['rule_id']} has unbound paths: {sorted(missing_paths)}")

        facts: dict[str, Any] = {}
        for item in items:
            for key, value in item["binding_facts"].items():
                if key in facts and facts[key] != value:
                    raise PolicyError(f"rule {rule['rule_id']} has conflicting binding fact: {key}")
                facts[key] = value
        missing_facts = CATALOG_REQUIREMENTS[rule["primitive_id"]] - set(facts)
        if missing_facts:
            raise PolicyError(f"rule {rule['rule_id']} lacks binding facts: {sorted(missing_facts)}")
        if rule["op"] == "named_validator":
            required_context = VALIDATOR_CONTEXT_REQUIREMENTS[rule["validator_id"]]
            mismatches = {
                key: expected
                for key, expected in required_context.items()
                if facts.get(key) != expected
            }
            if mismatches:
                raise PolicyError(
                    f"rule {rule['rule_id']} lacks validator context: {sorted(mismatches)}"
                )
    return policy


def compile_policy_shape_only(policy: dict[str, Any]) -> dict[str, Any]:
    """Compile the EC-P ablation without semantic evidence admission.

    This deliberately preserves schema, primitive registry, and runtime checks.
    Only Evidence Contract admission is removed, so EC-P and EC can consume the
    byte-identical Proposal candidate without changing the execution engine.
    """
    _validate_policy_shape(policy)
    if policy["policy_version"] != POLICY_VERSION:
        raise PolicyError("unsupported policy version")
    return policy


def compile_model_ir(model_ir: dict[str, Any]) -> dict[str, Any]:
    """Validate compact model output and deterministically compile Policy V2."""
    _reject_nonfinite(model_ir)
    errors = _format_errors(MODEL_IR_VALIDATOR, model_ir)
    if errors:
        raise PolicyError(f"model IR schema rejected: {errors}")
    decision = model_ir["decision"]
    if decision == "abstain":
        if model_ir["policy_id"] != "none" or model_ir["evidence_refs"] or model_ir["rules"]:
            raise PolicyError("abstain IR must use policy_id=none and empty evidence_refs/rules")
        if model_ir["reason_code"] == "none" or not model_ir["missing_evidence"]:
            raise PolicyError("abstain IR requires a reason code and missing evidence")
        return {
            "proposal_version": PROPOSAL_VERSION,
            "candidate_id": model_ir["candidate_id"],
            "decision": "abstain",
            "reason_code": model_ir["reason_code"],
            "missing_evidence": model_ir["missing_evidence"],
        }
    if model_ir["policy_id"] == "none" or not model_ir["evidence_refs"] or not model_ir["rules"]:
        raise PolicyError("propose IR requires policy_id, evidence_refs, and at least one rule")
    if model_ir["reason_code"] != "none" or model_ir["missing_evidence"]:
        raise PolicyError("propose IR must use reason_code=none and empty missing_evidence")
    rules = []
    for item in model_ir["rules"]:
        params = dict(item["params"])
        # These are runtime ABI defaults, not inferred business facts. They are
        # frozen before formal runs and applied byte-identically to every method.
        if item["op"] == "allowed_fields":
            params.setdefault("path", "/request/body")
        if item["op"] not in {"required", "server_derived_reject"}:
            params.setdefault("on_missing", "deny")
        rule = {
            "rule_id": item["rule_id"],
            "primitive_id": item["primitive_id"],
            "evidence_refs": item["evidence_refs"],
            "op": item["op"],
            **params,
        }
        rules.append(rule)
    policy = {
        "policy_version": POLICY_VERSION,
        "policy_id": model_ir["policy_id"],
        "target": model_ir["target"],
        "evidence_refs": model_ir["evidence_refs"],
        "rules": rules,
    }
    _validate_policy_shape(policy)
    return {
        "proposal_version": PROPOSAL_VERSION,
        "candidate_id": model_ir["candidate_id"],
        "decision": "propose",
        "policy": policy,
    }


def _violation(rule: dict[str, Any], code: str, detail: str) -> dict[str, str]:
    return {"rule_id": rule["rule_id"], "code": code, "detail": detail}


def _missing_result(rule: dict[str, Any], paths: Iterable[str]) -> dict[str, str] | None:
    if rule.get("on_missing") == "skip":
        return None
    return _violation(rule, "required_input_missing", ",".join(sorted(paths)))


def _evaluate_value_rule(rule: dict[str, Any], value: Any, path: str) -> dict[str, str] | None:
    op = rule["op"]
    if op == "content_type_allowlist":
        if not isinstance(value, str):
            return _violation(rule, "type_mismatch", path)
        media_type = value.split(";", 1)[0].strip().lower()
        allowed = {x.lower() for x in rule["media_types"]}
        return None if media_type in allowed else _violation(rule, "content_type_rejected", media_type)
    if op == "request_size_limit":
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            return _violation(rule, "invalid_request_size", path)
        return None if value <= rule["max_bytes"] else _violation(rule, "request_too_large", path)
    if op == "allowed_fields":
        if not isinstance(value, dict):
            return _violation(rule, "type_mismatch", path)
        extras = sorted(set(value) - set(rule["fields"]))
        return None if not extras else _violation(rule, "unexpected_fields", ",".join(extras))
    if op == "strict_type":
        return None if _is_strict_type(value, rule["expected_type"]) else _violation(rule, "type_mismatch", path)
    if op == "length_cardinality":
        if not isinstance(value, (str, list, dict)):
            return _violation(rule, "type_mismatch", path)
        return None if rule["min"] <= len(value) <= rule["max"] else _violation(rule, "length_out_of_range", path)
    if op == "number_range_precision":
        if not _is_number(value):
            return _violation(rule, "type_mismatch_or_nonfinite", path)
        if "min" in rule and value < rule["min"] or "max" in rule and value > rule["max"]:
            return _violation(rule, "number_out_of_range", path)
        if "max_scale" in rule:
            try:
                scale = max(0, -Decimal(str(value)).as_tuple().exponent)
            except InvalidOperation:
                return _violation(rule, "invalid_decimal", path)
            if scale > rule["max_scale"]:
                return _violation(rule, "decimal_scale_exceeded", path)
        return None
    if op == "enum_allowlist":
        return None if value in rule["values"] else _violation(rule, "enum_mismatch", path)
    if op == "named_validator":
        return None if VALIDATORS[rule["validator_id"]](value) else _violation(rule, "validator_rejected", rule["validator_id"])
    if op == "canonical_form":
        if not isinstance(value, str):
            return _violation(rule, "type_mismatch", path)
        canonical = unicodedata.normalize(rule["unicode_form"], value)
        if rule["strip_whitespace"]:
            canonical = canonical.strip()
        return None if canonical == value else _violation(rule, "noncanonical_value", path)
    raise PolicyError(f"unsupported value operation: {op}")


def _single(rule: dict[str, Any], envelope: dict[str, Any], key: str) -> Any:
    values = _resolve(envelope, rule[key])
    if len(values) == 1:
        return values[0]
    if not values:
        return MISSING
    raise PolicyError(f"{rule['rule_id']} requires a single value at {rule[key]}")


def _evaluate_rule(rule: dict[str, Any], envelope: dict[str, Any]) -> list[dict[str, str]]:
    op = rule["op"]
    if op == "required":
        values = _resolve(envelope, rule["path"])
        if not values:
            return [_violation(rule, "required_missing", rule["path"])]
        if not rule["allow_null"] and any(value is None for value in values):
            return [_violation(rule, "null_not_allowed", rule["path"])]
        return []
    if op == "server_derived_reject":
        return [] if not _resolve(envelope, rule["path"]) else [_violation(rule, "client_supplied_server_value", rule["path"])]
    if op in {
        "content_type_allowlist", "request_size_limit", "allowed_fields", "strict_type",
        "length_cardinality", "number_range_precision", "enum_allowlist", "named_validator",
        "canonical_form",
    }:
        values = _resolve(envelope, rule["path"])
        if not values:
            missing = _missing_result(rule, [rule["path"]])
            return [missing] if missing else []
        return [result for value in values if (result := _evaluate_value_rule(rule, value, rule["path"]))]
    if op == "date_order":
        earlier = _single(rule, envelope, "earlier_path")
        later = _single(rule, envelope, "later_path")
        if MISSING in (earlier, later):
            missing = _missing_result(rule, [rule["earlier_path"], rule["later_path"]])
            return [missing] if missing else []
        try:
            a, b = dt.date.fromisoformat(earlier), dt.date.fromisoformat(later)
        except (TypeError, ValueError):
            return [_violation(rule, "invalid_date", rule["rule_id"])]
        ok = a <= b if rule["allow_equal"] else a < b
        return [] if ok else [_violation(rule, "date_order_violation", rule["rule_id"])]
    if op == "age_matches_dob":
        age = _single(rule, envelope, "age_path")
        dob = _single(rule, envelope, "dob_path")
        as_of = _single(rule, envelope, "as_of_path")
        if any(value is MISSING for value in (age, dob, as_of)):
            missing = _missing_result(rule, [rule["age_path"], rule["dob_path"], rule["as_of_path"]])
            return [missing] if missing else []
        try:
            born, now = dt.date.fromisoformat(dob), dt.date.fromisoformat(as_of)
            expected = now.year - born.year - ((now.month, now.day) < (born.month, born.day))
        except (TypeError, ValueError):
            return [_violation(rule, "invalid_age_inputs", rule["rule_id"])]
        if not isinstance(age, int) or isinstance(age, bool):
            return [_violation(rule, "invalid_age_inputs", rule["rule_id"])]
        return [] if abs(age - expected) <= rule["tolerance_years"] else [_violation(rule, "age_dob_mismatch", rule["rule_id"])]
    if op == "state_transition":
        current = _single(rule, envelope, "current_state_path")
        requested = _single(rule, envelope, "requested_state_path")
        if MISSING in (current, requested):
            missing = _missing_result(rule, [rule["current_state_path"], rule["requested_state_path"]])
            return [missing] if missing else []
        transitions = {(item["from"], item["to"]) for item in rule["transitions"]}
        return [] if (current, requested) in transitions else [_violation(rule, "invalid_state_transition", f"{current}->{requested}")]
    raise PolicyError(f"unsupported operation: {op}")


def evaluate(
    policy: dict[str, Any],
    contract: dict[str, Any] | None,
    envelope: dict[str, Any],
    admission_mode: str = "semantic",
) -> dict[str, Any]:
    """Evaluate one request. Any engine or admission error denies the request."""
    policy_id = policy.get("policy_id") if isinstance(policy, dict) else None
    try:
        _reject_nonfinite(envelope)
        if admission_mode == "semantic":
            if contract is None:
                raise PolicyError("semantic admission requires an evidence contract")
            compiled = compile_policy(policy, contract)
        elif admission_mode == "shape_only":
            compiled = compile_policy_shape_only(policy)
        else:
            raise PolicyError(f"unsupported admission mode: {admission_mode}")
        violations = [violation for rule in compiled["rules"] for violation in _evaluate_rule(rule, envelope)]
        return {
            "policy_id": compiled["policy_id"],
            "decision": "deny" if violations else "allow",
            "fail_closed": True,
            "violations": violations,
        }
    except (KeyError, PolicyError, TypeError, ValueError) as exc:
        return {
            "policy_id": policy_id,
            "decision": "deny",
            "fail_closed": True,
            "engine_error": str(exc),
            "violations": [],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--request", required=True, type=Path)
    args = parser.parse_args()
    proposal = validate_proposal(_load_json(args.proposal))
    if proposal["decision"] == "abstain":
        print(json.dumps(proposal, ensure_ascii=False, sort_keys=True))
        return 0
    result = evaluate(
        proposal["policy"],
        _load_json(args.contract),
        _load_json(args.request),
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
