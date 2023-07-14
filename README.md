# Github Workflow Action: Changesets Changelog Info

![Version](https://img.shields.io/badge/latest-v0.0.4-blue)

## Overview

[The Changesets workflow](https://github.com/changesets/changesets#readme) is a
useful way to manage a project's CHANGELOG file.

Unfortunately, it _does_ not\* follow the [_Keep a
Changelog_](https://github.com/olivierlacan/keep-a-changelog#readme) standard

This action was written to grab the release notes
**for the most recent version**
in the CHANGELOG.md file for the project.

If the need arises, the functionality may be extended.

## Action Parameters

### Inputs

#### `changelog`

> Path to the Changesets formatted CHANGELOG.md

| Option   | Details        |
| -------- | -------------- |
| default  | `CHANGELOG.md` |
| required | `true`         |

#### `version` (**UNUSED** - this option currently has no effect)

> The version to release

| Option   | Details  |
| -------- | -------- |
| default  | `latest` |
| required | `true`   |

## Usage

### Action Step

In your workflow add the following you can usually use it out of the box with
no parameters. It will derive the information from `CHANGELOG.md` for the most
recent (top of file) version.

```yaml
- name: Get Changelog Entry
  id: get-changelog-entry
  uses: chizmw/changesets-changelog-info@v0.0.4
```

If your change file is in a non-standard location:

```yaml
- name: Get Changelog Entry
  id: get-changelog-entry
  uses: chizmw/changesets-changelog-info@v0.0.4
  with:
    changelog: path-to/my-change-file.md
```

### As Part Of A Release Workflow

Create `.github/workflows/github-release.yml` in your project with the
following content:

```yaml
---
name: Github Release

# yamllint disable-line rule:truthy
on:
  push:
    tags:
      - v*

permissions:
  contents: write

jobs:
  create-release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Get Change Info
        id: get-changelog-entry
        uses: chizmw/changesets-changelog-info@v0.0.4

      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: ${{ github.ref }}
          draft: false
          prerelease: false
          body: ${{ steps.get-changelog-entry.outputs.last-change-entry }}
```

**NOTE:** using a `v*` tag as a release trigger requires some additions to your
`changeset-release.yml` (or equivalent) workflow, to push the tags back to the
repo.

Add the following after your `changesets/action` step:

```yaml
- name: Push Tags
  # https://github.com/changesets/action#custom-publishing
  if: steps.changesets.outputs.hasChangesets == 'false'
  shell: bash
  run: |
    version="$(cat package.json | jq -r '.version')"
    git tag "v$version"
    git push --tags
```

For an example of a Changeset Release workflow file you can view
[.github/workflows/changeset-release.yml](.github/workflows/changeset-release.yml)
