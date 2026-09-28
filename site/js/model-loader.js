/* The rest of the page never waits for Three.js or the model download. */
(() => {
  const root = document.querySelector('#modelViewer');
  const button = document.querySelector('#loadModel');
  const status = document.querySelector('#modelStatus');
  let pending = false;
  async function load() {
    if (pending || root.dataset.state === 'ready') return;
    pending = true;
    root.dataset.state = 'loading';
    root.setAttribute('aria-busy', 'true');
    button.hidden = true;
    status.textContent = 'Preparing your interactive floor…';
    try {
      const { mountModelViewer } = await import('./model-viewer.bundle.js?v=8');
      await mountModelViewer(root);
    } catch (error) {
      root.dataset.state = 'error';
      document.querySelector('#modelLoading').hidden = false;
      status.textContent = 'The 3D viewer could not start. Try again in a WebGL-enabled browser, or download the model below.';
      button.textContent = 'Try loading again';
      button.hidden = false;
      console.warn('Core Culture 3D viewer:', error.message);
    } finally {
      pending = false;
      root.setAttribute('aria-busy', 'false');
    }
  }
  button.addEventListener('click', load);
  // Mobile and data-saver visitors begin with the lightweight model poster and opt in.
  const mobile = matchMedia('(max-width: 780px)').matches;
  if (mobile) status.textContent = 'Static floor preview. Load the interactive model when you are ready.';
  if ('IntersectionObserver' in window && !navigator.connection?.saveData && !mobile) {
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        observer.disconnect();
        load();
      }
    }, { rootMargin: '250px' });
    observer.observe(root);
  }
})();
