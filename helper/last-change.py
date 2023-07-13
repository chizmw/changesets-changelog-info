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

# print to a file
with open("relinfo.md", "w", encoding="utf-8") as relinfo:
    # only if there are patch changes
    if parsed_info["changes"]["patch_changes"]:
        print("### Patch Changes\n", file=relinfo)
        for change in parsed_info["changes"]["patch_changes"]:
            print(f"- {change}", file=relinfo)

    if parsed_info["changes"]["minor_changes"]:
        print("\nMinor Changes:", file=relinfo)
        for change in parsed_info["changes"]["minor_changes"]:
            print(f"- {change}", file=relinfo)

    if parsed_info["changes"]["major_changes"]:
        print("\nMajor Changes:", file=relinfo)
        for change in parsed_info["changes"]["major_changes"]:
            print(f"- {change}", file=relinfo)

    # if there are no changes
    if (
        not parsed_info["changes"]["patch_changes"]
        and not parsed_info["changes"]["minor_changes"]
        and not parsed_info["changes"]["major_changes"]
    ):
        print(
            f"> No changes detected for version {parsed_info['version']}", file=relinfo
        )
