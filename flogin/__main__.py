import argparse
import importlib
import importlib.metadata
import json
import platform
import sys
import uuid
from pathlib import Path

from . import version_info


def show_version() -> None:
    entries = []

    entries.append(
        "- Python v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}".format(
            sys.version_info
        )
    )

    entries.append(
        "- flogin v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}".format(version_info)
    )

    try:
        version = importlib.metadata.version("flogin")
        if version:
            entries.append(f"    - flogin metadata: v{version}")
    except importlib.metadata.PackageNotFoundError:
        pass

    uname = platform.uname()
    entries.append("- system info: {0.system} {0.release} {0.version}".format(uname))
    print("\n".join(entries))


def core(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.version:
        show_version()
    else:
        parser.print_help()


_settings_template = """
body:
  - type: textBlock
    attributes:
      description: Welcome to the settings page for my plugin. Here you can configure the plugin to your liking.
  - type: input
    attributes:
      name: user_name
      label: How should I call you?
      defaultValue: the user
  - type: textarea
    attributes:
      name: prepend_result
      label: Text to prepend to result output
      description: >
        This text will be added to the beginning of the result output. For example, if you set this to 
        "The result is: ", and the result is "42", the output will be "The result is: 42". 
  - type: dropdown
    attributes:
      name: programming_language
      label: Programming language to prefer for answers
      defaultValue: TypeScript
      options:
        - JavaScript
        - TypeScript
        - Python
        - "C#"
  - type: checkbox
    attributes:
      name: prefer_shorter_aswers
      label: Prefer shorter answers
      description: If checked, the plugin will try to give answer much shorter than the usual ones.
      defaultValue: false
"""
_gh_bug_report_issue_template = """
name: Bug Report
description: Report broken or incorrect behaviour
labels: unconfirmed bug
body:
    - type: markdown
        attributes:
        value: >
            Thanks for taking the time to fill out a bug.

            Please note that this form is for bugs only!
    - type: input
        attributes:
            label: Summary
            description: A simple summary of your bug report
        validations:
            required: true
    - type: textarea
        attributes:
            label: Reproduction Steps
            description: >
                What you did to make it happen.
        validations:
            required: true
    - type: textarea
        attributes:
            label: Minimal Reproducible Code
            description: >
                A short snippet of code that showcases the bug.
        render: python
    - type: textarea
        attributes:
            label: Expected Results
            description: >
                What did you expect to happen?
        validations:
            required: true
    - type: textarea
        attributes:
            label: Actual Results
            description: >
                What actually happened?
        validations:
            required: true
    - type: textarea
        attributes:
            label: Flow Launcher Version
            description: Go into your flow launcher settings, go into the about section, and the version should be at the top.
        validations:
            required: true
    - type: textarea
        attributes:
            label: Python Version/Path
            description: Go into your flow launcher settings, go to the general section, and scroll down until you find the `Python Path` field. Copy and paste the value here.
        validations:
            required: true
    - type: textarea
        attributes:
            label: If applicable, Flow Launcher Log File
            description: Use the `Open Log Location` command with the `System Commands` plugin to open the log file folder, and upload the newest file here.
    - type: textarea
        attributes:
            label: Flogin Log File
            description: Use the `Flow Launcher UserData Folder` command with the `System Commands` plugin to open your userdata folder, go into the `Plugins` folder, then find the plugin and go into it. If the `flogin.log` file exists, upload it here. Otherwise please state that it was not there.
    - type: checkboxes
        attributes:
            label: Checklist
            description: >
                Let's make sure you've properly done due diligence when reporting this issue!
            options:
                - label: I have searched the open issues for duplicates.
                required: true
                - label: I have shown the entire traceback, if possible.
                required: true
                - label: I have removed my token from display, if visible.
                required: true
    - type: textarea
        attributes:
            label: Additional Context
            description: If there is anything else to say, please do so here.
"""
_gh_pr_template = """
## Summary

<!-- What is this pull request for? Does it fix any issues? -->

## Checklist

<!-- Put an x inside [ ] to check it, like so: [x] -->

- [ ] If code changes were made then they have been tested.
    - [ ] I have updated the documentation to reflect the changes.
- [ ] This PR fixes an issue.
- [ ] This PR adds something new (e.g. new method or parameters).
- [ ] This PR is a breaking change (e.g. methods or parameters removed/renamed)
- [ ] This PR is **not** a code change (e.g. documentation, README, ...)
"""
_gh_publish_workflow = """
name: Publish and Release

on:
  workflow_dispatch:

jobs:
  publish:
    runs-on: ubuntu-latest
    env:
      python_ver: 3.11
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python ${{ env.python_ver }}
        uses: actions/setup-python@v2
        with:
          python-version: ${{ env.python_ver }}

      - name: get version
        id: version
        uses: notiz-dev/github-action-json-property@release
        with: 
          path: 'plugin.json'
          prop_path: 'Version'

      - run: echo ${{steps.version.outputs.prop}} 

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r ./requirements.txt -t ./lib
          zip -r ${{ github.event.repository.name }}.zip . -x '*.git*'

      - name: Publish
        if: success()
        uses: softprops/action-gh-release@v2
        with:
          files: '${{ github.event.repository.name }}.zip'
          tag_name: "v${{steps.version.outputs.prop}}"
"""
_plugin_dot_py_template = """
from flogin import Plugin

from .handlers.root import RootHandler
from .settings import {plugin}Settings


class {plugin}Plugin(Plugin[{plugin}Settings]):
    def __init__(self) -> None:
        super().__init__()

        self.register_search_handler(RootHandler())
"""
_plugin_dot_py_template_no_settings = """
from flogin import Plugin

from .handlers.root import RootHandler


class {plugin}Plugin(Plugin):
    def __init__(self) -> None:
        super().__init__()

        self.register_search_handler(RootHandler())
"""
_settings_dot_py_template = """
from flogin import Settings


class {plugin}Settings(Settings):
    ...
"""
_handler_template = """
from __future__ import annotations

from typing import TYPE_CHECKING

from flogin import Query, Result, SearchHandler

if TYPE_CHECKING:
    from ..plugin import {plugin}Plugin


class {name}Handler(SearchHandler["{plugin}Plugin"]):
    def condition(self, query: Query) -> bool:
        return True

    async def callback(self, query: Query):
        return "Hello World!"
"""
_main_py_template = """
import os
import sys

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "venv", "lib", "site-packages"))

from plugin.plugin import {plugin}Plugin

if __name__ == "__main__":
    {plugin}Plugin().run()
"""


def create_plugin_dot_json_file(
    parser: argparse.ArgumentParser, plugin_name: str
) -> None:
    data = {
        "ID": str(uuid.uuid4()),
        "ActionKeyword": "*",
        "Name": plugin_name,
        "Description": "",
        "Author": "",
        "Version": "0.0.1",
        "Language": "python_v2",
        "Website": "https://github.com/author/Flow.Launcher.Plugin.Name",
        "IcoPath": "Images/app.png",
        "ExecuteFileName": "main.py",
    }
    write_to_file(Path("plugin.json"), json.dumps(data, indent=4), parser)


def write_to_file(path: Path, content: str, parser: argparse.ArgumentParser) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with path.open("w") as f:
            f.write(content.strip())
    except OSError as e:
        parser.error(f"Unable to write to {path}: {e}")
        return False
    else:
        print(f"Wrote to {path}")
    return True


def create_new_handler(
    parser: argparse.ArgumentParser, *, path: Path, name: str, plugin: str
):
    write_to_file(path, _handler_template.format(plugin=plugin, name=name), parser)


def create_plugin_directory(parser: argparse.ArgumentParser, args: argparse.Namespace):
    plugin_dir = Path("plugin")
    plugin_name = args.plugin_name

    main_file = Path("main.py")

    write_to_file(main_file, _main_py_template.format(plugin=plugin_name), parser)

    plugin_file = plugin_dir / "plugin.py"
    template = (
        _plugin_dot_py_template_no_settings
        if args.no_settings
        else _plugin_dot_py_template
    )
    write_to_file(plugin_file, template.format(plugin=plugin_name), parser)

    if not args.no_settings:
        settings_file = plugin_dir / "settings.py"
        write_to_file(
            settings_file, _settings_dot_py_template.format(plugin=plugin_name), parser
        )

    handlers_dir = plugin_dir / "handlers"
    root_handler_file = handlers_dir / "root.py"

    create_new_handler(parser, path=root_handler_file, name="Root", plugin=plugin_name)


def create_git_files(parser: argparse.ArgumentParser, args: argparse.Namespace):
    github_dir = Path(".github")
    issue_template_dir = github_dir / "ISSUE_TEMPLATE"
    workflows_dir = github_dir / "workflows"

    bug_report_template_file = issue_template_dir / "bug_report.yml"
    write_to_file(bug_report_template_file, _gh_bug_report_issue_template, parser)

    pr_template_file = github_dir / "PULL_REQUEST_TEMPLATE.md"
    write_to_file(pr_template_file, _gh_pr_template, parser)

    publish_file = workflows_dir / "publish_release.yml"
    write_to_file(publish_file, _gh_publish_workflow, parser)


def init_command(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    plugin_name = args.plugin_name

    if not args.no_manifest:
        create_plugin_dot_json_file(parser, plugin_name)

    if not args.no_settings:
        settings_file = Path("SettingsTemplate.yaml")
        write_to_file(settings_file, _settings_template, parser)

    if not args.no_git:
        create_git_files(parser, args)

    if not args.no_plugin:
        create_plugin_directory(parser, args)


def add_init_args(subparser: argparse._SubParsersAction) -> None:
    parser = subparser.add_parser(
        "init",
        help="quickly sets up the environment for the development of a new plugin",
    )
    parser.set_defaults(func=init_command)

    parser.add_argument("plugin_name", help="the name of the plugin")
    parser.add_argument(
        "--no-git", help="whether or not to add git files", action="store_true"
    )
    parser.add_argument(
        "--no-settings", help="whether or not to add setting files", action="store_true"
    )
    parser.add_argument(
        "--no-plugin", help="Do not create an example plugin", action="store_true"
    )
    parser.add_argument(
        "--no-manifest",
        help="Do not create a plugin.json manifest file",
        action="store_true",
    )


def add_new_handler_command(
    parser: argparse.ArgumentParser, args: argparse.Namespace
) -> None:
    plugin_name: str = args.plugin_name or ""
    handler_name: str = args.name
    dir = Path("plugin") / (args.dir or "handlers")
    path = dir / handler_name.lower()

    classname = handler_name.replace("_", " ").title().replace(" ", "")

    create_new_handler(
        parser, path=path.with_suffix(".py"), name=classname, plugin=plugin_name
    )


def add_handler_command_args(subparser: argparse._SubParsersAction) -> None:
    parser = subparser.add_parser(
        "new-handler",
        help="quickly set up a new handler using flogin's handler template.",
    )
    parser.set_defaults(func=add_new_handler_command)

    parser.add_argument(
        "name", help="the name of the handler in case snake format. ex: 'root'"
    )
    parser.add_argument("--plugin-name", help="Sets the plugin name for importing")
    parser.add_argument("--dir", help="The handlers dir. Defaults to 'handlers'")


def parse_args() -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser(
        prog="flogin", description="Tools for helping with plugin development"
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="shows the library version"
    )
    parser.set_defaults(func=core)

    subparser = parser.add_subparsers(dest="subcommand", title="subcommands")
    add_init_args(subparser)
    add_handler_command_args(subparser)
    return parser, parser.parse_args()


def main() -> None:
    parser, args = parse_args()
    args.func(parser, args)


if __name__ == "__main__":
    main()
