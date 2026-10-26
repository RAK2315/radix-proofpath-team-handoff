param([ValidateSet('api','web','check')][string]$Part = 'api')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$env:RADIX_MODULE = 'resume_parsing'
$env:RADIX_ENV = 'development'
$env:RADIX_AUTH_MODE = 'local'
$env:RADIX_STORAGE_MODE = 'local'
$env:RADIX_DOCUMENT_STORAGE_MODE = 'local'
$env:RADIX_ALLOWED_ORIGIN = 'http://127.0.0.1:5173'
$env:RADIX_ALLOWED_ORIGINS = ''
$env:RADIX_DATA_DIR = 'data/private/resume_parsing'
if ($Part -eq 'api') { & '.\.venv\Scripts\python.exe' -m uvicorn apps.api.standalone:app --host 127.0.0.1 --port 8000 }
elseif ($Part -eq 'web') { npm run dev:module -- --host 127.0.0.1 --port 5173 }
else { & '.\.venv\Scripts\python.exe' scripts/check_module.py 'resume_parsing' }
if ($LASTEXITCODE -ne 0) { throw 'Module command failed. Read the error above.' }
