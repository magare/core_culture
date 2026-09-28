import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

/** A single, demand-rendered WebGL scene. Expanded mode reuses the same canvas. */
export async function mountModelViewer(root) {
  const $ = selector => document.querySelector(selector);
  const stage = $('#modelStage');
  const status = $('#modelStatus');
  const dialog = $('#modelDialog');
  const abort = new AbortController();
  const listen = (target, type, fn) => target.addEventListener(type, fn, { signal: abort.signal });
  let renderer, controls, asset, environmentTarget, ground, composer, aoPass, resizeObserver, visibilityObserver;
  let renderedFrames = 0;
  let frame = 0, inView = true, disposed = false, interactive = false, currentView = 'overview', customView = false;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#101311');
  const camera = new THREE.PerspectiveCamera(38, 1, .08, 250);

  function dispose() {
    disposed = true;
    cancelAnimationFrame(frame);
    abort.abort();
    controls?.dispose();
    resizeObserver?.disconnect();
    visibilityObserver?.disconnect();
    const closedImages = new Set();
    scene.traverse(object => {
      object.geometry?.dispose();
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      for (const material of materials) {
        if (!material) continue;
        if (material.map?.image && !closedImages.has(material.map.image)) {
          closedImages.add(material.map.image);
          material.map.image.close?.();
        }
        material.map?.dispose();
        material.dispose();
      }
    });
    environmentTarget?.dispose();
    composer?.passes.forEach(pass => pass.dispose?.());
    composer?.dispose();
    renderer?.dispose();
    renderer?.domElement.remove();
  }

  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'low-power', preserveDrawingBuffer: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    renderer.toneMapping = THREE.AgXToneMapping;
    renderer.toneMappingExposure = 1;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    renderer.shadowMap.autoUpdate = false;
    renderer.info.autoReset = false;
    const canvas = renderer.domElement;
    canvas.setAttribute('role', 'img');
    canvas.setAttribute('aria-label', 'Interactive Core Culture gym model. Central training floor 64 by 60 feet, with equipment and hanging zone signs.');
    canvas.setAttribute('aria-describedby', 'modelHelp modelKeyboardHelp');
    canvas.tabIndex = 0;
    stage.prepend(canvas);
    controls = new OrbitControls(camera, canvas);
    controls.enabled = false;
    controls.enableDamping = false;
    controls.autoRotate = false;
    controls.minDistance = 2;
    controls.maxDistance = 95;
    controls.minPolarAngle = .015;
    controls.maxPolarAngle = Math.PI / 2 - .025;
    controls.maxTargetRadius = 20;
    controls.screenSpacePanning = false;
    canvas.style.touchAction = 'pan-y';

    function requestRender() {
      if (!frame && !disposed && inView && !document.hidden) frame = requestAnimationFrame(render);
    }
    function render() {
      frame = 0;
      if (disposed || !inView || document.hidden) return;
      renderer.info.reset();
      if (composer) composer.render();
      else renderer.render(scene, camera);
      // Useful read-only diagnostics, without exposing a mutable scene global.
      root.dataset.frames = String(++renderedFrames);
      root.dataset.drawCalls = String(renderer.info.render.calls);
      root.dataset.triangles = String(renderer.info.render.triangles);
      root.dataset.camera = camera.position.toArray().map(v => v.toFixed(3)).join(',');
    }
    controls.addEventListener('change', requestRender);

    const pmrem = new THREE.PMREMGenerator(renderer);
    const roomEnvironment = new RoomEnvironment();
    environmentTarget = pmrem.fromScene(roomEnvironment, .06);
    scene.environment = environmentTarget.texture;
    scene.environmentIntensity = .65;
    roomEnvironment.dispose();
    pmrem.dispose();
    scene.add(new THREE.HemisphereLight('#f3f1e9', '#6a7266', .95));
    const key = new THREE.DirectionalLight('#fff5e4', 2.6);
    key.position.set(-12, 25, 16);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    Object.assign(key.shadow.camera, { left: -24, right: 24, top: 24, bottom: -24, near: .5, far: 70 });
    key.shadow.bias = -.00015;
    key.shadow.normalBias = .02;
    scene.add(key);
    const fill = new THREE.DirectionalLight('#dfe9f1', .8);
    fill.position.set(16, 15, -14);
    scene.add(fill);

    const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
    let lastProgress = -1;
    const gltf = await loader.loadAsync(new URL('../assets/models/core-culture-gym.glb', import.meta.url).href, progress => {
      if (!progress.total) return;
      const value = Math.floor(progress.loaded / progress.total * 10) * 10;
      if (value !== lastProgress) status.textContent = `Loading the gym model… ${value}%`;
      lastProgress = value;
    });
    asset = gltf.scene;
    const bounds = new THREE.Box3().setFromObject(asset);
    const center = bounds.getCenter(new THREE.Vector3());
    const offset = new THREE.Vector3(-center.x, -bounds.min.y, -center.z);
    asset.position.add(offset);
    const signs = [];
    asset.traverse(object => {
      if (object.userData.web_group === 'signage') signs.push(object);
      if (!object.isMesh) return;
      object.castShadow = true;
      object.receiveShadow = true;
      for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
        if (material.transparent) {
          material.depthWrite = false;
          material.side = THREE.DoubleSide;
        }
        if (material.map && material.name.startsWith('BRAND')) {
          // Printed decals must not shadow their own nearly coplanar surface.
          object.castShadow = false;
          object.receiveShadow = false;
          material.polygonOffset = true;
          material.polygonOffsetFactor = -1;
          material.polygonOffsetUnits = -1;
        }
        if (material.map) material.map.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
      }
    });
    scene.add(asset);
    const floorBounds = new THREE.Box3().setFromObject(asset);
    ground = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.ShadowMaterial({ color: '#000000', opacity: .38 }));
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -.015;
    ground.receiveShadow = true;
    scene.add(ground);
    const renderTarget = new THREE.WebGLRenderTarget(1, 1, { samples: 4, type: THREE.HalfFloatType });
    composer = new EffectComposer(renderer, renderTarget);
    composer.addPass(new RenderPass(scene, camera));
    aoPass = new GTAOPass(scene, camera, 1, 1);
    aoPass.updateGtaoMaterial({ radius: .48, thickness: .5, distanceFallOff: 1, samples: 8 });
    aoPass.blendIntensity = .75;
    composer.addPass(aoPass);
    composer.addPass(new OutputPass());
    renderer.shadowMap.needsUpdate = true;
    const ft = .3048;
    const fromBlender = (x, y, z) => new THREE.Vector3(x * ft, z * ft, -y * ft).add(offset);
    const overviewTarget = fromBlender(48, 30, 3);
    const presets = {
      overview: { name: 'Overview', direction: new THREE.Vector3(.46, .61, .64).normalize() },
      top: { name: 'Top view', direction: new THREE.Vector3(0, 1, .018).normalize() },
      weights: { name: 'Free weights', fov: 56, position: fromBlender(48, 22, 9), target: fromBlender(48, 59, 5) },
      reception: { name: 'Reception', fov: 60, position: fromBlender(94.1, 44, 6.4), target: fromBlender(87.3, 54, 6) }
    };
    function fit(direction) {
      const right = new THREE.Vector3().crossVectors(camera.up, direction).normalize();
      const up = new THREE.Vector3().crossVectors(direction, right).normalize();
      const tan = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
      let distance = 0;
      for (const x of [floorBounds.min.x, floorBounds.max.x]) for (const y of [floorBounds.min.y, floorBounds.max.y]) for (const z of [floorBounds.min.z, floorBounds.max.z]) {
        const v = new THREE.Vector3(x, y, z).sub(overviewTarget);
        distance = Math.max(distance, Math.abs(v.dot(right)) / (tan * camera.aspect) + v.dot(direction), Math.abs(v.dot(up)) / tan + v.dot(direction));
      }
      return overviewTarget.clone().addScaledVector(direction, distance);
    }
    function setView(id) {
      const preset = presets[id];
      customView = false;
      currentView = id;
      camera.fov = preset.fov || 38;
      camera.updateProjectionMatrix();
      controls.target.copy(preset.target || overviewTarget);
      if (preset.direction) camera.position.copy(fit(preset.direction));
      else camera.position.copy(controls.target).add(preset.position.clone().sub(controls.target).multiplyScalar(Math.max(1, 1.3 / camera.aspect)));
      controls.update();
      $('#modelViewLabel').textContent = preset.name;
      root.querySelectorAll('[data-model-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.modelView === id)));
      root.dataset.view = id;
      requestRender();
    }
    function markCustomView() {
      customView = true;
      root.dataset.view = 'custom';
      $('#modelViewLabel').textContent = 'Your perspective';
      root.querySelectorAll('[data-model-view]').forEach(button => button.setAttribute('aria-pressed', 'false'));
    }
    controls.addEventListener('start', markCustomView);
    function setInteractive(enabled, focus = true) {
      interactive = enabled;
      controls.enabled = enabled;
      canvas.style.touchAction = enabled ? 'none' : 'pan-y';
      canvas.style.cursor = enabled ? 'grab' : 'default';
      $('#modelInteract').setAttribute('aria-pressed', String(enabled));
      $('#modelInteract').textContent = enabled ? 'Exit orbit' : 'Enable orbit';
      $('#modelHelp').textContent = enabled ? 'Drag to rotate · right-drag to pan · scroll / pinch to zoom · Esc to exit orbit.' : 'Choose a viewpoint, or enable orbit to rotate, pan and zoom.';
      if (focus) (enabled ? canvas : $('#modelInteract')).focus({ preventScroll: true });
    }
    function resize() {
      const width = stage.clientWidth, height = stage.clientHeight;
      if (!width || !height) return;
      renderer.setSize(width, height, false);
      composer?.setSize(width, height);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      if (!customView) setView(currentView);
      requestRender();
    }
    resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(stage);
    visibilityObserver = new IntersectionObserver(entries => {
      inView = entries[0].isIntersecting;
      if (inView) requestRender();
    });
    visibilityObserver.observe(stage);
    listen(document, 'visibilitychange', requestRender);
    root.querySelectorAll('[data-model-view]').forEach(button => listen(button, 'click', () => setView(button.dataset.modelView)));
    listen($('#modelInteract'), 'click', () => setInteractive(!interactive));
    listen($('#modelZoomIn'), 'click', () => { markCustomView(); controls.dollyIn(.82); });
    listen($('#modelZoomOut'), 'click', () => { markCustomView(); controls.dollyOut(.82); });
    listen($('#modelReset'), 'click', () => setView('overview'));
    listen($('#modelLabels'), 'click', () => {
      const visible = $('#modelLabels').getAttribute('aria-pressed') !== 'true';
      signs.forEach(object => { object.visible = visible; });
      $('#modelLabels').setAttribute('aria-pressed', String(visible));
      renderer.shadowMap.needsUpdate = true;
      requestRender();
    });
    listen(canvas, 'keydown', event => {
      if (!interactive) return;
      const arrows = { ArrowLeft: [1, 0], ArrowRight: [-1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] };
      if (arrows[event.key]) {
        event.preventDefault();
        markCustomView();
        const [x, y] = arrows[event.key];
        if (event.shiftKey) controls.pan(x * 28, y * 28);
        else { controls.rotateLeft(x * .09); controls.rotateUp(y * .09); }
      } else if (['+', '=', '-', 'Home', 'Escape'].includes(event.key)) {
        event.preventDefault();
        if (event.key === 'Escape') { event.stopPropagation(); setInteractive(false); }
        else if (event.key === 'Home') setView('overview');
        else { markCustomView(); if (event.key === '-') controls.dollyOut(.82); else controls.dollyIn(.82); }
      }
    });
    listen($('#modelExpand'), 'click', () => {
      $('#modelHome').style.minHeight = root.getBoundingClientRect().height + 'px';
      $('#modelDialogMount').append(root);
      dialog.showModal();
      document.body.classList.add('modal-open');
      inView = true;
      resize();
      $('#modelClose').focus();
    });
    listen($('#modelClose'), 'click', () => dialog.close());
    listen(dialog, 'close', () => {
      $('#modelHome').append(root);
      $('#modelHome').style.minHeight = '';
      setInteractive(false, false);
      inView = true;
      resize();
      $('#modelExpand').focus({ preventScroll: true });
    });
    listen(canvas, 'webglcontextlost', event => {
      event.preventDefault();
      controls.enabled = false;
      status.textContent = 'The graphics connection was interrupted. Restoring the 3D view…';
      $('#modelLoading').hidden = false;
    });
    listen(canvas, 'webglcontextrestored', () => {
      controls.enabled = interactive;
      $('#modelLoading').hidden = true;
      renderer.shadowMap.needsUpdate = true;
      requestRender();
    });
    listen(window, 'pagehide', event => { if (!event.persisted) dispose(); });
    listen(window, 'pageshow', requestRender);
    status.textContent = 'Finishing the materials…';
    resize();
    await renderer.compileAsync(scene, camera);
    root.dataset.state = 'ready';
    root.dataset.engine = 'three-' + THREE.REVISION;
    root.querySelectorAll('button').forEach(button => { button.disabled = false; });
    status.textContent = 'Interactive model ready.';
    $('#modelLoading').hidden = true;
    requestRender();
  } catch (error) {
    dispose();
    throw error;
  }
}
