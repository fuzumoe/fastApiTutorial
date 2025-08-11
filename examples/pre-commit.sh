#!/bin/bash
set -e  # exit immediately if a command fails

echo "🔍 Running pre-commit checks (mypy + ruff)..."

# Only check staged Python files
PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -z "$PY_FILES" ]; then
    echo "✅ No Python files staged for commit."
    exit 0
fi

# Run Ruff linter
echo "🚀 Running Ruff..."
ruff check $PY_FILES
echo "✅ Ruff passed."

# Run mypy type checks
echo "🚀 Running mypy..."
mypy $PY_FILES
echo "✅ mypy passed."

echo "🎉 All checks passed!"
