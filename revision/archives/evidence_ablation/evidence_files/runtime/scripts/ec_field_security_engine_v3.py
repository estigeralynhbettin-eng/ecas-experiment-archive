#!/usr/bin/env python3
"""Fail-closed EC field-security runtime V3.

V3 reuses the audited V2 primitives and adds one bounded, non-recursive DNF
guard.  The guard evaluates data only; it cannot execute model-authored code.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
_CORE_PATH = Path(__file__).with_name("ec_field_security_engine_v2.py")
_SPEC = importlib.util.spec_from_file_location("_ec_field_security_engine_v2_for_v3", _CORE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load isolated V2 engine core")
core = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = core
_SPEC.loader.exec_module(core)
PolicyError = core.PolicyError


def _load(name: str) -> dict[str, Any]:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


# Patch the V2 implementation's late-bound protocol globals.  Its functions
# resolve these names at call time, so the unchanged audited primitives remain
# byte-identical while V3 schemas and constants are enforced.
core.POLICY_SCHEMA = _load("EC_FIELD_SECURITY_POLICY_SCHEMA_V3.json")
core.CONTRACT_SCHEMA = _load("EC_EVIDENCE_CONTRACT_SCHEMA_V3.json")
core.PROPOSAL_SCHEMA = _load("EC_FIELD_SECURITY_PROPOSAL_SCHEMA_V3.json")
core.CATALOG = _load("security_knowledge/SECURITY_PRIMITIVE_CATALOG_V2.json")
core.MODEL_IR_SCHEMA = _load("EC_FIELD_SECURITY_MODEL_IR_SCHEMA_V3.json")
for schema in (
    core.POLICY_SCHEMA,
    core.CONTRACT_SCHEMA,
    core.PROPOSAL_SCHEMA,
    core.MODEL_IR_SCHEMA,
):
    Draft202012Validator.check_schema(schema)
core.POLICY_VALIDATOR = Draft202012Validator(core.POLICY_SCHEMA)
core.CONTRACT_VALIDATOR = Draft202012Validator(core.CONTRACT_SCHEMA)
core.PROPOSAL_SHAPE_SCHEMA = json.loads(json.dumps(core.PROPOSAL_SCHEMA))
core.PROPOSAL_SHAPE_SCHEMA["oneOf"][0]["properties"]["policy"] = {"type": "object"}
core.PROPOSAL_VALIDATOR = Draft202012Validator(core.PROPOSAL_SHAPE_SCHEMA)
core.MODEL_IR_VALIDATOR = Draft202012Validator(core.MODEL_IR_SCHEMA)
core.POLICY_VERSION = "EC-FIELD-SECURITY-V3"
core.CONTRACT_VERSION = "EC-EVIDENCE-CONTRACT-V3"
core.PROPOSAL_VERSION = "EC-FIELD-PROPOSAL-V3"
core.PRIMITIVE_TO_OPS["SP-BOUNDED-BUSINESS-GUARD"] = {"bounded_guard_dnf"}
core.CATALOG_REQUIREMENTS = {
    item["primitive_id"]: set(item["required_binding_evidence"])
    for item in core.CATALOG["primitives"]
}

_v2_rule_paths = core._rule_paths
_v2_evaluate_rule = core._evaluate_rule


def _rule_paths(rule: dict[str, Any]) -> set[str]:
    if rule.get("op") != "bounded_guard_dnf":
        return _v2_rule_paths(rule)
    paths: set[str] = set()
    for alternative in rule["alternatives"]:
        for clause in alternative["clauses"]:
            paths.add(clause["left_path"])
            if clause["right_source"] == "path":
                paths.add(clause["right_path"])
    return paths


def _single(pointer: str, envelope: dict[str, Any]) -> Any:
    values = core._resolve(envelope, pointer)
    if len(values) == 1:
        return values[0]
    if not values:
        return core.MISSING
    raise PolicyError(f"bounded guard requires one value at {pointer}")


def _ordered(left: Any, right: Any, operator: str) -> bool:
    if operator == "eq":
        return left == right and type(left) is type(right)
    if operator == "ne":
        return not (left == right and type(left) is type(right))
    if isinstance(left, bool) or isinstance(right, bool):
        raise PolicyError("ordered comparison does not accept booleans")
    if isinstance(left, dt.date) and isinstance(right, dt.date):
        pass
    elif not (
        isinstance(left, (int, float, str))
        and isinstance(right, (int, float, str))
        and type(left) is type(right)
    ):
        raise PolicyError("ordered comparison requires same-type scalar operands")
    if isinstance(left, float) and (not math.isfinite(left) or not math.isfinite(right)):
        raise PolicyError("non-finite bounded guard operand")
    return {
        "lt": left < right,
        "lte": left <= right,
        "gt": left > right,
        "gte": left >= right,
    }[operator]


def _clause_result(clause: dict[str, Any], envelope: dict[str, Any]) -> bool | None:
    left = _single(clause["left_path"], envelope)
    if clause["right_source"] == "path":
        if not clause["right_path"].startswith(("/request", "/trusted")):
            raise PolicyError("path operand requires a registered JSON pointer")
        if clause["right_value"] is not None:
            raise PolicyError("path operand requires right_value=null")
        right = _single(clause["right_path"], envelope)
    else:
        if clause["right_path"] != "":
            raise PolicyError("literal operand requires an empty right_path")
        right = clause["right_value"]
    if left is core.MISSING or right is core.MISSING:
        return None
    kind = clause["kind"]
    if kind == "date_compare":
        try:
            left = dt.date.fromisoformat(left)
            right = dt.date.fromisoformat(right)
        except (TypeError, ValueError):
            raise PolicyError("date_compare requires ISO-8601 date operands")
    elif kind == "cardinality_compare":
        if not isinstance(left, (str, list, dict)):
            raise PolicyError("cardinality_compare left operand is not countable")
        left = len(left)
        if not isinstance(right, int) or isinstance(right, bool):
            raise PolicyError("cardinality_compare right operand is not an integer")
    return _ordered(left, right, clause["operator"])


def _evaluate_rule(rule: dict[str, Any], envelope: dict[str, Any]) -> list[dict[str, str]]:
    if rule.get("op") != "bounded_guard_dnf":
        return _v2_evaluate_rule(rule, envelope)
    saw_missing = False
    for alternative in rule["alternatives"]:
        results = [_clause_result(clause, envelope) for clause in alternative["clauses"]]
        saw_missing = saw_missing or any(result is None for result in results)
        if all(result is True for result in results):
            return []
    if saw_missing and rule.get("on_missing") == "skip":
        return []
    code = "required_input_missing" if saw_missing else "bounded_guard_rejected"
    return [core._violation(rule, code, rule["rule_id"])]


core._rule_paths = _rule_paths
core._evaluate_rule = _evaluate_rule

validate_proposal = core.validate_proposal
compile_policy = core.compile_policy
compile_policy_shape_only = core.compile_policy_shape_only
compile_model_ir = core.compile_model_ir
evaluate = core.evaluate


if __name__ == "__main__":
    raise SystemExit(core.main())
