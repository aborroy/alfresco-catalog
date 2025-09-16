import fs from 'node:fs';
import path from 'node:path';
import { Octokit } from 'octokit';

const issueNumber = Number(process.env.ISSUE_NUMBER);
const token = process.env.GITHUB_TOKEN;
const [owner, repo] = process.env.GITHUB_REPOSITORY.split('/');

const octokit = new Octokit({ auth: token });
const { data: issue } = await octokit.rest.issues.get({ owner, repo, issue_number: issueNumber });

// ---- helpers --------------------------------------------------------------

const norm = (s='') =>
  s.toLowerCase()
   .replace(/\(.*?\)/g, '')          // drop parenthetical notes, e.g. " (URL)"
   .replace(/[^a-z0-9]+/g, ' ')      // remove punctuation
   .trim();

function parseSections(text='') {
  const src = text + '\n### END';
  const re = /(?:^|\n)###\s+([^\n]+)\n+([\s\S]*?)(?=\n###|\n?$)/g;
  const items = [];
  let m;
  while ((m = re.exec(src))) {
    items.push({ raw: m[1].trim(), key: norm(m[1]), value: m[2].trim() });
  }
  return items;
}

function getField(sections, ...aliases) {
  const targets = aliases.map(norm);
  for (const t of targets) {
    // exact key
    const exact = sections.find(s => s.key === t);
    if (exact) return exact.value.trim();
    // substring match (handles "download page link" vs "download url")
    const sub = sections.find(s => s.key.includes(t));
    if (sub) return sub.value.trim();
  }
  return '';
}

function parseList(s) {
  if (!s) return [];
  const lines = s
    .split(/\r?\n/)
    .map(l => l.replace(/^- \[.\]\s*/, '').trim())
    .filter(Boolean);
  return lines.join(',').split(',').map(x => x.trim()).filter(Boolean);
}

function parseScreenshots(body='') {
  const urls = [];
  const imgRe = /!\[[^\]]*\]\(([^)]+)\)/g;
  let m;
  while ((m = imgRe.exec(body))) urls.push(m[1]);
  return urls.slice(0, 4);
}

const slugify = (s='entry') =>
  s.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/(^-|-$)/g,'');

// ---- extract --------------------------------------------------------------

const sections = parseSections(issue.body || '');

const title        = getField(sections, 'title','name') || issue.title || 'Untitled';
const description  = getField(sections, 'description','summary','overview');

const compatibility= parseList(getField(sections, 'compatibility','versions','alfresco versions'));
const license      = getField(sections, 'license','licence') || 'Proprietary';
const keywords     = parseList(getField(sections, 'keywords','tags'));

const downloadUrl  = getField(sections, 'download url','download page link','repo url','project url','link');
const vendor       = getField(sections, 'vendor','author','author vendor name','maintainer','company') || 'Unknown';
const aboutUrl     = getField(sections, 'about url','website','homepage');
const about        = (getField(sections, 'about','short pitch') || '').slice(0, 500);

// screenshots: explicit field or pasted markdown images
let screenshots    = parseList(getField(sections, 'screenshots'));
if (!screenshots.length) screenshots = parseScreenshots(issue.body || '');

const slug = slugify(title);

// ---- write file -----------------------------------------------------------

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
  return `${k}: ${v == null ? '""' : JSON.stringify(v)}`;
}).join('\n')}\n---\n\n`;

fs.writeFileSync(filePath, frontMatter, 'utf8');
console.log(`Created ${filePath}`);
