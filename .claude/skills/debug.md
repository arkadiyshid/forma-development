---
description: Run parser in debug mode with verbose output
---

# Debug Skill

Runs the Selenium parser with enhanced debugging output and error tracking.

## What it does

1. Checks if virtual environment is activated
2. Verifies ChromeDriver availability
3. Runs sel_parse_codex.py with verbose output
4. Captures all errors to errors.txt
5. Shows real-time progress

## Usage

```
/debug
```

## Implementation

```bash
#!/bin/bash

echo "🔍 Starting debug mode..."
echo ""

# Check venv
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Check ChromeDriver
CHROMEDRIVER_PATH="/Users/arkadijsidlovskij/Desktop/projects/PKK_FLAT_PARS/chromedriver"
if [[ ! -f "$CHROMEDRIVER_PATH" ]]; then
    echo "❌ ChromeDriver not found at: $CHROMEDRIVER_PATH"
    echo "Update CHROMEDRIVER_PATH in sel_parse_codex.py"
    exit 1
fi

echo "✅ Virtual environment: active"
echo "✅ ChromeDriver: found"
echo ""
echo "🚀 Running parser with debug output..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run with unbuffered output for real-time logs
python -u sel_parse_codex.py 2>&1 | tee -a errors.txt

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✅ Parser completed successfully"
    echo "📁 Results saved in: data/"
else
    echo "❌ Parser failed with exit code: $EXIT_CODE"
    echo "📝 Check errors.txt for details"
fi
```
