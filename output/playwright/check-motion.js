async (page) => {
  const passed = [];
  const errors = [];
  const check = (value, label) => { if (!value) throw new Error(label); passed.push(label); };
  page.on('pageerror', error => errors.push(error.message));
  const settle = () => page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  const scroll = async top => { await page.evaluate(top => scrollTo({ top, behavior: 'instant' }), top); await settle(); };
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('http://127.0.0.1:8931/site/');
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => document.documentElement.classList.contains('motion-active'));
  await page.waitForFunction(() => document.getAnimations().every(animation => animation.playState !== 'running'));
  check(await page.locator('.hero-line').count() === 2, 'Hero has separate animated headline lines');
  const heroBefore = await page.locator('.hero-image').evaluate(node => getComputedStyle(node).transform);
  await page.screenshot({ path: 'output/playwright/motion-hero.png' });
  await scroll(400);
  check(await page.locator('.hero-image').evaluate(node => getComputedStyle(node).transform) !== heroBefore, 'Hero photo responds to scrolling');
  check(await page.locator('#siteNav').evaluate(node => node.classList.contains('is-scrolled')), 'Header responds to scrolling');
  const geometry = await page.locator('#cultureStory').evaluate(node => {
    const sticky = node.querySelector('.culture-sticky');
    return { top: node.getBoundingClientRect().top + scrollY, pin: parseFloat(getComputedStyle(sticky).top), travel: node.offsetHeight - sticky.offsetHeight };
  });
  for (const [chapter, progress] of [[1, .1], [2, .5], [3, .9]]) {
    await scroll(geometry.top - geometry.pin + geometry.travel * progress);
    await page.waitForFunction(chapter => document.querySelector('#cultureStory').dataset.chapter === String(chapter), chapter);
    await page.waitForFunction(() => getComputedStyle(document.querySelector('.culture-frame.is-current')).opacity === '1');
    check(await page.locator('.culture-frame[aria-hidden="false"]').count() === 1, `Chapter ${chapter} exposes one image`);
    check(await page.locator('.culture-sticky').evaluate((node, pin) => Math.abs(node.getBoundingClientRect().top - pin) < 2, geometry.pin), `Chapter ${chapter} remains pinned`);
    check(await page.locator('.culture-word').nth(chapter - 1).evaluate(node => Number(node.style.getPropertyValue('--word-fill')) > .4), `Chapter ${chapter} fills its title`);
    await page.screenshot({ path: `output/playwright/motion-chapter-${chapter}.png` });
  }
  const bandTop = await page.locator('.kinetic-band').evaluate(node => node.getBoundingClientRect().top + scrollY);
  await scroll(bandTop - 800);
  const bandBefore = await page.locator('.kinetic-track').evaluate(node => getComputedStyle(node).transform);
  await scroll(bandTop - 350);
  check(await page.locator('.kinetic-track').evaluate(node => getComputedStyle(node).transform) !== bandBefore, 'Large typography band moves with scrolling');
  await page.waitForFunction(() => document.getAnimations().every(animation => animation.playState !== 'running'));
  await page.screenshot({ path: 'output/playwright/motion-band.png' });
  await page.locator('#memberships').scrollIntoViewIfNeeded();
  await page.waitForFunction(() => [...document.querySelectorAll('.plan-card')].every(node => node.classList.contains('is-visible')));
  check(await page.locator('.plan-card.is-visible').count() === 3, 'All membership cards reveal');
  await page.locator('.plan-card button').first().focus();
  check(await page.locator('.plan-card').first().evaluate(node => getComputedStyle(node).opacity === '1'), 'Focused content stays visible');

  for (const [width, height] of [[320, 740], [390, 844], [768, 1024], [1024, 700], [1120, 800], [1121, 800], [1440, 600], [1440, 1000], [1920, 1080]]) {
    await page.setViewportSize({ width, height });
    await scroll(0);
    await settle();
    check(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth), `No page overflow at ${width}px`);
    const pinned = width > 900 && height > 680;
    check(await page.locator('.culture-sticky').evaluate((node, pinned) => (getComputedStyle(node).position === 'sticky') === pinned, pinned), `Appropriate story layout at ${width}px`);
    const storyPosition = await page.locator('#cultureStory').evaluate(node => node.getBoundingClientRect().top + scrollY);
    await scroll(storyPosition - (pinned ? 40 : 100));
    check(await page.locator('.culture-word').nth(1).evaluate(node => node.getBoundingClientRect().right <= innerWidth), `Narrative title fits at ${width}px`);
    if (width === 390 || width === 1024) {
      await page.waitForFunction(() => document.getAnimations().every(animation => animation.playState !== 'running'));
      await page.screenshot({ path: `output/playwright/motion-story-${width}.png` });
    }
    if (width === 1024) {
      check(await page.locator('#menuBtn').isVisible() && !await page.locator('.desktop-nav').isVisible(), 'Tablet uses compact navigation');
      await page.locator('#menuBtn').click();
      check(await page.locator('#mobileMenu').isVisible(), 'Tablet menu opens');
      await page.keyboard.press('Escape');
      await page.locator('#mobileMenu').waitFor({ state: 'hidden' });
    }
  }

  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.waitForFunction(() => !document.documentElement.classList.contains('motion-active'));
  check(await page.locator('.culture-sticky').evaluate(node => getComputedStyle(node).position !== 'sticky'), 'Live reduced-motion preference removes pinning');
  check(await page.locator('.motion-reveal').evaluateAll(nodes => nodes.every(node => getComputedStyle(node).opacity === '1')), 'Reduced motion leaves every reveal visible');
  check(await page.locator('.hero-image').evaluate(node => getComputedStyle(node).transform === 'none'), 'Reduced motion removes parallax');
  check(await page.evaluate(() => document.getAnimations().every(animation => animation.playState !== 'running')), 'Reduced motion stops running animations');
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.waitForFunction(() => document.documentElement.classList.contains('motion-active'));
  check(await page.locator('.culture-sticky').evaluate(node => getComputedStyle(node).position === 'sticky'), 'Live motion preference can be restored');

  await page.goto('http://127.0.0.1:8931/site/?rm=1');
  check(await page.evaluate(() => !document.documentElement.classList.contains('motion-active') && document.documentElement.classList.contains('reduce-motion')), 'Reduced-motion URL disables enhancement');
  check(await page.locator('.culture-sticky').evaluate(node => getComputedStyle(node).position !== 'sticky'), 'Reduced-motion URL has a natural document layout');

  const fallbackContext = await page.context().browser().newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const fallback = await fallbackContext.newPage();
  await fallback.goto('http://127.0.0.1:8931/site/');
  check(await fallback.locator('.culture-word').count() === 3 && await fallback.locator('.culture-frame.is-current').isVisible(), 'Story remains readable without JavaScript');
  check(await fallback.locator('#hero-title').evaluate(node => getComputedStyle(node).opacity === '1'), 'Hero remains readable without JavaScript');
  check(await fallback.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth), 'No-JavaScript mobile layout fits');
  await fallbackContext.close();
  check(errors.length === 0, 'No browser JavaScript errors');
  return { passed: passed.length, checks: passed, errors };
}
