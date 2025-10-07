# Alfresco Catalog 

![Status](https://img.shields.io/badge/status-DEVELOPMENT-orange?style=flat-square) [![License](https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square)](LICENSE) [![Built with Hugo](https://img.shields.io/badge/built%20with-Hugo-ff4088?style=flat-square\&logo=hugo)](https://gohugo.io/) [![GitHub Pages](https://img.shields.io/badge/deployed%20on-GitHub%20Pages-24292e?style=flat-square\&logo=github)](https://aborroy.github.io/alfresco-catalog/) [![Build](https://github.com/aborroy/alfresco-catalog/actions/workflows/validate-and-build.yml/badge.svg)](https://github.com/aborroy/alfresco-catalog/actions/workflows/validate-and-build.yml)

> **Project in Active Development**
>
> The Alfresco Catalog is currently under migration to the **[AlfrescoLabs](https://github.com/AlfrescoLabs)** organization.
> During this phase, **external contributions are paused** until the new location is live.
> You can still explore the project, structure, and build locally.

## Overview

The **Alfresco Catalog** is a **community-driven showcase** of add-ons, integrations, and tools built for the Alfresco ecosystem.
It’s entirely static, runs on **Hugo + GitHub Pages**, and enables **zero-infrastructure publishing** of third-party solutions.

**Live site (development):** [https://aborroy.github.io/alfresco-catalog/](https://aborroy.github.io/alfresco-catalog/)

Key features:

* Community-contributed extensions and solutions
* Instant client-side search (Fuse.js)
* Automated validation through JSON Schema (AJV)
* Zero server infrastructure — built and deployed from GitHub Actions
* Optional analytics and weekly traffic reports

## Project Structure

```
.
├─ .github/
│  ├─ ISSUE_TEMPLATE/            # Catalog submission form
│  ├─ workflows/                 # CI/CD workflows
│  │  ├─ validate-and-build.yml  # Validate entries + build Hugo site
│  │  ├─ pr-from-issue.yml       # Convert issues into PRs automatically
│  │  └─ collect-stats.yml       # Collect weekly traffic analytics
│  └─ CODEOWNERS
├─ archetypes/entry.md           # Template for new catalog entries
├─ content/entries/              # Markdown entries for each add-on
├─ data/licenses.yaml            # Reference list of accepted licenses
├─ layouts/partials/             # Hugo partials (cards, search, facets)
├─ schema/entry.schema.json      # JSON Schema used for validation
├─ scripts/                      # Node.js utilities for CI validation
│  ├─ validate-frontmatter.mjs
│  └─ make-entry-from-issue.mjs
├─ reports/                      # Generated weekly traffic stats
├─ static/uploads/               # Logos and screenshots
├─ hugo.toml                     # Hugo site configuration
├─ run.sh                        # Docker helper for local builds
└─ LICENSE                       # Apache 2.0 License
```

## Local Development

You can preview and test the catalog locally using Hugo.

### Option 1: Native Hugo

```bash
# Install Hugo (extended version)
hugo server -D
```

Then open [http://localhost:1313](http://localhost:1313).

### Option 2: Docker (Recommended)

```bash
./run.sh
```

This uses the official `klakegg/hugo:ext` container to run a consistent environment.

## Adding New Entries (Temporarily Disabled)

While the catalog is in **development mode**, new submissions are paused.
Once migrated to [AlfrescoLabs](https://github.com/AlfrescoLabs), contributions will be re-enabled through Issues and PRs.

For reference, the normal submission flow is:

1. **Submit an Issue** using the “Submit a catalog entry” template
2. A GitHub Action automatically generates a Pull Request
3. Schema validation ensures metadata compliance
4. Approved entries are automatically published

## Validation Rules

All entries are validated against [`schema/entry.schema.json`](schema/entry.schema.json) using **AJV**.
You can test locally (optional):

```bash
npm install
node scripts/validate-frontmatter.mjs
```

## Traffic & Analytics

The repository includes a GitHub Action that collects traffic data via the **GitHub REST API**:

* Runs **every Sunday at midnight (UTC)**
* Stores data as JSON and CSV in `/reports/`
* Requires a **fine-grained PAT** with `traffic:read` permission
* Token name: `TRAFFIC_STATS_TOKEN`

To set it up:

```text
Settings → Secrets → Actions → New repository secret
Name: TRAFFIC_STATS_TOKEN
Value: <your fine-grained token>
```

## License

Licensed under the **Apache License 2.0**.
See the [LICENSE](LICENSE) file for details.

## Contributing

> Temporarily closed for contributions while migrating to [AlfrescoLabs](https://github.com/AlfrescoLabs).

Once open again:

* Follow [CONTENT_POLICY.md](CONTENT_POLICY.md) and [TAKEDOWN.md](TAKEDOWN.md)
* Each PR undergoes automatic schema validation and manual review
* Accepted submissions appear in the public catalog automatically