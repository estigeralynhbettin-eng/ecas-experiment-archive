# 七案例：来源→受限IR→证据准入→离线执行

本表逐案绑定来源、候选、Inventory、注册路径和归档请求结果；全部曾准入且归档原请求对为allow/deny。这是既有输出链核对，不能据此宣称全部来源语义或生产行为正确。

| 案例 | 所属项目 | 来源到IR的映射 | 当前证据定位 |
|---|---|---|---|
| B06 撤销条件 | Apache Fineract | bounded_guard_dnf：reAgeIsLatestTransaction=true | 历史抽取/布尔判定演示；专用undoReAge与旧通用undo目标不一致，映射未闭合 |
| S02 字段白名单 | Apache Fineract | allowed_fields：四字段闭集 | 历史网关策略约定；静态HTTP链先DTO绑定、关闭未知键报错，拒绝未知键未证成 |
| S04 邮箱格式 | ERPNext | named_validator：email_basic_v1 | 可展示Email属性到注册基本格式原语的映射；未证明与后端全部邮箱规范等价 |
| S03 整数类型 | Apache Fineract | strict_type(integer)，on_missing=skip | 支持指定类型子约束的来源到IR及离线执行链 |
| B13 上限与授权例外 | ERPNext | bounded_guard_dnf：qty≤max，或超限且authorizedRole | 支持指定数量子约束；上限计算、角色认证与真实状态获取由公共ABI提供，未单独验证 |
| B17 禁用客户 | ERPNext | bounded_guard_dnf：customerDisabled=false | 支持已知布尔状态下的方向映射；状态认证及生产转发未验证 |
| B19 冻结类型 | ERPNext | bounded_guard_dnf：supplierOnHold=false OR holdType=Payments | 支持冻结类型子规则；原ABI未声明规范化和有效期语义，完整冻结生命周期未闭合 |

B06、S02保留历史演示身份，不纳入来源/API语义充分闭合的主证据；B19保留类型子规则身份。所有案例仍假定公共ABI提供真实且适当的上下文，本轮没有证明认证、新鲜度、生产HTTP转发或全业务规则覆盖。

[逐字段证据链JSON](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/SEVEN_CASE_CHAIN.json)；[链条CSV](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/SEVEN_CASE_CHAIN.csv)
