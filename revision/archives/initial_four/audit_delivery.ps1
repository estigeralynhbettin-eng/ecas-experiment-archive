$ErrorActionPreference='Stop'
$base=$PSScriptRoot
function Convert-LinuxPath([string]$value){
    if($value.StartsWith('/mnt/d/')){return 'D:/'+$value.Substring(7)}
    if($value.StartsWith('/mnt/c/')){return 'C:/'+$value.Substring(7)}
    return '\\wsl.localhost\Ubuntu'+$value.Replace('/','\')
}
$byPath=@{}
foreach($name in @('EXECUTION_INPUT_MANIFEST.json','FORMAT_RECOVERY_INPUT_MANIFEST.json','DOCUMENTED_INPUT_MANIFEST.json')){
    $manifest=Get-Content -Raw -LiteralPath (Join-Path $base $name)|ConvertFrom-Json
    foreach($entry in $manifest){
        if($byPath.ContainsKey($entry.path) -and $byPath[$entry.path].sha256 -ne $entry.sha256){throw 'Conflicting frozen versions'}
        $byPath[$entry.path]=$entry
    }
}
$inputChecks=foreach($entry in $byPath.Values){
    $path=Convert-LinuxPath $entry.path
    [pscustomobject]@{path=$entry.path;pass=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -eq $entry.sha256}
}
$calls=@(Get-Content -Raw -LiteralPath (Join-Path $base 'CALL_LEDGER.json')|ConvertFrom-Json)
$rawChecks=foreach($call in $calls){
    $rawPath=Convert-LinuxPath $call.raw_response_path
    $raw=Get-Content -Raw -LiteralPath $rawPath|ConvertFrom-Json
    [pscustomobject]@{
        index=$call.index
        pass=((Get-FileHash -LiteralPath $rawPath -Algorithm SHA256).Hash -eq $call.raw_response_sha256) -and $raw.model -eq 'glm-5.2' -and $raw.choices[0].finish_reason -eq 'stop' -and $call.status -eq 'COMPLETED'
        usage_matches=($raw.usage.prompt_tokens -eq $call.usage.prompt_tokens) -and ($raw.usage.completion_tokens -eq $call.usage.completion_tokens)
        budget_ok=($raw.usage.prompt_tokens -le 16384) -and ($raw.usage.completion_tokens -le 16384)
    }
}
$summary=Get-Content -Raw -LiteralPath (Join-Path $base 'COMPARISON_SUMMARY.json')|ConvertFrom-Json
$rows=foreach($row in $summary.rows){
    $source=Join-Path (Convert-LinuxPath $row.source_folder) 'RESULT.json'
    $result=Get-Content -Raw -LiteralPath $source|ConvertFrom-Json
    $same=$row.status -eq $result.status -and @($row.requests).Count -eq @($result.requests).Count
    for($i=0;$i -lt @($row.requests).Count;$i++){
        $same=$same -and $row.requests[$i].actual.decision -eq $result.requests[$i].actual.decision -and $row.requests[$i].expected -eq $result.requests[$i].expected
    }
    $probeFlags=@($row.branch_probes|Where-Object { $_.pass -ne (($_.actual.decision -eq $_.expected) -and (-not $_.actual.engine_error)) }).Count -eq 0
    $pair=if($row.status -eq 'EVALUATED'){@($row.requests).Count -eq 2 -and @($row.requests|Where-Object {$_.actual.decision -ne $_.expected -or $_.actual.engine_error}).Count -eq 0}else{$null}
    [pscustomobject]@{task=$row.task;method=$row.method;summary_matches_result=$same;pair_flag_matches=$pair -eq $row.pair_correct;probe_flags_match=$probeFlags}
}
$ok=@($inputChecks|Where-Object {-not $_.pass}).Count -eq 0
$ok=$ok -and @($rawChecks|Where-Object {-not $_.pass -or -not $_.usage_matches -or -not $_.budget_ok}).Count -eq 0
$ok=$ok -and @($rows|Where-Object {-not $_.summary_matches_result -or -not $_.pair_flag_matches -or -not $_.probe_flags_match}).Count -eq 0
$ok=$ok -and $calls.Count -eq $summary.calls -and $calls.Count -le 40 -and $summary.reconciliation -eq 'PASS'
$output=[ordered]@{status=$(if($ok){'PASS'}else{'FAIL'});classification='INDEPENDENT_DETERMINISTIC_DELIVERY_RECONCILIATION_NOT_SCIENTIFIC_CLEARANCE';frozen_unique_files=$inputChecks.Count;raw_calls=$calls.Count;comparison_rows=$rows.Count;input_checks=@($inputChecks);raw_checks=@($rawChecks);row_checks=@($rows)}
$output|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $base 'DELIVERY_QA.json') -Encoding utf8
[pscustomobject]$output|Select-Object status,frozen_unique_files,raw_calls,comparison_rows|ConvertTo-Json
if(-not $ok){throw 'Delivery reconciliation failed'}
