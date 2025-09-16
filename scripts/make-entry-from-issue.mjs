import fs from 'node:fs';
import path from 'node:path';
import { Octokit } from 'octokit';

const issueNumber = process.env.ISSUE_NUMBER;
const token = process.env.GITHUB_TOKEN;
const [owner, repo] = process.env.GITHUB_REPOSITORY.split('/');

const octokit = new Octokit({ auth: token });
const { data: issue } = await octokit.rest.issues.get({ owner, repo, issue_number: Number(issueNumber) });

// --- Parse helpers ---------------------------------------------------------

// Parse "### Heading" blocks from issue.body into { heading -> value }
function parseFormSections(text) {
  const body = (text || '') + '\n### END';
  const re = /(?:^|\n)###\s+([^\n]+)\n+([\s\S]*?)(?=\n###|\n?$)/g;
  const map = new Map();
  let m;
  while ((m = re.exec(body))) {
    const key = m[1].trim().toLowerCase();            // e.g., "title", "name", "description"
    const val = m[2].trim();
    if (!map.has(key)) map.set(key, val);
  }
  return map;
}

// Normalize a comma/list field; also supports checklist or one-per-line lists
function parseList(s) {
  if (!s) return [];
  const lines = s
    .split(/\r?\n/)
    .map(l => l.replace(/^- \[.\]\s*/, '').trim())     // checkbox lines
    .filter(Boolean);
  const joined = lines.join(',');                      // allow both forms
  return joined.split(',').map(x => x.trim()).filter(Boolean);
}

// Extract Markdown image URLs for screenshots
function parseScreenshots(text) {
  if (!text) return [];
  const urls = [];
  const imgRe = /!\[[^\]]*\]\(([^)]+)\)/g;            // ![alt](url)
  let m;
  while ((m = imgRe.exec(text))) urls.push(m[1]);
  return urls.slice(0, 4);
}

// Slugify
function slugify(s) {
  return (s || 'entry')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

// --- Extract fields from issue --------------------------------------------

const sections = parseFormSections(issue.body || '');

// flexible getters: try several aliases/labels
function getField(...aliases) {
  for (const a of aliases) {
    const v = sections.get(a.toLowerCase());
    if (v) return v.trim();
  }
  return '';
}

const title        = getField('title', 'name') || issue.title || 'Untitled';
const description  = getField('description', 'short description', 'summary');
const downloadUrl  = getField('download_url', 'download url', 'repo url', 'link');
const vendor       = getField('vendor', 'author', 'company') || 'Unknown';
const about        = (getField('about', 'short pitch') || '').slice(0, 300);
const aboutUrl     = getField('about_url', 'about url', 'website');
const license      = getField('license', 'licence') || 'Proprietary';
const keywords     = parseList(getField('keywords', 'tags'));
const compatibility= parseList(getField('compatibility', 'versions', 'alfresco versions'));

// screenshots: from a dedicated field OR scrape images from the whole body
let screenshots    = parseList(getField('screenshots'));
if (!screenshots.length) screenshots = parseScreenshots(issue.body || '');

const slug = slugify(title);

// --- Write content file ----------------------------------------------------

const fm = {
  title,
  description,
  screenshots,
  compatibility,
  license,
  keywords,
  download_url: downloadUrl,
  vendor,
  about,
  about_url: aboutUrl,
  draft: false,
};

const outDir = path.join('content', 'entries');
fs.mkdirSync(outDir, { recursive: true });

const filePath = path.join(outDir, `${slug}-${issue.number}.md`);
const frontMatter = `---\n${Object.entries(fm).map(([k,v]) => {
  if (Array.isArray(v)) return `${k}: ${JSON.stringify(v)}`;
  return `${k}: ${v === null || v === undefined ? '""' : JSON.stringify(v)}`;
}).join('\n')}\n---\n\n`;

fs.writeFileSync(filePath, frontMatter, 'utf8');
console.log(`Created ${filePath}`);
