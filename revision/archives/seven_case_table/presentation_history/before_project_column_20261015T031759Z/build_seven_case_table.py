"""Build an evidence-linked descriptive table without running methods or APIs."""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OLD = ROOT / "working/exploration/20261014_external_baseline_pilot"
NEW = ROOT / "working/exploration/20261014_matched_evidence_labor/matched_generation"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def native(value):
    if not value:
        return None
    value = str(value)
    if value.startswith("/mnt/d/"):
        value = "D:/" + value[len("/mnt/d/"):]
    return Path(value)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source(path):
    p = native(path)
    assert p and p.is_file(), str(p)
    return {"path": str(p), "sha256": sha(p)}


old_summary_path = OLD / "binding_replay_resource_object/SUMMARY.json"
new_summary_path = NEW / "results_review_v1/COMPARISON_SUMMARY.json"
old_summary = load(old_summary_path)
new_summary = load(new_summary_path)
old_ledger = {x["index"]: x for x in load(OLD / "CALL_LEDGER.json")}
new_ledger = {x["index"]: x for x in load(NEW / "CALL_LEDGER.json")}
pre_format = {(x["task"], x["method"]): x for x in load(OLD / "PRE_FORMAT_EXECUTION_STATE.json")["rows"]}
checks = []
rows = []
provenance = []
labels = {
    "FSV-B06": "撤销条件", "FSV-S02": "字段白名单", "FSV-S04": "邮箱格式",
    "FSV-S03": "年龄字段类型", "FSV-B13": "数量上限与授权例外",
    "FSV-B17": "禁用客户", "FSV-B19": "供应商冻结类型",
}
methods = {"ECAS_MATCHED": "ECAS", "P2P_STYLE": "P2P适配版", "AUTOPAC_STYLE": "AutoPAC适配版"}


def symbol(pair):
    if not pair:
        return "—", None
    assert len(pair) == 2
    correct = sum(x["actual"]["decision"] == x["expected"] for x in pair)
    return {0: "○", 1: "◐", 2: "●"}[correct], correct


def captures(call_indices, ledger):
    found = []
    for ix in call_indices:
        call = ledger[ix]
        recovered = call.get("local_recovery_status") == "RECOVERED_LOCAL_STATUS_ALIAS"
        assert call["status"] == "COMPLETED" or recovered
        raw = source(call["raw_response_path"])
        assert raw["sha256"] == call["raw_response_sha256"]
        prompt = source(call["prompt_path"])
        assert prompt["sha256"] == call["prompt_sha256"]
        output = source(call["recovered_output_path"] if recovered else call["output_path"])
        expected_output_sha = call.get("recovered_output_sha256") if recovered else call.get("output_sha256")
        if expected_output_sha:
            assert output["sha256"] == expected_output_sha
        capture = {"index": ix, "stage": call["stage"], "original_ledger_status": call["status"], "raw": raw, "prompt": prompt, "parsed_output": output}
        if recovered:
            capture["local_recovery_receipt"] = source(native(call["recovered_output_path"]).parent / "LOCAL_RECOVERY_RECEIPT.json")
        found.append(capture)
        checks.append({"kind": "capture_identity", "index": ix, "scope": str(native(call["prompt_path"]).parents[2]), "pass": True})
    return found


