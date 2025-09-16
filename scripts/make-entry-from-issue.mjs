import fs from 'node:fs';
import { Octokit } from 'octokit';

const issueNumber = process.env.ISSUE_NUMBER;
const token = process.env.GITHUB_TOKEN;
const [owner, repo] = process.env.GITHUB_REPOSITORY.split('/');

const octokit = new Octokit({ auth: token });

const { data: issue } = await octokit.rest.issues.get({ owner, repo, issue_number: issueNumber });

function getField(id) {
  const m = new RegExp(`### ${id}[\s\S]*?\n\n([\s\S]*?)(\n###|$)`).exec(issue.body + '\n###');
  return m ? m[1].trim() : '';
}

const title = getField('title') || 'Untitled';
const description = getField('description');
const compatibility = (getField('compatibility') || '').split(',').map(s => s.trim()).filter(Boolean);
const license = getField('license') || 'Proprietary';
const keywords = (getField('keywords') || '').split(',').map(s => s.trim()).filter(Boolean);
const download_url = getField('download_url');
const vendor = getField('vendor');
const about_url = getField('about_url');
const about = getField('about');

const slug = title.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/(^-|-$)/g,'');

const fm = `---
title: "${title.replace(/"/g,'\"')}"
description: "${description.replace(/"/g,'\"')}"
screenshots: []
compatibility: ${JSON.stringify(compatibility)}
license: "${license}"
keywords: ${JSON.stringify(keywords)}
download_url: "${download_url}"
vendor: "${vendor}"
about: "${about.replace(/"/g,'\"')}"
about_url: "${about_url}"
draft: false
---

`;

fs.mkdirSync('content/entries',{recursive:true});
fs.writeFileSync(`content/entries/${slug || 'entry'}-${issueNumber}.md`, fm);
console.log('Created content file from issue.');
