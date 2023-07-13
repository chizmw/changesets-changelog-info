import os
import sys


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
                changes = {
                    "patch_changes": [],
                    "minor_changes": [],
                    "major_changes": [],
                }
        elif line.startswith("### "):
            current_section = line.replace("### ", "").lower().replace(" ", "_")
        elif version and line.startswith("-") and current_section:
            changes[current_section].append(line.replace("- ", ""))

    return {"version": version, "changes": changes}


# read CHANGELOG.md and save in changelog_text
with open("CHANGELOG.md", "r", encoding="utf-8") as f:
    changelog_text = f.read()

parsed_info = parse_changelog(changelog_text)

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
