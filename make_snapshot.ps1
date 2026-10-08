$root = "C:\Users\hp\Desktop\SafeVision-project"
$out  = Join-Path $root "PROJECT_SNAPSHOT.txt"
$exts = "*.py","*.jsx","*.js","*.json","*.txt","*.md",".env.example"
$bad  = '\\venv\\|\\node_modules\\|\\__pycache__\\|\\datasets\\|\\evidence\\|\\videos\\|\\models\\|\\.git\\|\\dist\\|\\build\\|\\notebooks\\|PROJECT_SNAPSHOT|package-lock'

$files = Get-ChildItem -Path $root -Recurse -File -Include $exts |
         Where-Object { $_.FullName -notmatch $bad } |
         Sort-Object FullName

$sb = [System.Text.StringBuilder]::new()
foreach ($f in $files) {
    $rel = $f.FullName.Substring($root.Length + 1)
    [void]$sb.AppendLine("===== FILE: $rel =====")
    [void]$sb.AppendLine((Get-Content -Path $f.FullName -Raw -Encoding UTF8))
    [void]$sb.AppendLine("")
}
[System.IO.File]::WriteAllText($out, $sb.ToString(), [System.Text.Encoding]::UTF8)
Write-Host "DONE: $($files.Count) files -> $out"