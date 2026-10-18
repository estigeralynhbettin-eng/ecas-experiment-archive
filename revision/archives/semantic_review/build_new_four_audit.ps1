$ErrorActionPreference = 'Stop'
$base = 'D:\lunwen\EC-CSI投稿\working\exploration\20261014_matched_evidence_labor\matched_generation'
$out = $PSScriptRoot
function Read-Json([string]$path) { Get-Content -LiteralPath $path -Raw -Encoding utf8 | ConvertFrom-Json }
function Evidence([string]$path) {
    [ordered]@{ path = $path; sha256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
}
$rows = @()
$sources = @()
foreach ($case in 'FSV-S03','FSV-B13','FSV-B17','FSV-B19') {
    $packetPath = Join-Path $base "generation_inputs\$case\packet.json"
    $packet = Read-Json $packetPath
    $sources += [ordered]@{
        case = $case; packet = Evidence $packetPath; target = $packet.target
        objective = $packet.TARGET_OBJECTIVE
        visible_sources = @($packet.visible_sources | ForEach-Object { [ordered]@{
            evidence_id = $_.evidence_id; source_id = $_.source_id; source_sha256 = $_.source_sha256; locator = $_.locator
        } })
    }
    foreach ($method in 'P2P_STYLE','AUTOPAC_STYLE','ECAS_MATCHED') {
        $methodDir = Join-Path $base "method_runs\$case\$method"
        $resultPath = Join-Path $methodDir 'RESULT.json'
        $result = Read-Json $resultPath
        $files = @()
        foreach ($f in 'p2p_detect.json','p2p_extract.json','p2p_rego.json','autopac_generate.json','autopac_judge.json','first_candidate.json','initial\original.rego','initial\admitted_policy.json','initial\CHECKS.json','repair.json','repaired\original.rego','repaired\CHECKS.json','RESULT.json') {
            $p = Join-Path $methodDir $f
            if (Test-Path -LiteralPath $p) { $files += Evidence $p }
        }
        $main = 'MAIN_CONSTRAINT_CORRECT_STATIC_SOURCE_POLICY_MAPPING'
        $direction = 'CORRECT_WITHIN_DOCUMENTED_KNOWN_STATE_DOMAIN'
        $optional = 'NOT_APPLICABLE'
        $compound = 'NOT_APPLICABLE'
        $default = 'NO_SOURCE_DEFAULT_REQUIREMENT_IDENTIFIED_FOR_THIS_FOCUSED_TARGET'
        $repair = 'NOT_RUN'
        if ($case -eq 'FSV-S03') {
            $direction = 'INTEGER_REQUIRED_IF_PRESENT'
            $optional = 'PRESERVED_BY_ON_MISSING_SKIP'
            if ($method -eq 'P2P_STYLE') {
                $main = 'OUT_OF_SCOPE_TYPE_VALIDATION_RECOGNIZED_NO_POLICY_GENERATED'
                $direction = 'NO_POLICY_TO_ASSESS'
                $optional = 'NO_POLICY_TO_ASSESS'
            }
            if ($method -eq 'AUTOPAC_STYLE') {
                $main = 'INTEGER_TYPE_INTENT_IDENTIFIED_BUT_NONEXECUTABLE_CODE'
                $direction = 'INTEGER_INTENT_CORRECT_NOT_VALIDATED_AS_EXECUTABLE_POLICY'
                $optional = 'STATIC_PRESENCE_OVERCONSTRAINT_RISK_DEFAULT_FALSE_NO_MISSING_ALLOW_BRANCH'
                $repair = 'INTEGER_INTENT_RETAINED_UNDEFINED_TYPEOF_STILL_NONEXECUTABLE'
            }
        }
        if ($case -eq 'FSV-B13') {
            $compound = 'WITHIN_MAXIMUM_OR_AUTHORIZED_EXCEPTION_CORRECT'
        }
        if ($case -eq 'FSV-B19') {
            $compound = 'ON_HOLD_AND_INVOICES_OR_ALL_BLOCKS_PURCHASE_ORDER_KNOWN_ENUMS_CORRECT'
            if ($method -eq 'ECAS_MATCHED') {
                $default = 'EMPTY_HELD_TYPE_DENIED_CONSISTENT_WITH_DOCUMENTED_DEFAULT_ALL_IF_RAW_EMPTY_REACHES_GATEWAY'
            } else {
                $default = 'EMPTY_HELD_TYPE_ALLOWED_DOCUMENT_DEFAULT_ALL_NOT_MAPPED_IF_RAW_EMPTY_REACHES_GATEWAY'
            }
        }
        $rows += [ordered]@{
            case = $case; method = $method
            main_constraint_mapping = $main; decision_direction = $direction
            compound_or_exception = $compound; optional_presence = $optional
            source_default = $default
            first_development_accepted = $result.first_checks.accepted
            final_status = $result.status; repaired_once = $result.repaired_once
            repair_semantic_observation = $repair
            auto_judge = $(if ($method -eq 'AUTOPAC_STYLE') { Read-Json (Join-Path $methodDir 'autopac_judge.json') } else { $null })
            archived_branch_observations = @($result.final_evaluation.branches | Where-Object { $_.label -in @('held-empty-type','held-unknown-type','missing-trusted') } | ForEach-Object { [ordered]@{
                label = $_.label; archived_kind = $_.kind; expected = $_.expected; actual = $_.actual.decision
            } })
            evidence_files = $files
        }
    }
}
if ($rows.Count -ne 12) { throw 'Expected exactly four cases and three methods.' }
$b19PacketPath = Join-Path $base 'generation_inputs\FSV-B19\packet.json'
$b19Packet = Read-Json $b19PacketPath
$supplierSource = @($b19Packet.visible_sources | Where-Object { $_.evidence_id -eq 'VIS-FSV-B19-01' })[0]
$abiSource = @($b19Packet.visible_sources | Where-Object { $_.evidence_id -eq 'VIS-FSV-B19-RUNTIME-ABI' })[0]
$supplierFields = @($b19Packet.visible_sources | Where-Object { $_.evidence_id -eq 'VIS-FSV-B19-03' })[0]
$startMarker = '### 2.4 Payment Terms and Block Supplier'
$endMarker = '### 2.5 Default Payable Accounts'
$sourceStart = $supplierSource.content.IndexOf($startMarker, [System.StringComparison]::Ordinal)
$sourceEnd = $supplierSource.content.IndexOf($endMarker, $sourceStart, [System.StringComparison]::Ordinal)
if ($sourceStart -lt 0 -or $sourceEnd -le $sourceStart) { throw 'Cannot locate B19 full default-value source section.' }
$holdPath = @($abiSource.content.available_values | Where-Object { $_.path -eq '/trusted/holdType' })[0]
if ($holdPath.type -ne 'string' -or $holdPath.PSObject.Properties.Name -contains 'enum') { throw 'B19 ABI differed from observed string-only declaration.' }
$audit = [ordered]@{
    audit_id = 'ECAS-NEW-FOUR-SEMANTIC-AUDIT-20261015-01'
    date = '2026-10-15'; status = 'DERIVED_READ_ONLY_AUDIT_FOR_ROOT_INDEPENDENT_CHECK'
    new_model_calls = 0; new_policy_executions = 0
    procedure = 'Read frozen visible packets, P2P detection and extraction, generated policies, AutoPAC Judge, repair and existing result records; compare source-policy semantics statically; do not infer full understanding from request pair success.'
    sources = $sources; rows = $rows
    b19_default_value_posthoc_clue = [ordered]@{
        classification = 'POSTHOC_SOURCE_DEFAULT_CLUE_NOT_PREREGISTERED_SEMANTIC_PROBE'
        source_packet = Evidence $b19PacketPath
        source_evidence_id = $supplierSource.evidence_id
        full_source_subsection = $supplierSource.content.Substring($sourceStart, $sourceEnd - $sourceStart)
        supplier_doctype_fields = @($supplierFields.content.field_catalog | Where-Object { $_[0] -in @('on_hold','hold_type') })
        abi_evidence_id = $abiSource.evidence_id; abi_hold_path = $holdPath
        common_adapter = $b19Packet.common_adapter
        source_layer = 'Documentation says omitted hold type defaults to All; complete section includes the hold types and their affected operations.'
        abi_layer = 'ABI declares string path only, without enum or normalization guarantee; common adapter says original trusted unchanged. Select catalog contains an empty leading option plus All, Invoices, Payments, but it is not proof of saved empty production state.'
        production_layer = 'UNKNOWN whether production backend normalizes before adapter, whether empty held state is reachable, and whether adapter authenticates/freshens the state. No production vulnerability conclusion.'
        candidate_causality = 'ECAS has no explicit empty-to-All normalization rule. Its restrictive allow list yields the same observed denial as the source default. This is outcome consistency, not direct proof that the model extracted default-All semantics.'
        archived_classification_preserved = 'held-empty-type remains conservative_empty_type_control; no original result or branch classification modified.'
    }
    limits = @(
        'Four historical tasks from two existing systems; posthoc explanatory audit, not blind or independent evaluation.',
        'All three are GLM adaptations; no original P2P implementation or AutoPAC fine-tuned CodeT5 checkpoint run.',
        'Main constraint mapping is separate from source optionality/defaults, executable code, Inventory admission and gateway fail-closed controls.',
        'B19 normal source-enumerated state domain is equivalent across permit and deny formulations; missing or unknown state does not prove better business-semantic understanding.',
        'B19 empty hold type has explicit default-All source evidence but only applies to the gateway if the adapter exposes raw empty state rather than server-normalized All; no production observation proves that path.',
        'S03 optional-presence issue in invalid AutoPAC code is a static risk, not a new runtime observation.'
    )
}
$json = $audit | ConvertTo-Json -Depth 30
[System.IO.File]::WriteAllText((Join-Path $out 'NEW_FOUR_SEMANTIC_AUDIT.json'), $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
$parsed = Read-Json (Join-Path $out 'NEW_FOUR_SEMANTIC_AUDIT.json')
if ($parsed.rows.Count -ne 12) { throw 'Written JSON row count mismatch.' }
Write-Output "Audit exported: $($parsed.rows.Count) method-case rows; zero model calls; zero new policy executions."
