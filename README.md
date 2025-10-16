# Alfresco Addons Catalog 

![Status](https://img.shields.io/badge/status-DEVELOPMENT-orange?style=flat-square) [![License](https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square)](LICENSE) [![Built with Hugo](https://img.shields.io/badge/built%20with-Hugo-ff4088?style=flat-square\&logo=hugo)](https://gohugo.io/) [![GitHub Pages](https://img.shields.io/badge/deployed%20on-GitHub%20Pages-24292e?style=flat-square\&logo=github)](https://alfrescolabs.github.io/alfresco-addons-catalog/) [![Build](https://github.com/alfrescolabs/alfresco-addons-catalog/actions/workflows/validate-and-build.yml/badge.svg)](https://github.com/alfrescolabs/alfresco-addons-catalog/actions/workflows/validate-and-build.yml)

> **Project in Beta — Now in AlfrescoLabs**
> The **Alfresco Add-ons Catalog** is now available in the **[AlfrescoLabs](https://github.com/AlfrescoLabs)** organization.
> The project is currently in **Beta status** and **open to community contributions**.
> We welcome feedback, ideas, and pull requests as we continue shaping the catalog together.

## Overview

The **Alfresco Addons Catalog** is a **community-driven showcase** of add-ons, integrations, and tools built for the Alfresco ecosystem.
It’s entirely static, runs on **Hugo + GitHub Pages**, and enables **zero-infrastructure publishing** of third-party solutions.

**Live site (development):** [https://alfrescolabs.github.io/alfresco-addons-catalog/](https://alfrescolabs.github.io/alfresco-addons-catalog/)

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

## Adding New Entries

The catalog is now hosted in **[AlfrescoLabs](https://github.com/AlfrescoLabs)** and is in **Beta status**.
You can **submit new entries** and **propose improvements** through **Issues and Pull Requests**.
Community contributions are encouraged as we refine and expand the Alfresco Add-ons Catalog.

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

* Follow [CONTENT_POLICY.md](CONTENT_POLICY.md) and [TAKEDOWN.md](TAKEDOWN.md)
* Each PR undergoes automatic schema validation and manual review
* Accepted submissions appear in the public catalog automatically
