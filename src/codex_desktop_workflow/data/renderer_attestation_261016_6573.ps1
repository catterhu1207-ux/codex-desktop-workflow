function Get-StructuredLogJsonObject {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value.Length -eq 0 -or $Value[0] -ne '{') { return $null }
    $depth = 0
    $inString = $false
    $escaped = $false
    for ($index = 0; $index -lt $Value.Length; $index++) {
        $character = $Value[$index]
        if ($inString) {
            if ($escaped) {
                $escaped = $false
            } elseif ($character -eq '\') {
                $escaped = $true
            } elseif ($character -eq '"') {
                $inString = $false
            }
            continue
        }
        if ($character -eq '"') {
            $inString = $true
        } elseif ($character -eq '{') {
            $depth++
        } elseif ($character -eq '}') {
            $depth--
            if ($depth -eq 0) { return $Value.Substring(0, $index + 1) }
            if ($depth -lt 0) { return $null }
        }
    }
    return $null
}

function Get-6573FrontendFeatureAttestation {
    param(
        [Parameter(Mandatory = $true)][string]$LogsRoot,
        [Parameter(Mandatory = $true)][int]$TargetProcessId,
        [Parameter(Mandatory = $true)][DateTimeOffset]$StartedAt,
        [Parameter(Mandatory = $true)][object]$QualifiedManifest
    )
    $revision = [string]$QualifiedManifest.builder_version
    $artifact = $revision + '-6f56542b508e'
    $expectedAsar = ''
    $expectedModule = ''
    if ($revision -eq '2.9.2') {
        $expectedAsar = '9928bccc3ca070ff255f3bdf3c12e19fff43430a4ef538e203b443e1a6f4d177'
        $expectedModule = '416270f0069a5e9193210fd6821df6021c79a2189b98977db997a9feca7c16f3'
    }
    $required = @(
        'priority_filter_recency_sorting','priority_filter_live_resort',
        'priority_filter_pinned_recency_sorting','priority_filter_hold_membership',
        'priority_click_hold','priority_identity_migration','priority_project_context_subtitle',
        'plan_pending_detection','plan_pending_yellow_indicator','plan_pending_unread_indicator',
        'attention_highlight_color_semantics','project_sorting','active_priority_sort',
        'automation_priority_gate','pinned_priority_sync','new_chat_file_drop',
        'resume_history_on_demand','paginated_tail_retention','idle_history_eviction',
        'remote_project_label','work_remote_project_picker','user_action_pending_orange',
        'portable_update_awareness'
    )
    $probe = $QualifiedManifest.frontend_runtime_attestation.live_renderer_probe
    if ($QualifiedManifest.package_version -ne '26.1016.6573.0' -or
        $QualifiedManifest.package_full_name -ne 'OpenAI.Codex_26.1016.6573.0_x64__2p2nqsd0c76g0' -or
        $QualifiedManifest.official_source_sha256 -ne '6f56542b508eea5b6e4d03e852dcd90afc2578aac7125baa3f25ebe85ebc7e25' -or
        $QualifiedManifest.portable_asar_sha256 -ne $expectedAsar -or
        $revision -notin @('2.9.2') -or
        $QualifiedManifest.frontend_runtime_attestation.validator_version -ne $revision -or
        $probe.artifact_id -ne $artifact -or $probe.schema_version -ne 7 -or
        $probe.module_sha256 -ne $expectedModule -or
        @($QualifiedManifest.feature_contracts.psobject.Properties).Count -ne 26 -or
        @($probe.feature_ids).Count -ne 23 -or
        @($probe.feature_ids | Select-Object -Unique).Count -ne 23 -or
        @($required | Where-Object { $_ -notin $probe.feature_ids }).Count -gt 0) {
        return [pscustomobject]@{fatal=$true;kind='frontend_attestation_contract_failed';error='The 6573 qualified manifest identity or feature inventory differs.'}
    }
    if (-not (Test-Path -LiteralPath $LogsRoot -PathType Container)) { return $null }
    $pidPattern = '-' + [regex]::Escape([string]$TargetProcessId) + '-t\d+-'
    $minimum = $StartedAt.UtcDateTime.AddSeconds(-5)
    $files = @(Get-ChildItem -LiteralPath $LogsRoot -Recurse -File -Filter 'codex-desktop-*.log' -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match $pidPattern -and $_.CreationTimeUtc -ge $minimum } |
        Sort-Object CreationTimeUtc,Name)
    $loaded = $null
    foreach ($file in $files) {
        $stream = $null
        $reader = $null
        try {
            $stream = [IO.File]::Open($file.FullName,[IO.FileMode]::Open,[IO.FileAccess]::Read,
                ([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete))
            $reader = [IO.StreamReader]::new($stream,[Text.Encoding]::UTF8,$true,4096,$true)
            while (-not $reader.EndOfStream) {
                $line = $reader.ReadLine()
                $at = $line.IndexOf('[CF9]',[StringComparison]::Ordinal)
                if ($at -lt 0 -or
                    $line -notmatch 'rendererWindowAppearance=["'']?primary(?:["'']|\s|$)' -or
                    $line -notmatch 'rendererWindowVisible=["'']?true(?:["'']|\s|$)') { continue }
                $payload = Get-StructuredLogJsonObject -Value $line.Substring($at+5).Trim()
                if ([string]::IsNullOrWhiteSpace($payload)) {
                    return [pscustomobject]@{fatal=$false;status='log_read_pending';
                        kind='frontend_attestation_log_read_pending';file_name=$file.Name;
                        error='6573 renderer JSON record is still incomplete.'}
                }
                $proof = $payload | ConvertFrom-Json -ErrorAction Stop
                if ($proof.schema_version -ne 7 -or $proof.validator_version -ne $revision -or
                    $proof.artifact_id -ne $artifact -or
                    [string]$proof.run_id -notmatch '^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$' -or
                    $proof.content_logged -ne $false -or $proof.transport -ne 'renderer_log_message_v1') {
                    throw '6573 renderer record identity or transport differs.'
                }
                if ($proof.status -eq 'module_loaded') {
                    $loaded = [pscustomobject]@{fatal=$false;status='module_loaded';process_id=$TargetProcessId;
                        artifact_id=$artifact;run_id=[string]$proof.run_id;validator_version=$revision;
                        transport='renderer_log_message_v1';content_logged=$false;log_file=$file.Name;
                        checked_at=[DateTimeOffset]::Now.ToString('o')}
                    continue
                }
                if (-not $loaded -or $loaded.run_id -ne $proof.run_id) {
                    throw '6573 final proof has no matching module-loaded record.'
                }
                if ($proof.status -eq 'failed') {
                    return [pscustomobject]@{fatal=$true;kind='frontend_attestation_feature_execution_failed';
                        error=('6573 renderer check failed: '+[string]$proof.failure_code);
                        failure_code=$proof.failure_code;file_name=$file.Name}
                }
                if ($proof.status -ne 'passed' -or
                    $proof.scope -ne 'packaged_synthetic_runtime_regression' -or
                    $proof.native_function_bindings -ne $true -or $proof.actual_renderer -ne $true -or
                    $proof.main_route_mounted -ne $true -or $proof.user_catalog_read -ne $false -or
                    $proof.user_data_modified -ne $false -or $proof.external_requests_sent -ne $false -or
                    $proof.palette.yellow -ne 'rgb(234, 179, 8)' -or
                    $proof.palette.orange -ne 'rgb(249, 115, 22)' -or
                    [string]::IsNullOrWhiteSpace([string]$proof.palette.red) -or
                    [string]::IsNullOrWhiteSpace([string]$proof.palette.blue) -or
                    @(@($proof.palette.yellow,$proof.palette.orange,$proof.palette.red,$proof.palette.blue) |
                        Select-Object -Unique).Count -ne 4) {
                    throw '6573 native execution, isolation or computed colors differ.'
                }
                $props = @($proof.features.psobject.Properties)
                if ($props.Count -ne $required.Count) { throw '6573 renderer feature count differs.' }
                foreach ($name in $required) {
                    if ($proof.features.$name.passed -ne $true -or
                        [string]::IsNullOrWhiteSpace([string]$proof.features.$name.evidence)) {
                        throw ('6573 renderer did not prove '+$name)
                    }
                }
                return [pscustomobject][ordered]@{fatal=$false;status='passed';protocol='live_renderer_attestation_v3';
                    transport='renderer_log_message_v1';checked_at=[DateTimeOffset]::Now.ToString('o');
                    process_id=$TargetProcessId;artifact_id=$artifact;run_id=[string]$proof.run_id;
                    validator_version=$revision;feature_count=$required.Count;features=$proof.features;
                    computed_colors=$proof.palette;computed_color='renderer_dom_get_computed_style';
                    content_logged=$false;log_file=$file.Name}
            }
        } catch [IO.IOException] {
            return [pscustomobject]@{fatal=$false;status='log_read_pending';
                kind='frontend_attestation_log_read_pending';file_name=$file.Name;
                error=$_.Exception.Message}
        } catch {
            return [pscustomobject]@{fatal=$true;kind='frontend_attestation_contract_failed';
                error=$_.Exception.Message;file_name=$file.Name}
        } finally {
            if ($reader) { $reader.Dispose() }
            if ($stream) { $stream.Dispose() }
        }
    }
    return $loaded
}

function Get-PortableFrontendFeatureAttestation {
 param([string]$LogsRoot,[int]$TargetProcessId,[DateTimeOffset]$StartedAt,[object]$QualifiedManifest)
 if ($QualifiedManifest.builder_version -ne '2.9.2') { return [pscustomobject]@{fatal=$true;status='failed';error='Unsupported public 6573 revision'} }
 Get-6573FrontendFeatureAttestation -LogsRoot $LogsRoot -TargetProcessId $TargetProcessId -StartedAt $StartedAt -QualifiedManifest $QualifiedManifest
}
