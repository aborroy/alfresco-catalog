# Alfresco Marketplace (Beta)

A zero-infrastructure, community-driven catalog of third‑party solutions for Alfresco.
Built with **Hugo + GitHub Pages**, moderated via Pull Requests, with **client‑side search (Fuse.js)**.

## Quick start
- Add a listing: open an Issue "Submit a marketplace entry" or send a PR with a file under `content/entries/`.
- Preview: every PR builds a preview; reviewers and authors get a link.
- Search: instant search + filters (compatibility, license, keywords) on the homepage.
- Analytics: GA4/Plausible ready (enable in `layouts/partials/analytics.html`).

## Structure
```
.
├─ .github/
│  ├─ ISSUE_TEMPLATE/
│  │  └─ submission.yml
│  ├─ workflows/
│  │  ├─ validate-and-build.yml
│  │  └─ pr-from-issue.yml
│  └─ CODEOWNERS
├─ archetypes/
│  └─ entry.md
├─ assets/css/brand.css
├─ content/entries/sample-solution.md
├─ data/licenses.yaml
├─ layouts/
│  ├─ _default/list.html
│  ├─ _default/single.html
│  ├─ index.json.json
│  └─ partials/{search.html,analytics.html,card.html,facets.html,head.html}
├─ schema/entry.schema.json
├─ scripts/{validate-frontmatter.mjs, make-entry-from-issue.mjs}
├─ static/uploads/
├─ config.toml
└─ hugo.toml (alias of config.toml for newer Hugo)
```

## Local build
```bash
# Requires Hugo (extended)
hugo server -D
```

## Content model
See `archetypes/entry.md` and `schema/entry.schema.json`.