for batch, summary in (("A", old_summary), ("B", new_summary)):
    for item in summary["rows"]:
        task, method = item["task"], item["method"]
        legacy = batch == "A"
        result_path = OLD / "effect_runs" / task / method / "RESULT.json" if legacy else native(item["source_result"])
        result = load(result_path)
        assert result["task"] == task and result["method"] == method
        pair = item["requests"] if legacy else item["final_original_pair"]
        if not legacy:
            assert result["final_evaluation"]["requests"] == pair
            assert result["status"] == item["status"]
        sym, count = symbol(pair)
        if not legacy:
            assert sym == item["final_symbol"]
        else:
            if pair:
                assert item["request_pair_correct"] == (count == 2)
        original_status = pre_format[(task, method)]["status"] if legacy else result["status"]
        if legacy and method == "ECAS_MATCHED":
            policy_path = OLD / "effect_runs" / task / method / "admitted_policy.json"
        elif legacy:
            policy_path = native(item.get("checks", {}).get("policy_path") or result.get("developer_checks", {}).get("policy_path"))
        else:
            policy_path = native(result.get("final_checks", {}).get("policy_path"))
        policy_ref = source(policy_path) if policy_path else None
        if not legacy and pair:
            assert result["execution_eligible"] is True
            assert sha(policy_path) == result["final_evaluation"]["policy_sha256"]
            frozen = load(result_path.parent / "FINAL_POLICY_FREEZE.json")
            assert frozen["sha256"] == sha(policy_path)
        if legacy and method == "ECAS_MATCHED":
            assert item["original_policy_sha256"] == sha(policy_path)
        if legacy and item.get("format_receipt"):
            assert item["format_receipt"]["ast_equal_without_locations"] is True
            assert item["format_receipt"]["formatted_sha256"] == sha(policy_path)
        calls = item["model_calls"] if legacy else item["call_indices"]
        assert result["calls"] == calls
        caps = captures(calls, old_ledger if legacy else new_ledger)
        note = ""
        if item["status"] == "OUT_OF_SCOPE":
            note = "检测阶段声明范围外，未执行"
        elif item["status"] == "DEVELOPMENT_REJECTED":
            note = "开发阶段编译失败，未获执行资格"
        elif task == "FSV-S04" and method == "P2P_STYLE":
            note = "事后复演允许合法邮箱，也允许错误邮箱；遗漏格式约束"
        elif legacy and original_status == "DEVELOPMENT_REJECTED":
            note = "原流程开发未通过；OPA格式/接口映射恢复后事后复演"
        elif legacy:
            note = "旧批次原请求对；表中沿用事后统一接口复演"
        else:
            note = "共同目标协议下首次生成已合格"
        row = {
            "batch": batch, "task": task, "case_name_cn": labels[task],
            "system": "Fineract" if task in ("FSV-B06", "FSV-S02", "FSV-S03") else "ERPNext",
            "method": method, "method_name_cn": methods[method],
            "original_pre_format_status": original_status,
            "post_format_pre_mapping_status": result["status"] if legacy else "NOT_APPLICABLE",
            "displayed_status": item["status"], "displayed_symbol": sym,
            "original_legal_decision": pair[0]["actual"]["decision"] if pair else "NOT_EXECUTED",
            "original_violation_decision": pair[1]["actual"]["decision"] if pair else "NOT_EXECUTED",
            "pair_correct_count": count, "first_generation_eligible": item.get("initial_eligible") if not legacy else "NOT_COMPARABLE",
            "repaired_once": result.get("repaired_once", False),
            "result_source": str(result_path),
            "display_source": str(old_summary_path if legacy else new_summary_path),
            "final_policy_source": str(policy_path) if policy_path else "NONE",
            "raw_call_indices": ";".join(map(str, calls)), "note_cn": note,
        }
        rows.append(row)
        entry = {
            "task": task, "method": method, "batch": batch,
            "row": row, "result": source(result_path),
            "display_summary": source(old_summary_path if legacy else new_summary_path),
            "policy": policy_ref, "calls": caps,
            "original_pair": pair,
        }
        if legacy and item.get("format_receipt"):
            entry["post_hoc_format_receipt"] = item["format_receipt"]
            entry["pre_mapping_policy"] = source(item["format_receipt"]["source_path"])
        if legacy:
            entry["original_pre_format_state"] = source(OLD / "PRE_FORMAT_EXECUTION_STATE.json")
        else:
            entry["primary_reconciliation"] = source(NEW / "results_review_v1/PRIMARY_RECONCILIATION.json")
            entry["independent_reconciliation"] = source(NEW / "FINAL_INDEPENDENT_AUDIT.json")
        provenance.append(entry)
        checks.append({"kind": "row_and_policy_identity", "task": task, "method": method, "pass": True})

