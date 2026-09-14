'use strict';
// No analytics, credentials, or prompt contents are stored. Checklist state stays local.
const storageKey = 'manymangoes-ai-operations-checklist-v1';
const checks = [...document.querySelectorAll('[data-check]')];
let saved = {};
try { saved = JSON.parse(localStorage.getItem(storageKey) || '{}') || {}; } catch (_) {}
checks.forEach(input => { input.checked = saved[input.dataset.check] === true; });
function updateProgress() {
  if (!checks.length) return;
  const count = checks.filter(input => input.checked).length;
  document.getElementById('progress-text').textContent = `${count} of ${checks.length} checked`;
  document.getElementById('progress-fill').style.width = `${count / checks.length * 100}%`;
  const state = Object.fromEntries(checks.map(input => [input.dataset.check, input.checked]));
  try { localStorage.setItem(storageKey, JSON.stringify(state)); } catch (_) {}
}
checks.forEach(input => input.addEventListener('change', updateProgress));
document.getElementById('reset-progress')?.addEventListener('click', () => {
  checks.forEach(input => { input.checked = false; }); updateProgress();
});
updateProgress();
document.querySelectorAll('[data-copy]').forEach(button => {
  button.addEventListener('click', async () => {
    const target = document.getElementById(button.dataset.copy);
    const status = document.getElementById(button.dataset.status) || button.closest('.copy-block, .prompt-card')?.querySelector('.copy-status');
    const text = target.textContent.trim();
    try {
      if (!navigator.clipboard?.writeText) throw new Error('clipboard unavailable');
      await navigator.clipboard.writeText(text);
      status.textContent = button.closest('.terminal') || /command(?:-steps)?$/.test(button.dataset.copy)
        ? 'Copied. Paste into Terminal.' : 'Copied. Paste into your project chat.';
    } catch (_) {
      const disclosure = target.closest('details');
      if (disclosure) disclosure.open = true;
      target.scrollIntoView({block: 'center'});
      const range = document.createRange(); range.selectNodeContents(target);
      const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
      status.textContent = 'Automatic copy is unavailable. Text selected: press ⌘C (Mac) or Ctrl+C.';
    }
  });
});
document.querySelectorAll('[data-filter]').forEach(button => {
  button.addEventListener('click', () => {
    const filter = button.dataset.filter;
    document.querySelectorAll('[data-filter]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    document.querySelectorAll('[data-category]').forEach(card => { card.hidden = filter !== 'all' && card.dataset.category !== filter; });
  });
});
// A deep link to an automation card must work even after another filter was selected.
function revealHashCard() {
  const target = document.getElementById(location.hash.slice(1));
  if (target?.matches('[data-category]') && target.hidden) {
    document.querySelector('[data-filter="all"]').click(); target.scrollIntoView();
  }
}
window.addEventListener('hashchange', revealHashCard);
revealHashCard();
