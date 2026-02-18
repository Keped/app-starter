#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_APP_PATH="$SCRIPT_DIR/run_app.py"
ZSHRC="$HOME/.zshrc"
ALIAS_LINE="alias sd=\"python3 $RUN_APP_PATH\""

echo "Installing dependencies..."
python3 -m pip install -r "$SCRIPT_DIR/requirements.txt"

touch "$SCRIPT_DIR/apps.json"

if grep -q 'alias sd=' "$ZSHRC" 2>/dev/null; then
  echo "Alias 'sd' already exists in ~/.zshrc"
else
  echo "" >> "$ZSHRC"
  echo "# run_app launcher (added by install.sh)" >> "$ZSHRC"
  echo "$ALIAS_LINE" >> "$ZSHRC"
  echo "Added alias 'sd' to ~/.zshrc"
  echo "Installed. Run 'source ~/.zshrc' or open a new terminal to use 'sd'"
fi

echo ""
echo "Add app definitions to apps.json. Each entry needs: name, directory, command"
