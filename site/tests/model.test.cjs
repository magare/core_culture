const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const validator = require('gltf-validator');
const site = path.resolve(__dirname, '..');
const glb = fs.readFileSync(path.join(site, 'assets/models/core-culture-gym.glb'));
const manifest = JSON.parse(fs.readFileSync(path.join(site, 'assets/models/model-manifest.json')));
const jsonLength = glb.readUInt32LE(12);
const document = JSON.parse(glb.subarray(20, 20 + jsonLength).toString());
const binary = glb.subarray(28 + jsonLength);
const viewer = fs.readFileSync(path.join(site, 'js/model-viewer.js'), 'utf8');
const loader = fs.readFileSync(path.join(site, 'js/model-loader.js'), 'utf8');

test('GLB is self-contained, compressed, and within the download budget', () => {
  assert.equal(glb.readUInt32LE(0), 0x46546c67);
  assert.equal(glb.readUInt32LE(4), 2);
  assert.equal(glb.readUInt32LE(8), glb.length);
  assert.equal(glb.length, manifest.bytes);
  assert.ok(glb.length < 6 * 1024 * 1024);
  assert.ok(document.extensionsRequired.includes('EXT_meshopt_compression'));
  assert.ok(document.images.length > 0);
  for (const image of document.images) assert.equal(typeof image.bufferView, 'number');
  for (const buffer of document.buffers) assert.equal(buffer.uri, undefined);
});

test('the exported GLB passes core glTF validation', async () => {
  const report = await validator.validateBytes(new Uint8Array(glb), { maxIssues: 0 });
  assert.equal(report.issues.numErrors, 0, JSON.stringify(report.issues));
  assert.equal(report.issues.numWarnings, 0, JSON.stringify(report.issues));
  // The validator does not inspect EXT_meshopt buffers; decode them below too.
});

test('every compressed buffer decodes, and position attributes contain finite geometry', async () => {
  const { MeshoptDecoder } = await import('three/addons/libs/meshopt_decoder.module.js');
  await MeshoptDecoder.ready;
  const decoded = document.bufferViews.map(view => {
    const ext = view.extensions?.EXT_meshopt_compression;
    if (!ext) return binary.subarray(view.byteOffset || 0, (view.byteOffset || 0) + view.byteLength);
    const bytes = new Uint8Array(ext.count * ext.byteStride);
    MeshoptDecoder.decodeGltfBuffer(bytes, ext.count, ext.byteStride,
      binary.subarray(ext.byteOffset || 0, (ext.byteOffset || 0) + ext.byteLength), ext.mode, ext.filter);
    return bytes;
  });
  let triangles = 0;
  for (const mesh of document.meshes) for (const primitive of mesh.primitives) {
    triangles += document.accessors[primitive.indices].count / 3;
    const accessor = document.accessors[primitive.attributes.POSITION];
    assert.equal(accessor.componentType, 5126);
    const bytes = decoded[accessor.bufferView];
    const values = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    const stride = document.bufferViews[accessor.bufferView].byteStride || 12;
    for (let vertex = 0; vertex < accessor.count; vertex++) for (let component = 0; component < 3; component++) {
      assert.ok(Number.isFinite(values.getFloat32((accessor.byteOffset || 0) + vertex * stride + component * 4, true)));
    }
  }
  assert.equal(triangles, manifest.triangles);
  assert.ok(triangles > 250000 && triangles < 350000);
});

test('branding, top-hung signage, proportions, and the source Blender file are preserved', () => {
  assert.equal(manifest.hanging_signs, 10);
  assert.equal(manifest.exported_logos, 8); // three floor-circle logos were removed with the unsupported circle
  assert.deepEqual(manifest.footprint_ft, [96, 60]);
  assert.ok(document.nodes.some(node => node.extras?.web_group === 'signage'));
  assert.equal(document.nodes.filter(node => node.extras?.web_group === 'logos').length, 8);
  const source = path.join(site, '../output/blender/core_culture_gym', manifest.source);
  if (fs.existsSync(source)) assert.equal(crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex'), manifest.source_sha256);
});

test('viewer loads near the section, respects data saver, and never auto-rotates', () => {
  assert.match(loader, /IntersectionObserver/);
  assert.match(loader, /saveData/);
  assert.match(loader, /import\('\.\/model-viewer\.bundle\.js/);
  assert.match(viewer, /controls\.autoRotate = false/);
  assert.match(viewer, /!document\.hidden/);
  assert.ok(!viewer.includes('setAnimationLoop'));
  assert.match(viewer, /controls\.enabled = false/);
  assert.match(viewer, /'pan-y'/);
});

test('model has keyboard controls, recoverable errors, and a single reusable expanded canvas', () => {
  for (const key of ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Escape', 'Home']) assert.ok(viewer.includes(key));
  assert.match(viewer, /webglcontextlost/);
  assert.match(viewer, /webglcontextrestored/);
  assert.match(viewer, /modelDialogMount'\)\.append\(root\)/);
  assert.match(viewer, /modelHome'\)\.append\(root\)/);
  assert.match(loader, /Try loading again/);
  assert.ok(fs.existsSync(path.join(site, 'js/model-viewer.bundle.js')));
});
