# Build output/docx/paper.docx, then export output/pdf/paper.pdf with Microsoft Word.
# Run from anywhere: pwsh paper/build.ps1
$repo = Split-Path -Parent $PSScriptRoot
$docx = Join-Path $repo "output\docx\paper.docx"
$pdf = Join-Path $repo "output\pdf\paper.pdf"
New-Item -ItemType Directory -Force (Split-Path $docx), (Split-Path $pdf) | Out-Null

node (Join-Path $PSScriptRoot "build_paper.js") $docx
if ($LASTEXITCODE -ne 0) { exit 1 }

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docx, $false, $true)
    $doc.ExportAsFixedFormat($pdf, 17)  # 17 = PDF
    $doc.Close($false)
} finally {
    $word.Quit()
}
Write-Output "wrote $pdf"
