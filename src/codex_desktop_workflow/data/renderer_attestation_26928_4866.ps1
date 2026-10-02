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

function Get-PortableFrontendFeatureAttestation {
    param(
        [Parameter(Mandatory = $true)][string]$LogsRoot,
        [Parameter(Mandatory = $true)][int]$TargetProcessId,
        [Parameter(Mandatory = $true)][DateTimeOffset]$StartedAt,
        [object]$QualifiedManifest = $null
    )
    # A new proof inventory is selected only by the exact qualified artifact.
    # Historical callers retain their own validator and required feature set.
    if ($null -ne $QualifiedManifest -and $QualifiedManifest.package_version -eq '26.928.4866.0') {
        $nativeProbe = $QualifiedManifest.frontend_runtime_attestation.live_renderer_probe
        if ($QualifiedManifest.package_full_name -ne 'OpenAI.Codex_26.928.4866.0_x64__2p2nqsd0c76g0' -or
            $QualifiedManifest.official_source_sha256 -ne '84fe697418b26a921f8d14090616559498a02f51768ff0bba69cefaadf4086f5' -or
            $QualifiedManifest.builder_version -ne '2.7.9' -or
            $QualifiedManifest.frontend_runtime_attestation.validator_version -ne '2.6.0' -or
            $nativeProbe.artifact_id -ne '2.7.9-84fe697418b2' -or
            @($QualifiedManifest.feature_contracts.psobject.Properties).Count -ne 25 -or
            @($nativeProbe.feature_ids).Count -ne 22) {
            return [pscustomobject]@{fatal = $true; kind = 'frontend_attestation_contract_failed'; error = 'The qualified manifest does not match the exact new proof contract.'}
        }
        $expectedFrontendContractValidatorVersion = '2.6.0'
        $expectedFrontendAttestationArtifactId = '2.7.9-84fe697418b2'
        $requiredLiveRendererFeatures = @($requiredLiveRendererFeatures | Where-Object { $_ -ne 'user_action_pending_orange' }) + @('user_action_pending_orange')
        if (@($requiredLiveRendererFeatures | Select-Object -Unique).Count -ne 22 -or
            @($requiredLiveRendererFeatures | Where-Object { @($nativeProbe.feature_ids) -notcontains $_ }).Count -ne 0) {
            return [pscustomobject]@{fatal = $true; kind = 'frontend_attestation_feature_inventory_failed'; error = 'The new proof contract has an invalid required feature inventory.'}
        }
    }
    if (-not (Test-Path -LiteralPath $LogsRoot -PathType Container)) { return $null }
    $pidPattern = '-' + [regex]::Escape([string]$TargetProcessId) + '-t\d+-'
    $minimumCreationTime = $StartedAt.UtcDateTime.AddSeconds(-5)
    $candidates = @(Get-ChildItem -LiteralPath $LogsRoot -Recurse -File `
        -Filter 'codex-desktop-*.log' -ErrorAction SilentlyContinue | Where-Object {
            $_.Name -match $pidPattern -and $_.CreationTimeUtc -ge $minimumCreationTime
        } | Sort-Object LastWriteTimeUtc -Descending)
    $lastLoaded = $null
    foreach ($candidate in $candidates) {
        $stream = $null
        $reader = $null
        try {
            $stream = [IO.File]::Open(
                $candidate.FullName,
                [IO.FileMode]::Open,
                [IO.FileAccess]::Read,
                ([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete)
            )
            $reader = [IO.StreamReader]::new($stream, [Text.Encoding]::UTF8, $true, 4096, $true)
            while (-not $reader.EndOfStream) {
                $line = $reader.ReadLine()
                $markerIndex = $line.IndexOf($expectedFrontendAttestationMarker, [StringComparison]::Ordinal)
                if ($markerIndex -lt 0) { continue }
                # The renderer entry is shared by the visible primary window
                # and hidden auxiliary windows such as avatarOverlay.  Only a
                # proof emitted by the visible primary renderer can attest the
                # user-facing UI.  Auxiliary failures and successes are
                # diagnostic-only and must not decide launch eligibility.
                if ($line -notmatch 'rendererWindowAppearance=["'']?primary(?:["'']|\s|$)' -or
                    $line -notmatch 'rendererWindowVisible=["'']?true(?:["'']|\s|$)') {
                    continue
                }
                $payload = $line.Substring($markerIndex + $expectedFrontendAttestationMarker.Length).Trim()
                if ($payload.StartsWith('E', [StringComparison]::Ordinal)) {
                    return [pscustomobject][ordered]@{
                        fatal = $true
                        kind = 'frontend_attestation_module_import_failed'
                        error = if ($payload.Length -gt 2) {
                            'The signed frontend module import failed: ' + $payload.Substring(2)
                        } else {
                            'The signed frontend module import failed before it could publish a proof.'
                        }
                        file_name = $candidate.Name
                    }
                }
                $jsonPayload = Get-StructuredLogJsonObject -Value $payload
                try {
                    if ([string]::IsNullOrWhiteSpace($jsonPayload)) {
                        throw 'The structured log did not contain one complete JSON object.'
                    }
                    $proof = $jsonPayload | ConvertFrom-Json -ErrorAction Stop
                } catch {
                    return [pscustomobject][ordered]@{
                        fatal = $true
                        kind = 'frontend_attestation_contract_failed'
                        error = 'The real renderer returned a damaged feature-attestation record.'
                        file_name = $candidate.Name
                    }
                }
                if ($proof.schema_version -ne $expectedFrontendAttestationSchemaVersion -or
                    $proof.validator_version -ne $expectedFrontendContractValidatorVersion -or
                    $proof.artifact_id -ne $expectedFrontendAttestationArtifactId -or
                    [string]$proof.run_id -notmatch '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$' -or
                    $proof.content_logged -ne $false -or
                    $proof.transport -ne 'renderer_log_message_v1') {
                    return [pscustomobject][ordered]@{
                        fatal = $true
                        kind = 'frontend_attestation_contract_failed'
                        error = 'The real renderer returned an invalid proof identity or transport.'
                        file_name = $candidate.Name
                    }
                }
                if ($proof.status -eq 'module_loaded') {
                    $lastLoaded = [pscustomobject][ordered]@{
                        fatal = $false
                        status = 'module_loaded'
                        checked_at = [DateTimeOffset]::Now.ToString('o')
                        process_id = $TargetProcessId
                        artifact_id = $expectedFrontendAttestationArtifactId
                        run_id = [string]$proof.run_id
                        validator_version = $expectedFrontendContractValidatorVersion
                        transport = 'renderer_log_message_v1'
                        content_logged = $false
                        log_file = $candidate.Name
                    }
                    continue
                }
                if (-not $lastLoaded -or
                    [string]$lastLoaded.run_id -ne [string]$proof.run_id -or
                    [string]$lastLoaded.log_file -ne [string]$candidate.Name) {
                    return [pscustomobject][ordered]@{
                        fatal = $true
                        kind = 'frontend_attestation_contract_failed'
                        error = 'The visible primary renderer returned a final proof without its matching module-loaded record.'
                        file_name = $candidate.Name
                    }
                }
                if ($proof.status -eq 'failed') {
                    return [pscustomobject][ordered]@{
                        fatal = $true
                        kind = 'frontend_attestation_feature_execution_failed'
                        error = 'The real renderer executed the feature suite but it failed: ' + [string]$proof.failure_code
                        failure_code = [string]$proof.failure_code
                        file_name = $candidate.Name
                    }
                }
                if ($proof.status -ne 'passed' -or
                    ($expectedFrontendContractValidatorVersion -in @('2.5.1','2.6.0') -and ($proof.ssh_label -ne 'project-alpha' -or $proof.new_chat_picker_label -ne 'project-alpha' -or $null -eq $proof.new_chat_picker_visible_uuid_count -or [int]$proof.new_chat_picker_visible_uuid_count -ne 0)) -or
                    ($expectedFrontendContractValidatorVersion -notin @('2.5.1','2.6.0') -and $proof.ssh_label -ne 'mailassistant') -or
                    [int]$proof.ssh_post_merge_uuid_count -ne 0 -or
                    $proof.ssh_thread_keys_preserved -ne $true -or
                    $proof.ssh_host_path_fallback -ne $true -or
                    $proof.route_identity_unchanged -ne $true -or
                    $proof.plan_waiting_yellow -ne $true -or
                    ($expectedFrontendContractValidatorVersion -notin @('2.4.12', '2.5.0', '2.5.1','2.6.0') -and $proof.plan_source -ne 'pending_request_type') -or
                    ($expectedFrontendContractValidatorVersion -in @('2.4.12', '2.5.0', '2.5.1','2.6.0') -and ($proof.plan_source -ne 'pending_request_kind' -or $proof.mounted_row.status -ne 'passed' -or $proof.mounted_row.actual_react_row -ne $true -or $proof.mounted_row.official_producer -ne $true -or $proof.mounted_row.retained_root -ne $true -or $proof.mounted_row.spinner -ne $true -or $proof.mounted_row.pinned_plan_color -ne 'rgb(234, 179, 8)' -or $proof.mounted_row.read_plan_color -ne 'rgb(234, 179, 8)' -or $proof.mounted_row.completed_cleared -ne $true)) -or
                    ($expectedFrontendContractValidatorVersion -eq '2.6.0' -and ($proof.mounted_row.orange_pending -ne $true -or $proof.mounted_row.orange_color -ne 'rgb(249, 115, 22)')) -or
                    $proof.colors.red -ne 'var(--color-text-danger)' -or
                    $proof.colors.yellow -ne '#eab308' -or
                    $proof.computed_colors.yellow -ne 'rgb(234, 179, 8)' -or
                    $proof.colors.blue -ne 'var(--color-text-info)' -or
                    [string]::IsNullOrWhiteSpace([string]$proof.computed_colors.red) -or
                    [string]::IsNullOrWhiteSpace([string]$proof.computed_colors.yellow) -or
                    [string]::IsNullOrWhiteSpace([string]$proof.computed_colors.blue) -or
                    @(@(
                        [string]$proof.computed_colors.red,
                        [string]$proof.computed_colors.yellow,
                        [string]$proof.computed_colors.blue
                    ) | Select-Object -Unique).Count -ne 3) {
                    return [pscustomobject][ordered]@{
                        fatal = $true
                        kind = 'frontend_attestation_contract_failed'
                        error = 'The real renderer returned an invalid identity, color, SSH-label, or route result.'
                        file_name = $candidate.Name
                    }
                }
                $proofProperties = @($proof.features.psobject.Properties)
                if ($proofProperties.Count -ne $requiredLiveRendererFeatures.Count) {
                    return [pscustomobject][ordered]@{
                        fatal = $true
                        kind = 'frontend_attestation_feature_inventory_failed'
                        error = 'The real renderer did not report the exact required feature inventory.'
                        file_name = $candidate.Name
                    }
                }
                $featureEvidence = [ordered]@{}
                foreach ($featureName in $requiredLiveRendererFeatures) {
                    $featureProof = $proof.features.$featureName
                    if (-not $featureProof -or
                        $featureProof.passed -ne $true -or
                        [string]::IsNullOrWhiteSpace([string]$featureProof.evidence)) {
                        return [pscustomobject][ordered]@{
                            fatal = $true
                            kind = 'frontend_attestation_feature_failed'
                            error = "The real renderer did not prove feature: $featureName"
                            feature_id = $featureName
                            file_name = $candidate.Name
                        }
                    }
                    $featureEvidence[$featureName] = [pscustomobject][ordered]@{
                        passed = $true
                        evidence = [string]$featureProof.evidence
                    }
                }
                return [pscustomobject][ordered]@{
                    fatal = $false
                    status = 'passed'
                    protocol = 'live_renderer_attestation_v3'
                    transport = 'renderer_log_message_v1'
                    checked_at = [DateTimeOffset]::Now.ToString('o')
                    process_id = $TargetProcessId
                    artifact_id = $expectedFrontendAttestationArtifactId
                    run_id = [string]$proof.run_id
                    validator_version = $expectedFrontendContractValidatorVersion
                    feature_count = $requiredLiveRendererFeatures.Count
                    features = [pscustomobject]$featureEvidence
                    colors = $proof.colors
                    computed_colors = $proof.computed_colors
                    plan_waiting_yellow = $true
                    plan_source = [string]$proof.plan_source
                    mounted_row = $proof.mounted_row
                    computed_color = 'renderer_dom_get_computed_style'
                    content_logged = $false
                    log_file = $candidate.Name
                }
            }
        } catch {
            return [pscustomobject][ordered]@{
                fatal = $true
                kind = 'frontend_attestation_log_read_failure'
                error = $_.Exception.Message
                file_name = $candidate.Name
            }
        } finally {
            if ($reader) { $reader.Dispose() }
            if ($stream) { $stream.Dispose() }
        }
    }
    return $lastLoaded
}