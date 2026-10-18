# B19：固定版本源码路径与已有分支覆盖

日期：2026-10-15。仅本地只读核查；新增模型调用、网络请求、政策执行、源码函数执行均为 0。原始材料与旧实验分类保持不变。

## 结论

已找到 ERPNext 16.0.0 与 Frappe 16.1.1 的本地源码。Supplier 正常保存时，`on_hold=true` 且空 `hold_type` 会在写入数据库前变为 `All`。Purchase Order 校验读取供应商已存状态，按 `All/Invoices` 阻止交易，且还检查 `release_date`。因此，原来的“held=true、type为空”网关探针不能直接解释为正常保存后的生产业务状态，更不能据此声称生产漏洞。

现有 B13/B17/B19 分支已能展示各自主逻辑，无需重复已有测试。B13 若要求 `< / = / > × role` 六组合全覆盖，还差“低于上限且有授权”“等于上限且有授权”两项。B19 的完整生产冻结生命周期仍缺到期日期与适配器映射证据；当前 ABI 没有 release_date，不能靠补同一子规则的请求声称闭合。

## 1. 版本身份和可见性

源码根目录：`D:\lunwen\ec\runtime\erpnext_qualification\erpnext-v16.0.0\erpnext-16.0.0`；`erpnext/__init__.py:9` 声明 16.0.0。关键源码逐字节哈希与本地 `erpnext-v16.0.0.zip` 中对应 entry 一致。另一个 `erpnext-v16.0.0-full` 副本采用 CRLF，原字节不同；四个已检查目标文件统一换行后与归档内容相同，本报告以原始解压副本为准。

Frappe 根目录：`D:\lunwen\ec\runtime\erpnext_qualification\frappe-v16.1.1\frappe-16.1.1`；`frappe/__init__.py:57` 声明 16.1.1，document.py 与本地 `frappe-v16.1.1.zip` entry 一致。历史 `bench_version.txt` 另记录 ERPNext 16.0.0 / Frappe 16.1.1，但它属于历史其他实验，不能冒充本轮生产环境验证。此处没有取得可独立核验的上游 Git commit，版本身份限于本地固定归档、版本声明、entry 对账与历史环境记录。

生成时可见：共同输入 packet 的 Supplier 文档快照、Supplier/Purchase Order 字段目录、REST Create 文档和运行时 ABI。原 `SOURCE_MANIFEST.json` 明确动态网页不是 v16.0.0 tag 文档。运行时字段 JSON 标为 exact_runtime_image_source。

本轮后见：supplier.py、controllers 源码、Frappe document.py 和上游测试源码。它们用于解释路径，未回填给历史模型，不能把新增源码信息记成模型当时已提取的证据。

## 2. 空类型在哪一步变成 All

`erpnext/buying/doctype/supplier/supplier.py:88` 的完整函数：

```python
def before_save(self):
    if not self.on_hold:
        self.hold_type = ""
        self.release_date = ""
    elif self.on_hold and not self.hold_type:
        self.hold_type = "All"
```

Frappe `frappe/model/document.py:1312` 的 `run_before_save_methods` 在 `_action == "save"` 时依次调用 validate、before_save（1331–1333）。`_save` 在 554 调它，在 568 才 db_update；`insert` 在 447 调它，在 458 才 db_insert。这是正常文档保存路径的静态证明。`ignore_validate` 在 1328–1329 可提前返回；不能由正常路径结论排除绕过 hooks、直接数据库写入、缓存与竞态等其他路径，它们未在本轮验证。

Supplier 保存和 Purchase Order 保存是两个文档事件。静态链条是“保存 Supplier 时先规范化；之后 Purchase Order 读取已存 Supplier”。未观察本轮真实事件时间、事务、缓存或网络转发。

## 3. Purchase Order 实际检查什么

`erpnext/controllers/accounts_controller.py:157` 的完整目标函数：

```python
def ensure_supplier_is_not_blocked(self):
    is_supplier_payment = self.doctype == "Payment Entry" and self.party_type == "Supplier"
    is_buying_invoice = self.doctype in ["Purchase Invoice", "Purchase Order"]
    supplier_name = self.supplier if is_buying_invoice else self.party if is_supplier_payment else None
    supplier = None
    if supplier_name:
        supplier = frappe.get_lazy_doc("Supplier", supplier_name)
    if supplier and supplier.on_hold:
        if (is_buying_invoice and supplier.hold_type in ["All", "Invoices"]) or (
            is_supplier_payment and supplier.hold_type in ["All", "Payments"]
        ):
            if not supplier.release_date or getdate(nowdate()) <= supplier.release_date:
                frappe.msgprint(
                    _("{0} is blocked so this transaction cannot proceed").format(supplier_name),
                    raise_exception=1,
                )
```

