# Github Workflow Action: Changesets Changelog Info

![Version](https://img.shields.io/badge/latest-v0.1.1-blue)

## Overview

[The Changesets workflow](https://github.com/changesets/changesets#readme) is a
useful way to manage a project's CHANGELOG file.

Unfortunately, it _does_ not follow the [_Keep a
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

### Outputs

#### `last-change-entry`

The change entry for the version from the changelog.

```yaml
- name: Last Change Entry
  run: |
    echo ${{ steps.get-changelog-info.outputs.last-change-entry }}
```

#### `last-change-version`

The version number corresponding to the entry from the changelog, **without**
the `v` prefix.
This can be passed to a release action workflow (see below).

```yaml
- name: Last Change Version
  run: |
    echo ${{ steps.get-changelog-info.outputs.last-change-version }}
```

#### `last-change-version-v`

The version number corresponding to the entry from the changelog, **including**
the `v` prefix.
This can be passed to a release action workflow (see below).

```yaml
- name: Last Change Version With V
  run: |
    echo ${{ steps.get-changelog-info.outputs.last-change-version-v }}
```

## Usage

### Action Step

In your workflow add the following you can usually use it out of the box with
no parameters. It will derive the information from `CHANGELOG.md` for the most
recent (top of file) version.

```yaml
- name: Get Changelog Entry
  id: get-changelog-entry
  uses: chizmw/changesets-changelog-info@v0.1.1
```

If your change file is in a non-standard location:

```yaml
- name: Get Changelog Entry
  id: get-changelog-entry
  uses: chizmw/changesets-changelog-info@v0.1.1
  with:
    changelog: path-to/my-change-file.md
```

### As Part Of A Release Workflow

Create `.github/workflows/github-release.yml` in your project with the
following content:

<!-- markdownlint-disable MD013 -->

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
        id: get-changelog-info
        uses: chizmw/changesets-changelog-info@v0.1.1

      - name: Create Github Release
        uses: softprops/action-gh-release@v1
        # only run if we have a changelog entry
        if: steps.get-changelog-info.outputs.last-change-entry != ''
        with:
          body: ${{ steps.get-changelog-info.outputs.last-change-entry }}
          tag_name: ${{ steps.get-changelog-info.outputs.last-change-version }}
          name: ${{ steps.get-changelog-info.outputs.last-change-version }}
          draft: false
          prerelease: false
```

<!-- markdownlint-enable MD013 -->

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
    git tag ${{ steps.get-changelog-info.outputs.last-change-version }}
    # this could fail in a merge without changesets
    # (e.g. update README.md, merge)
    # but that's a bit naughty anyway, so we'll let it fail
    git push --tag
```

For an example of a Changeset Release workflow file you can view
[.github/workflows/changeset-release.yml](.github/workflows/changeset-release.yml)

## `secrets.CHANGESETS_TOKEN`

From
[Triggering a workflow from a workflow](https://docs.github.com/en/actions/using-workflows/triggering-a-workflow#triggering-a-workflow-from-a-workflow):

> When you use the repository's GITHUB_TOKEN to perform tasks, events triggered
> by the GITHUB_TOKEN will not create a new workflow run.
>
> If you do want to trigger a workflow from within a workflow run, you can use
> a GitHub App installation access token or a personal access token instead of
> GITHUB_TOKEN to trigger events that require a token.

This project uses a personal access token called `CHANGESETS_TOKEN`.
If you already have a
[personal access token](https://github.com/settings/tokens)
configured in your repo, or organization, you should replace any references to
match the name of your secret.

For your reference, `CHANGESETS_TOKEN` has been created as a _Classic Token_
with the following permissions:

- `repo`

## Further Reading

- [Changeset Flow Overview](docs/changeset-flow-overview.md)
- [Full Workflow Suggestion](docs/full-workflow-suggestion.md)