assert len(rows) == 21 and len({(x["task"], x["method"]) for x in rows}) == 21
with (HERE / "SEVEN_CASE_COMPARISON.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
sources = {
    "status": "SOURCE_RECONCILED_DESCRIPTIVE_TABLE_INDEPENDENT_REVIEW_PENDING",
    "created_date": "2026-10-15", "new_model_calls": 0, "new_method_executions": 0,
    "batch_A": "Archived original candidates; post-hoc interface mapping and OPA formatting recovery; original qualification failures retained.",
    "batch_B": "Common-target protocol; first/repaired qualification and sealed original-pair evaluation; different protocol from A.",
    "aggregation_prohibited": ["pooled_accuracy", "seven_case_single_protocol_claim", "independent_project_count", "native_baseline_performance"],
    "sources": provenance, "checks": checks, "passed_checks": len(checks),
}
(HERE / "TABLE_SOURCES.json").write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

order = ["FSV-B06", "FSV-S02", "FSV-S04", "FSV-S03", "FSV-B13", "FSV-B17", "FSV-B19"]
index = {(x["task"], x["method"]): x for x in rows}
lines = [
    "# 七案例原请求对总览", "", "日期：2026-10-15。只读取既有原响应、策略与执行记录；本表没有新增模型调用或方法执行。", "",
    "## 总表", "",
    "图例：● 原合法与违规请求均判对；◐ 仅一条判对；○ 两条均错；— 未执行。圆圈只描述每例原有两条请求，不表示整个系统正确率。", "",
    "| 批次 | 案例与目标 | ECAS | P2P适配版 | AutoPAC适配版 |",
    "|---|---|---|---|---|",
]
for task in order:
    base = index[(task, "ECAS_MATCHED")]
    cells = []
    for method in ("ECAS_MATCHED", "P2P_STYLE", "AUTOPAC_STYLE"):
        r = index[(task, method)]
        cell = r["displayed_symbol"]
        if r["displayed_status"] == "OUT_OF_SCOPE":
            cell += " 范围外"
        elif r["displayed_status"] == "DEVELOPMENT_REJECTED":
            cell += " 编译失败"
        elif task == "FSV-S04" and method == "P2P_STYLE":
            cell += " 错误邮箱也允许"
        cells.append(cell)
    lines.append("| " + " | ".join([base["batch"], f"{task.replace('FSV-', '')}：{labels[task]}", *cells]) + " |")
lines += [
    "", "## 两批来源必须分清", "",
    "- A批次：B06、S02、S04沿用旧模型候选，经事后接口映射与OPA格式恢复后的本地复演。本表保留原流程开发资格，不能把复演结果写成原流程端到端成功。",
    "- B批次：S03、B13、B17、B19采用共同目标、完整操作说明、限定一次修复及执行资格检查的新协议。B批次所有取得资格的方法均首次生成已合格；S03的AutoPAC首次及修复均编译失败。",
    "- 七例合在一张表方便查看，但不能计算合并准确率、声称同协议七例测试、或把七例当七个独立项目。它们均来自原Fineract和ERPNext两个项目、已暴露旧任务，每方法每例仅一轮。P2P与AutoPAC均为共同GLM的流程适配版，不能代表原作性能。",
    "", "## 原流程开发资格与事后恢复", "",
    "| A批次方法/案例 | 原始开发状态（格式恢复前） | 表中最终观察 |",
    "|---|---|---|",
]
for task in order[:3]:
    for method in ("ECAS_MATCHED", "P2P_STYLE", "AUTOPAC_STYLE"):
        r = index[(task, method)]
        lines.append(f"| {task.replace('FSV-', '')} / {methods[method]} | {r['original_pre_format_status']} | {r['displayed_symbol']}：{r['note_cn']} |")
lines += [
    "", "S04的P2P实际为allow/allow：合法邮箱判断正确，格式错误邮箱误放，所以填◐，不能泛称两条都判断错。S02的AutoPAC虽在修复中补出字段白名单，但调用不存在的is_integer，编译失败，填—；这不是一半请求判对。P2P的S02/S03判为范围外，同样填—。", "",
    "## 目标来源的解释边界", "",
    "- B06的原请求走通用undo接口，而来源约束是Re-Age最新交易才可撤销；结果限定于任务中提供的reAgeIsLatestTransaction可信标志，不能推出所有undo交易均适用该规则。",
    "- S02把所列字段作为封闭白名单是任务约定；列出API字段本身不自动证明生产API禁止所有额外字段。当前结果证明落实该约定，不能把值中的脚本串表述为已识别真实脚本攻击。",
    "- S04是本例email_basic_v1注册校验器的基本邮箱格式检查，不表示完整RFC邮箱验证。",
    "- 缺可信状态、空/未知冻结类型等工程控制应另表展示；它们不是新增独立案例，也没有验证可信状态认证、新鲜度或真实生产API转发。",
    "", "## 原始材料", "",
    "每个方法的raw响应、解析输出、最终策略与执行记录均列在TABLE_SOURCES.json，附SHA-256。SEVEN_CASE_COMPARISON.csv每行保留批次、资格状态、实际决策和来源。此表尚待独立复核后冻结。", "",
]
(HERE / "SEVEN_CASE_TABLE_CN.md").write_text("\n".join(lines), encoding="utf-8")
print(json.dumps({"rows": len(rows), "source_checks": len(checks), "output_dir": str(HERE)}, ensure_ascii=False))
