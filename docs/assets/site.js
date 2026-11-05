document.documentElement.classList.add('js');
const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.nav');
toggle?.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  nav.classList.toggle('is-open', open);
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && toggle?.getAttribute('aria-expanded') === 'true') {
    toggle.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
    toggle.focus();
  }
});
const search = document.querySelector('#publication-search');
const publications = [...document.querySelectorAll('.publication')];
const typeFilter = document.querySelector('#publication-type');
const yearFilter = document.querySelector('#publication-year');
const normalizeSearch = value => value.toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
function filterPublications() {
  const terms = normalizeSearch(search.value).trim().split(/\s+/).filter(Boolean);
  let count = 0;
  publications.forEach(item => {
    const text = normalizeSearch(item.dataset.search);
    const match = terms.every(term => text.includes(term)) &&
      (!typeFilter.value || item.dataset.type === typeFilter.value) &&
      (!yearFilter.value || item.dataset.year === yearFilter.value);
    item.hidden = !match;
    if (match) count++;
  });
  document.querySelector('.publication-count').textContent = `${count} of ${publications.length} research outputs · newest first`;
  document.querySelector('.empty-result').hidden = count !== 0;
}
if (search && typeFilter && yearFilter) {
  document.querySelector('.publication-tools').hidden = false;
  search.addEventListener('input', filterPublications);
  typeFilter.addEventListener('change', filterPublications);
  yearFilter.addEventListener('change', filterPublications);
}
document.querySelector('.reset-filters')?.addEventListener('click', () => {
  search.value = '';
  typeFilter.value = '';
  yearFilter.value = '';
  filterPublications();
  search.focus();
});
let statusTimeout;
function announce(message) {
  const status = document.querySelector('.status-message');
  status.textContent = message;
  clearTimeout(statusTimeout);
  statusTimeout = setTimeout(() => { status.textContent = ''; }, 3500);
}
document.querySelectorAll('.copy-citation').forEach(button => button.addEventListener('click', async () => {
  const citation = button.dataset.citation;
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(citation);
    } else {
      const area = document.createElement('textarea');
      area.value = citation;
      area.style.cssText = 'position:fixed;left:-9999px;top:0';
      document.body.append(area);
      area.select();
      const copied = document.execCommand('copy');
      area.remove();
      button.focus();
      if (!copied) throw new Error('Clipboard unavailable');
    }
    announce('Citation copied');
  } catch {
    announce('Clipboard unavailable. You can select and copy the citation text.');
  }
}));
document.querySelector('[data-print]')?.addEventListener('click', () => window.print());