调用链：

`PurchaseOrder.validate:193–194` → `BuyingController.validate:33–36` → `SubcontractingController.validate:67–77` → `StockController.validate:57–58` → `AccountsController.validate:218/235` → `ensure_supplier_is_not_blocked:157–174`。

`PurchaseOrder.validate_supplier:275` 检查的是 Supplier Scorecard 的 prevent_pos/warn_pos，并非本例 hold_type 检查。不能因同名 validate_supplier 误连调用链。

上游测试源码 `test_purchase_order.py:628–637` 先将 on_hold 设为 1 并 supplier.save，断言 hold_type 为 All，再期望 create_purchase_order 抛错；639–667 另覆盖 Invoices/Payments。这里只阅读测试源码，未运行测试，不能写成测试通过。

对隔离函数验证而言：before_save 只有属性读写，可用最小对象执行；ensure 函数需 stub `frappe.get_lazy_doc/msgprint`、`_`、`getdate/nowdate` 及 self 字段。若根任务执行这种验证，只能称实际函数的隔离逻辑检查，不能称完整 Frappe 或生产路径验证。本核查未执行它们。

## 4. 对 B19 网关结果的重新定位

| 层次 | 已确认 | 仍未闭合 |
|---|---|---|
| 文档 | 未选类型默认 All | 动态快照与固定源码版本对应关系不能由网页名保证 |
| 固定源码正常保存路径 | before_save 将 held+empty 设 All；未冻结会清空类型/日期 | 特殊写入、hook 跳过、缓存、并发等非正常路径 |
| 当前网关 ABI | 只有 supplierOnHold(boolean)、holdType(string)，无规范化保证、无 release_date；trusted 原样保持 | supplierOnHold 是数据库原 on_hold 还是已合成有效期后的状态；状态认证、新鲜度、生产可达性 |
| 归档网关执行 | held+empty 时 ECAS deny，两同行 allow | 该输入是否能出现在真实适配器输出；ECAS 是否显式提取默认值（候选没有该显式规则） |

所以空值控制是“未规范化输入下、与默认 All 结果一致”的事后线索，旧 conservative_empty_type_control 分类保持不变。已规范化的四种状态下，三方法的类型子规则一致：未冻结允许；冻结 All/Invoices 拒绝；冻结 Payments 允许。

额外发现：源码仅在“无 release_date 或 today≤release_date”时阻止；当前政策没有日期。若 supplierOnHold 是原字段而不是有效期合成状态，release_date 已过时网关可能过度拒绝 All/Invoices。当前材料不足以判定是哪一种，须记为适配器映射缺口，不能直接记为已观察 ECAS 错误，也不能声称完整生产语义复现。

## 5. 已有分支是否足够

仅检查既有 `matched_generation/method_runs/<case>/<method>/RESULT.json` 和 sealed branch_protocol，不新增执行。三方法输入逐项相同，JSON 保存每项归档路径/hash、输入和观察。

| 案例 | 已有主逻辑覆盖 | 具体缺口 | 建议 |
|---|---|---|---|
| B13 | role=false 时 qty 为109、110、111（max110）；role=true 时111及1000；已有 body 假角色/假上限和缺 trusted 控制 | 六组合域中 `<max & true`、`=max & true` 未执行；上限推导与角色认证不在此子规则内 | 主逻辑展示已足够；仅在要声称六组合完备时补两项 |
| B17 | customerDisabled false/true 两态均有；另有 body 假状态、缺 trusted | 聚焦 boolean 子规则无主逻辑组合缺口；上游身份/状态可靠性未验证 | 不重复测试 |
| B19 | 正常 before_save 后的四组合 false+空、true+All、true+Invoices、true+Payments 均有；另有空/未知类型、伪造 body、缺 trusted 控制 | 当前类型子规则无规范化域缺口；完整源码还需无日期/今天/将来/过去日期分支，ABI未提供日期；false+非空类型属于未规范化状态，不能冒充正常状态新案例 | 不重跑已有四态；先厘清适配器有效期含义，才考虑扩大范围 |

## 证据入口

同目录 `B19_SOURCE_PATH.json` 提供实际绝对路径、SHA256、行范围、最小完整函数体、归档 entry 对账、生成可见/后见分类、已有分支及缺项。它是本次只读核查派生结果，不替代原始源文件与实验账本。
