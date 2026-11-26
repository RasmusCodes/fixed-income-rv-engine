# Check the JavaScript port (web/firv.js) against the Python engine.
#   1. python scripts/make_golden.py        (writes web/test/golden.js)
#   2. powershell -File scripts/run_js_selftest.ps1
# Headless Edge executes web/test/selftest.html and prints it to PDF; the first line of the
# PDF text is "SELFTEST PASS n/n" or "SELFTEST FAIL k/n". Needs pypdf in the venv.
$root = Split-Path -Parent $PSScriptRoot
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$pdf = Join-Path $env:TEMP "firv-selftest.pdf"
$profile = Join-Path $env:TEMP "firv-edge-profile"
$page = ((Join-Path $root "web\test\selftest.html") -replace '\\', '/')
if (Test-Path $pdf) { Move-Item $pdf "$pdf.old" -Force }
$p = Start-Process -FilePath $edge -ArgumentList @("--headless=new", "--disable-gpu", "--no-first-run",
  "--user-data-dir=$profile", "--virtual-time-budget=60000", "--no-pdf-header-footer", "--print-to-pdf=$pdf",
  "file:///$page") -PassThru -Wait -WindowStyle Hidden
$py = Join-Path $root ".venv\Scripts\python.exe"
& $py -c "import sys; from pypdf import PdfReader; t='\n'.join(p.extract_text() for p in PdfReader(sys.argv[1]).pages); print(t.splitlines()[0]); [print('  ', l) for l in t.splitlines() if 'FAIL' in l and not l.startswith('SELFTEST')]" $pdf
