param([ValidateSet('setup','api','web','example','test','check')][string]$Part = 'api')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
$module = 'talent_check'
$python = Join-Path (Get-Location) '.venv/Scripts/python.exe'

function Run([string]$Program, [string[]]$CommandArguments) {
    & $Program @CommandArguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed: $Program. Read the first error above." }
}

if ($Part -eq 'setup') {
    if (-not (Test-Path -LiteralPath $python)) { Run 'python' @('-m','venv','.venv') }
    Run $python @('-m','pip','install','-r','requirements.lock.txt')
    Run 'npm.cmd' @('ci')
    Run 'npx.cmd' @('playwright','install','chromium')
    Write-Host 'Setup complete. Open two terminals: run.ps1 api and run.ps1 web. See START_HERE.'
    exit 0
}
if (-not (Test-Path -LiteralPath $python)) { throw "Run .$module
un.ps1 setup from the repository root first." }

# Independent teaching mode uses local storage. Private cloud configuration is not required.
$env:RADIX_MODULE = $module
$env:RADIX_ENV = 'development'
$env:RADIX_AUTH_MODE = 'local'
$env:RADIX_STORAGE_MODE = 'local'
$env:RADIX_DOCUMENT_STORAGE_MODE = 'local'
$env:RADIX_ALLOWED_ORIGIN = 'http://127.0.0.1:5173'
$env:RADIX_ALLOWED_ORIGINS = ''
$env:RADIX_DATA_DIR = "data/private/$module"

switch ($Part) {
    'api' { Run $python @('-m','uvicorn','apps.api.standalone:app','--host','127.0.0.1','--port','8000') }
    'web' { Run 'npm.cmd' @('run','dev:module','--','--host','127.0.0.1','--port','5173') }
    'example' { Run $python @('scripts/module_example.py',$module) }
    'check' { Run $python @('scripts/check_module.py',$module) }
    'test' {
        $env:RADIX_LLM_MODE = 'rules'
        $env:RADIX_LLM_API_KEY = ''
        $env:GROQ_API_KEY = ''
        Run $python @('scripts/module_example.py',$module)
        Run $python @('scripts/check_module.py',$module)
        Run $python @('-m','pytest',"$module/tests",'-q')
        Run 'npm.cmd' @('run','test','--',"$module/frontend")
        Run 'npm.cmd' @('run','typecheck')
        Run 'npm.cmd' @('run','lint')
        Run 'npm.cmd' @('run','build:module')
        Run 'npx.cmd' @('playwright','test','--config','playwright.handoff.config.ts','--project',$module)
        Write-Host "PASS: $module API, example, unit, component, type/lint/build and browser checks. Record YOUR results."
    }
}
