import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';

const shared = await readFile('src/assets/css/clusters/amazon-guide.css', 'utf8');
for (const country of ['peru', 'bolivia', 'brazil', 'colombia', 'guyana']) {
  test(`${country} delivers complete shared CSS under its actual content hash`, async () => {
    const css = await readFile(`dist/assets/css/clusters/${country}.css`, 'utf8');
    assert.equal(css, shared);
    assert.doesNotMatch(css, /@import\b/);
    assert.ok(css.includes(`.${country}-hero`));
    assert.ok(css.includes(`[data-country="${country}"]`));
    const version = createHash('sha256').update(css).digest('hex').slice(0,12);
    for (const prefix of ['', 'es/']) {
      const page = await readFile(`dist/${prefix}${country}/index.html`, 'utf8');
      assert.ok(page.includes(`/assets/css/clusters/${country}.css?v=${version}`));
    }
  });
}
