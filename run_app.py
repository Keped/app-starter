#!/usr/bin/env python3
"""CLI to load apps.json, select an app, and run its command in the app directory."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import questionary
from questionary.prompts.common import Separator


def resolve_directory(raw: str) -> Path:
    var_ref = f"${raw[1:]}" if raw.startswith("~") and len(raw) > 1 else raw
    expanded = os.path.expandvars(var_ref)
    if raw.startswith("~") and (expanded == var_ref or not expanded):
        expanded = os.environ.get("DEVELOPMENT")
        if not expanded:
            raise ValueError(
                f"~{raw[1:]} is not set. Set {raw[1:]} or DEVELOPMENT env var."
            )
    elif raw.startswith("$") and len(raw) > 1 and (expanded == var_ref or not expanded):
        expanded = raw[1:]
    return Path(os.path.expanduser(expanded)).resolve()


def load_apps(apps_path: Path) -> list[dict]:
    if not apps_path.exists():
        apps_path.touch()
        return []
    with open(apps_path, encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        return []
    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("apps.json must contain a JSON array")
    for i, app in enumerate(data):
        if not isinstance(app, dict) or "name" not in app or "directory" not in app or "command" not in app:
            raise ValueError(f"App at index {i} must have 'name', 'directory', and 'command'")
    return data


def save_apps(apps_path: Path, apps: list[dict]) -> None:
    with open(apps_path, "w", encoding="utf-8") as f:
        json.dump(apps, f, indent=2)


def clear_screen() -> None:
    print("\033[2J\033[H", end="", flush=True)


_ADD_APP = object()
_REMOVE_APP = object()
_EXIT = object()


_MENU_STYLE = questionary.Style([
    ("action", "italic dim"),
])

def prompt_selection(apps: list[dict]) -> Optional[dict]:
    choices = [
        questionary.Choice(title=app["name"], value=app) for app in apps
    ] + [
        Separator(),
        questionary.Choice(title=[("class:action", "Add An App")], value=_ADD_APP),
        questionary.Choice(
            title=[("class:action", "Remove App")],
            value=_REMOVE_APP,
            disabled="No apps to remove" if not apps else None,
        ),
        questionary.Choice(title=[("class:action", "Exit")], value=_EXIT),
    ]
    result = questionary.select(
        "Select an app to run:",
        choices=choices,
        style=_MENU_STYLE,
    ).ask()
    if result is _EXIT:
        return None
    if result is _ADD_APP:
        return _ADD_APP
    if result is _REMOVE_APP:
        return _REMOVE_APP
    return result


def add_app(apps_path: Path, apps: list[dict]) -> list[dict]:
    name = questionary.text("App name:").ask()
    if not name or not name.strip():
        return apps
    name = name.strip()
    existing_names = {a["name"] for a in apps}
    if name in existing_names:
        print(f"Error: App named '{name}' already exists.", file=sys.stderr)
        return apps
    print(f"  ✔ Name: {name}")

    directory = questionary.text("Directory (e.g. ~FRONT or /path/to/project):").ask()
    if not directory or not directory.strip():
        return apps
    directory = directory.strip()
    try:
        work_dir = resolve_directory(directory)
        if not work_dir.exists():
            print(f"Error: Directory does not exist: {work_dir}", file=sys.stderr)
            return apps
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return apps
    print(f"  ✔ Directory: {directory}")

    command = questionary.text("Command (e.g. pnpm nx serve client-investor):").ask()
    if not command or not command.strip():
        return apps
    command = command.strip()
    print(f"  ✔ Command: {command}")

    new_app = {"name": name, "directory": directory, "command": command}
    updated = apps + [new_app]
    save_apps(apps_path, updated)
    print(f"  ✔ Added '{name}'.")
    return updated


def remove_app(apps_path: Path, apps: list[dict]) -> list[dict]:
    if not apps:
        return apps
    choices = [
        questionary.Choice(title=app["name"], value=app) for app in apps
    ] + [
        Separator(),
        questionary.Choice(title=[("class:action", "Cancel")], value=None),
    ]
    to_remove = questionary.select(
        "Select app to remove:",
        choices=choices,
        style=_MENU_STYLE,
    ).ask()
    if to_remove is None:
        return apps
    if not questionary.confirm(
        f"Are you sure you want to remove '{to_remove['name']}'?",
        default=False,
    ).ask():
        return apps
    updated = [a for a in apps if a != to_remove]
    save_apps(apps_path, updated)
    print(f"Removed '{to_remove['name']}'.")
    return updated


def main() -> int:
    apps_path = Path(__file__).resolve().parent / "apps.json"
    apps = load_apps(apps_path)

    while True:
        clear_screen()
        selected = prompt_selection(apps)
        if selected is None:
            clear_screen()
            return 0
        if selected is _ADD_APP:
            apps = add_app(apps_path, apps)
            continue
        if selected is _REMOVE_APP:
            apps = remove_app(apps_path, apps)
            continue

        work_dir = resolve_directory(selected["directory"])
        if not work_dir.exists():
            print(f"Error: Directory does not exist: {work_dir}", file=sys.stderr)
            return 1

        raw_cmd = selected["command"]
        print(f"\nRunning: {raw_cmd}")
        print(f"Working directory: {work_dir}\n")

        script_path = Path(__file__).resolve().parent / "run_app.sh"
        return subprocess.run(
            ["bash", str(script_path), str(work_dir), raw_cmd],
        ).returncode


if __name__ == "__main__":
    sys.exit(main())
