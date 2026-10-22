"""Exercise the shipped PowerShell source selection without running installation."""
import os,subprocess,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(os.name=='nt','Windows PowerShell is required')
class InstallerSourcePlan(unittest.TestCase):
    def test_matching_version_prerequisites_and_mixed_source_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            script=Path(directory)/'check.ps1'
            script.write_text(r'''
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1') -ErrorAction Stop
Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Utility/Microsoft.PowerShell.Utility.psd1') -ErrorAction Stop
Set-StrictMode -Version Latest
$tokens=$null; $errors=$null
$tree=[Management.Automation.Language.Parser]::ParseFile($env:TEST_INSTALLER,[ref]$tokens,[ref]$errors)
if ($errors.Count) { throw 'Installer syntax error' }
foreach ($name in @('Get-Sha256','Get-MatchingSourceVersion','Show-BackendPlan')) {
  $nodes=@($tree.FindAll({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $name},$true))
  if ($nodes.Count -ne 1) { throw 'Ambiguous installer function' }
  . ([scriptblock]::Create($nodes[0].Extent.Text))
}
$app=Join-Path $env:TEST_ROOT 'fixture'
$resources=Join-Path $app 'resources'
[void](New-Item -ItemType Directory -Path $resources)
$backend=Join-Path $resources 'codex.exe'
[IO.File]::WriteAllBytes($backend,[Text.Encoding]::UTF8.GetBytes('synthetic backend'))
$digest=Get-Sha256 $backend
$versionInfo=[pscustomobject]@{source_contracts=[pscustomobject]@{'26.1016.8120.0'=[pscustomobject]@{asar_sha256=('a'*64);backend_sha256=$digest}}}
$version=Get-MatchingSourceVersion -App $app -AsarHash ('a'*64)
if ($version -ne '26.1016.8120.0') { throw 'Source version was not selected' }
$BackendMode='compat'; $BackendManifest=''
$current=(& { Show-BackendPlan -SourceVersion $version } 6>&1 | Out-String)
if ($current -notmatch 'Rust 1.99.1' -or $current -notmatch 'Official package: 26.1016.8120.0') { throw 'Current profile prerequisites missing' }
$old=(& { Show-BackendPlan -SourceVersion '26.1016.6573.0' } 6>&1 | Out-String)
if ($old -notmatch 'Rust 1.95.0') { throw 'Previous profile prerequisites changed' }
$rejected=$false
try { Get-MatchingSourceVersion -App $app -AsarHash ('b'*64) } catch { $rejected=$true }
if (-not $rejected) { throw 'Unknown source accepted' }
[IO.File]::WriteAllBytes($backend,[Text.Encoding]::UTF8.GetBytes('another backend'))
$rejected=$false
try { Get-MatchingSourceVersion -App $app -AsarHash ('a'*64) } catch { $rejected=$true }
if (-not $rejected) { throw 'Mixed official backend accepted' }
$versionInfo=[pscustomobject]@{version='historical-bundle'}
if ($null -ne (Get-MatchingSourceVersion -App $app -AsarHash ('a'*64))) { throw 'Legacy bundle should retain its deferred source gate' }
Write-Output 'source-plan-cases-passed'
''',encoding='utf-8-sig')
            env={**os.environ,'TEST_INSTALLER':str(ROOT/'install.ps1'),'TEST_ROOT':directory}
            host=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
            result=subprocess.run([str(host),'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(script)],env=env,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=30,creationflags=0x08000000)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('source-plan-cases-passed',result.stdout)

if __name__=='__main__':unittest.main()
