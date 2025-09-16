// ESM, Ajv2020 + formats
import fs from 'node:fs';
import path from 'node:path';
import matter from 'gray-matter';
import Ajv2020 from 'ajv/dist/2020.js';
import addFormats from 'ajv-formats';

const ajv = new Ajv2020({ allErrors: true, strict: false }); // strict off = fewer surprises
addFormats(ajv);

const schema = JSON.parse(fs.readFileSync('schema/entry.schema.json', 'utf8'));
const validate = ajv.compile(schema);

const dir = 'content/entries';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));

let ok = true;
for (const f of files) {
  const raw = fs.readFileSync(path.join(dir, f), 'utf8');
  const fm = matter(raw).data;

  if (!validate(fm)) {
    ok = false;
    console.error(`Schema errors in ${f}:`);
    for (const e of validate.errors) console.error('-', e.instancePath || '/', e.message);
  }

  // repo-specific rules
  if (Array.isArray(fm.screenshots) && fm.screenshots.length > 4) {
    ok = false;
    console.error(`Too many screenshots in ${f} (max 4)`);
  }
  if (typeof fm.about === 'string' && fm.about.length > 500) {
    ok = false;
    console.error(`"about" too long in ${f} (${fm.about.length} > 500)`);
  }
}

if (!ok) process.exit(1);
console.log('Front-matter OK');
