import fs from 'node:fs';
import path from 'node:path';
import matter from 'gray-matter';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

const ajv = new Ajv({allErrors:true, allowUnionTypes:true});
addFormats(ajv);

const schema = JSON.parse(fs.readFileSync('schema/entry.schema.json','utf8'));
const validate = ajv.compile(schema);

const dir = 'content/entries';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
let ok = true;

for (const f of files) {
  const raw = fs.readFileSync(path.join(dir,f),'utf8');
  const fm = matter(raw).data;
  if (!validate(fm)) {
    ok = false;
    console.error(`Schema errors in ${f}:`);
    console.error(validate.errors);
  }
  if (fm.screenshots && fm.screenshots.length > 4) {
    ok = false;
    console.error(`Too many screenshots in ${f} (max 4)`);
  }
}
if (!ok) process.exit(1);
else console.log('Front-matter OK');
