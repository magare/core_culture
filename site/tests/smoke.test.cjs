const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const site = path.resolve(__dirname, '..');
const context = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(site, 'js/data.js'), 'utf8'), context);
const CC = context.window.CC;
const html = fs.readFileSync(path.join(site, 'index.html'), 'utf8');
const css = fs.readFileSync(path.join(site, 'css/styles.css'), 'utf8');
const refinements = fs.readFileSync(path.join(site, 'css/refinements.css'), 'utf8');
const app = fs.readFileSync(path.join(site, 'js/app.js'), 'utf8');

test('content identifiers are unique in every collection', () => {
  for (const key of ['rooms', 'equipment', 'batches', 'events', 'memberships']) {
    const ids = CC[key].map(item => item.id);
    assert.equal(new Set(ids).size, ids.length, key);
  }
});

test('every room has a valid category, real local imagery, and a complete gallery', () => {
  assert.equal(CC.rooms.length, 8);
  for (const room of CC.rooms) {
    assert.ok(CC.categories[room.category], room.id);
    assert.ok(room.gallery.length > 0, room.id);
    for (const image of [room.photo, ...room.gallery]) {
      assert.ok(fs.existsSync(path.resolve(site, image.src)), image.src);
      assert.ok(image.alt.length > 15, image.src + ' alt');
    }
    for (const id of room.equipment) {
      assert.ok(CC.equipment.some(item => item.id === id && item.roomId === room.id), id);
    }
  }
});

test('equipment and sessions reference valid rooms and categories', () => {
  for (const item of [...CC.equipment, ...CC.batches, ...CC.events]) {
    assert.ok(CC.rooms.some(room => room.id === item.roomId), item.id);
    assert.ok(CC.categories[item.category], item.id);
  }
});

test('weekly class times are valid and do not double-book a room', () => {
  for (const item of CC.batches) {
    assert.match(item.time, /^([01]\d|2[0-3]):[0-5]\d$/);
    assert.ok(item.duration > 0);
  }
  const minutes = time => Number(time.slice(0, 2)) * 60 + Number(time.slice(3));
  for (const day of ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']) {
    for (const room of CC.rooms) {
      const list = CC.batches.filter(item => item.roomId === room.id && item.days.includes(day)).sort((a, b) => minutes(a.time) - minutes(b.time));
      for (let i = 1; i < list.length; i++) {
        assert.ok(minutes(list[i - 1].time) + list[i - 1].duration <= minutes(list[i].time), day + ': ' + list[i].name);
      }
    }
  }
});

test('HTML identifiers are unique and anchor targets exist', () => {
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
  assert.equal(new Set(ids).size, ids.length);
  for (const match of html.matchAll(/href="#([^"]+)"/g)) {
    if (match[1].startsWith('room=')) assert.ok(CC.rooms.some(room => room.id === match[1].slice(5)));
    else assert.ok(ids.includes(match[1]), match[1]);
  }
});

test('all declared scripts, fonts, styles, and static images are local and available', () => {
  for (const match of html.matchAll(/(?:src|href)="([^"]+)"/g)) {
    if (match[1].startsWith('#') || match[1].startsWith('data:')) continue;
    assert.ok(!/^https?:/.test(match[1]), match[1]);
    assert.ok(fs.existsSync(path.resolve(site, match[1].split('?')[0])), match[1]);
  }
  for (const match of css.matchAll(/url\('([^']+)'\)/g)) {
    assert.ok(fs.existsSync(path.resolve(site, 'css', match[1])), match[1]);
  }
});

test('the preview does not publish invented prices or submit personal information', () => {
  assert.ok(CC.memberships.every(plan => plan.price === null));
  assert.match(html, /No request is sent and no personal details are stored/);
  assert.ok(!/\b(fetch|XMLHttpRequest|sendBeacon|localStorage|sessionStorage)\b/.test(app));
  assert.match(html, /AI-generated concept imagery, not venue photography/);
});

test('motion preferences, form errors, and native accessible dialogs are provided', () => {
  assert.match(css, /prefers-reduced-motion:reduce/);
  assert.match(app, /classList.add\("reduce-motion"\)/);
  for (const id of ['Name', 'Phone', 'Date']) assert.ok(html.includes('aria-describedby="err' + id + '"'));
  for (const id of ['roomPanel', 'directory', 'lightbox', 'mobileMenu']) {
    assert.match(html, new RegExp('<dialog[^>]+id="' + id + '"'));
  }
});

test('the official identity and downloadable model are local', () => {
  assert.equal((html.match(/class="brand-logo"/g) || []).length, 2);
  assert.ok(!html.includes('class="brand-mark"'));
  assert.ok(!html.includes('id="planSvg"'));
  assert.ok(fs.existsSync(path.join(site, 'assets/images/core-culture-logo.png')));
  assert.ok(fs.existsSync(path.join(site, 'assets/models/core-culture-gym.glb')));
  assert.ok(!html.includes('id="modelImage"'));
  assert.ok(!html.includes('id="enlargeModel"'));
  assert.match(html, /The overall width and unspecified equipment remain estimates/);
  assert.match(html, /proposed amenities beyond the ground-floor model/);
});

test('four real 3D viewpoints are independent of the room photo galleries', () => {
  assert.equal((html.match(/data-model-view="[a-z]+"/g) || []).length, 4);
  assert.match(html, /role="group" aria-label="Choose a 3D viewpoint"/);
  assert.match(html, /<dialog[^>]+id="modelDialog"/);
  assert.match(app, /Enlarged room photo/);
  assert.ok(!app.includes('modelViews'));
});

test('light sections retain a contrasting keyboard focus ring', () => {
  assert.match(refinements, /\.paper :focus-visible\{outline-color:var\(--accent-dark\)\}/);
});
