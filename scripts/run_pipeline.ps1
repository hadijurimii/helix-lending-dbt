param(
    [string]$ProjectRoot = (Resolve-Path ".").Path
)

python "$ProjectRoot\main.py" --project-root "$ProjectRoot"
