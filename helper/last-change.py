import argparse
import os
import sys

ACTION_DEBUG: bool = len(os.environ.get("CHANGESET_INFO_DEBUG", "")) > 0
args: argparse.Namespace


def gh_debug(args, **kwargs):
    if ACTION_DEBUG:
        print(f"::info::{args}", **kwargs)


def parse_changelog(changelog):
    lines = changelog.split("\n")
    version = None
    changes = {}
    current_section = None

    for line in lines:
        line = line.strip()

        if line.startswith("## "):
            if version:
                break
            else:
                version = line.replace("## ", "")
                gh_debug(f"found version: {version}")
                changes = {
                    "patch_changes": [],
                    "minor_changes": [],
                    "major_changes": [],
                }
        elif line.startswith("### "):
            current_section = line.replace("### ", "").lower().replace(" ", "_")
            gh_debug(f"found section: {current_section}")
        elif version and line.startswith("-") and current_section:
            line = line.replace("- ", "")
            changes[current_section].append(line)
            gh_debug(f"found '{current_section}' change: {line}")

    return {"version": version, "changes": changes}


def build_markdown_block(parsed_info: dict) -> str:
    # build a string with the changes
    markdown_block = ""
    if parsed_info["changes"]["patch_changes"]:
        markdown_block += "### Patch Changes\n"
        for change in parsed_info["changes"]["patch_changes"]:
            markdown_block += f"- {change}\n"
    if parsed_info["changes"]["minor_changes"]:
        markdown_block += "\nMinor Changes:\n"
        for change in parsed_info["changes"]["minor_changes"]:
            markdown_block += f"- {change}\n"
    if parsed_info["changes"]["major_changes"]:
        markdown_block += "\nMajor Changes:\n"
        for change in parsed_info["changes"]["major_changes"]:
            markdown_block += f"- {change}\n"

    return markdown_block


def output_markdown_block(markdown_block: str) -> None:
    # if we have an env variable named GITHUB_OUTPUT, we are running in github
    # actions and should use that as a file to append to, othwerwise just print to
    # stdout
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            # we know it's likely to be multiline, so we need to use a little magic
            # that we found in https://github.com/github/docs/issues/21529
            f.write("changeentry<<EOF\n")
            f.write(f"{markdown_block}\n")
            f.write("EOF\n")
    else:
        sys.stdout.write(f"[set-output] changeentry:\n{markdown_block}")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="Change Entry Info",
        description="helper for chizmw/changesets-changelog-info",
    )

    parser.add_argument(
        "--changelog",
        type=str,
        default="CHANGELOG.md",
        help="Path to CHANGELOG.md file",
    )

    parser.add_argument(
        "--get-version",
        type=str,
        default="latest",
        help="get information about a specific version",
    )

    args = parser.parse_args()
    return args


def main():
    # read CHANGELOG.md and save in changelog_text
    gh_debug(f"reading {args.changelog}")
    with open(args.changelog, "r", encoding="utf-8") as f:
        changelog_text = f.read()

    parsed_info = parse_changelog(changelog_text)
    markdown_block = build_markdown_block(parsed_info)
    output_markdown_block(markdown_block)


if __name__ == "__main__":
    args = parse_args()
    main()
