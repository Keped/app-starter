# Starter

CLI to launch apps from a JSON config. Select an app with arrow keys, run it in the correct directory.

## Installation

```bash
bash install.sh
```

Then run `source ~/.zshrc` or open a new terminal. The `sd` alias will launch the app selector.

## Usage

```bash
sd
```

Or run directly:

```bash
python3 run_app.py
```

Use arrow keys to select an app, Enter to run. Select Exit to quit.

## apps.json

Add app definitions in `apps.json`, for example:

```json
[
  {"name": "Front", "directory": "path-to-front", "command": "pnpm nx serve my-front-app"},
  {"name": "Server", "directory": "path-to-back", "command": "npm run serve:api"}
]
```

Each entry: `name`, `directory`, `command`.

### Directory resolution

- Absolute paths — used as-is
- Relative paths — resolved from current directory

## Requirements

- Python 3
- pip
