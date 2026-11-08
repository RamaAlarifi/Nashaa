param([string]$BackupFile, [switch]$VerifyRestore)
$ErrorActionPreference='Stop'
if(-not $BackupFile){$BackupFile=Join-Path $PWD ('backups\nashaa-'+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.dump')}
$resolved=[IO.Path]::GetFullPath($BackupFile)
$parent=Split-Path -Parent $resolved
New-Item -ItemType Directory -Force -Path $parent | Out-Null
if(Test-Path -LiteralPath $resolved){throw 'Choose a new backup filename; existing backups are never overwritten.'}
# pg_dump writes a custom-format archive directly, avoiding PowerShell's binary
# redirection/encoding pitfalls. No database credentials appear in host output.
$remote='/tmp/nashaa-backup-'+[guid]::NewGuid().ToString('N')+'.dump'
docker compose exec -T database sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f "$1"' sh $remote
if($LASTEXITCODE -ne 0){throw 'Database backup failed.'}
docker compose cp "database:$remote" $resolved
if($LASTEXITCODE -ne 0){throw 'Could not copy the backup out of the container.'}
Write-Output "Backup stored outside the database container: $resolved"
if($VerifyRestore){
  $testDb='nashaa_restore_'+[guid]::NewGuid().ToString('N')
  if($testDb -notmatch '^nashaa_restore_[0-9a-f]{32}$'){throw 'Unsafe restore database name.'}
  docker compose exec -T database sh -c 'createdb -U "$POSTGRES_USER" "$1" && pg_restore -U "$POSTGRES_USER" --exit-on-error --no-owner -d "$1" "$2"' sh $testDb $remote
  if($LASTEXITCODE -ne 0){throw "Restore verification failed; disposable database retained: $testDb"}
  $verificationSql='SELECT version_num FROM alembic_version; SELECT count(*) FROM users; SELECT count(*) FROM business_ideas; SELECT count(*) FROM assessments; SELECT count(*) FROM collaborations; SELECT count(*) FROM customer_profiles; SELECT count(*) FROM leads; SELECT count(*) FROM ratings; SELECT count(*) FROM user_reports; SELECT count(*) FROM admin_actions; SELECT count(*) FROM progress_updates; SELECT count(*) FROM lead_sources; SELECT count(*) FROM company_records; SELECT count(*) FROM lead_notes; SELECT count(*) FROM outreach_drafts; SELECT count(*) FROM evaluation_sessions;'
  $sourceCounts=$verificationSql | docker compose exec -T database sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -At -v ON_ERROR_STOP=1'
  if($LASTEXITCODE -ne 0){throw 'Source-record verification failed.'}
  $restoredCounts=$verificationSql | docker compose exec -T database sh -c 'psql -U "$POSTGRES_USER" -d "$1" -At -v ON_ERROR_STOP=1' sh $testDb
  if($LASTEXITCODE -ne 0){throw 'Restored-record verification failed.'}
  if(($sourceCounts -join "`n") -ne ($restoredCounts -join "`n")){throw 'Source and restore counts differ; retain the disposable database for investigation.'}
  Write-Output ('Verified schema version and row counts for users, ideas, assessments, collaborations, customer profiles, leads, ratings, reports, audit records, progress, sources, companies, notes, drafts and evaluation records: '+($restoredCounts -join ', '))
  Write-Output "Restored successfully into disposable database $testDb. The application database was not replaced."
  # Restrict cleanup to the exact disposable database created by this run.
  docker compose exec -T database sh -c 'dropdb -U "$POSTGRES_USER" "$1"' sh $testDb
  if($LASTEXITCODE -ne 0){throw 'Disposable restore database cleanup failed.'}
}
docker compose exec -T database rm -- $remote
