param([string]$ComposeFile = 'docker-compose.yml', [string]$Project = 'nashaa')
$ErrorActionPreference = 'Stop'
$backupDir = Join-Path $PSScriptRoot '../.backups'
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$containerFile = "/tmp/nashaa-$stamp.dump"
$hostFile = Join-Path $backupDir "nashaa-$stamp.dump"
docker compose -p $Project -f $ComposeFile exec -T database sh -c 'pg_dump -Fc -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$1"' sh $containerFile
if ($LASTEXITCODE -ne 0) { throw 'Database backup failed.' }
docker compose -p $Project -f $ComposeFile cp "database:$containerFile" $hostFile
if ($LASTEXITCODE -ne 0) { throw 'Could not copy backup to host.' }
Get-FileHash -LiteralPath $hostFile -Algorithm SHA256
