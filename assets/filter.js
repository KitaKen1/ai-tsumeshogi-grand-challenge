document.documentElement.classList.add('js');
const form = document.querySelector('.filters');
const controls = Object.fromEntries(['stage','category','search','recent'].map(k => [k,document.getElementById(k)]));
const rows = [...document.querySelectorAll('tbody tr[data-task]')];
const sections = new Map([...document.querySelectorAll('.challenge')].map(s => [s.id,s]));
const normalize = s => s.normalize('NFKC').toLocaleLowerCase();
function filter() {
  const terms = normalize(controls.search.value.trim()).split(/\s+/).filter(Boolean);
  let count = 0;
  for (const row of rows) {
    const d = row.dataset;
    const show = (!controls.stage.value || d.stage === controls.stage.value)
      && (!controls.category.value || d.category === controls.category.value)
      && (!controls.recent.checked || Number(d.year) >= 2020)
      && terms.every(t => normalize(d.search).includes(t));
    row.hidden = !show;
    sections.get(d.task).hidden = !show;
    if (show) count++;
  }
  document.getElementById('result-count').textContent = `${count}件を表示`;
  document.getElementById('no-results').hidden = count !== 0;
  for (const b of document.querySelectorAll('[data-preset]')) b.setAttribute('aria-pressed',String(b.dataset.preset === controls.stage.value));
}
function clearControls() {
  controls.stage.value = ''; controls.category.value = '';
  controls.search.value = ''; controls.recent.checked = false;
}
form.addEventListener('submit',e => e.preventDefault());
form.addEventListener('input',filter);
form.addEventListener('change',filter);
form.addEventListener('reset',() => setTimeout(filter,0));
for (const b of document.querySelectorAll('[data-preset]')) b.addEventListener('click',() => {
  clearControls(); controls.stage.value = b.dataset.preset; filter();
});
function revealHash() {
  let id; try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  const target = sections.get(id);
  if (!target || !target.hidden) return;
  clearControls(); filter(); target.scrollIntoView();
}
document.addEventListener('click',e => {
  if (e.target.closest('a[href^="#"]')) requestAnimationFrame(revealHash);
});
window.addEventListener('hashchange',revealHash);
filter(); revealHash();
