// Main JS: active nav, year, simple portfolio filter
const yearEl = document.getElementById('y'); if (yearEl) yearEl.textContent = new Date().getFullYear();

// Active nav link on scroll for pages with sections
const navLinks = Array.from(document.querySelectorAll('nav a'));
function setActiveByHash(hash) {
  navLinks.forEach(a => a.classList.toggle('active', a.getAttribute('href') === hash));
}
window.addEventListener('hashchange', () => setActiveByHash(location.hash));
setActiveByHash(location.hash || '#home');

// Simple project loader (if present)
try {
  const projEl = document.getElementById('projects');
  if (projEl && window.projects) {
    projEl.innerHTML = window.projects.map(p => {
      const tagEls = (p.tags||[]).map(t=>`<span class="tag">${t}</span>`).join(' ');
      const linkEls = (p.links||[]).map(l=>`<a class="btn" href="${l.href}">${l.label}</a>`).join(' ');
      return `<article class="card" data-tags="${(p.tags||[]).join(',')}">
        <h3>${p.title}</h3>
        <p>${p.blurb||''}</p>
        <div class="row">${tagEls}</div>
        <div style="margin-top:10px; color:var(--muted)">${p.stack||''}</div>
        <div class="row" style="margin-top:12px">${linkEls}</div>
      </article>`;
    }).join('');
    const filterBar = document.getElementById('projectFilters');
    filterBar?.addEventListener('click', (e)=>{
      const btn = e.target.closest('button[data-filter]'); if(!btn) return;
      const f = btn.dataset.filter;
      for(const el of projEl.children){
        const tags = el.getAttribute('data-tags') || '';
        el.style.display = (f==='all' || tags.includes(f)) ? '' : 'none';
      }
    });
  }
} catch (e) { console.warn(e); }

// Contact form fallback
const form = document.getElementById('contactForm');
form?.addEventListener('submit', (e)=>{
  e.preventDefault();
  const data = new FormData(form);
  const obj = Object.fromEntries(data.entries());
  alert(`Thanks, ${obj.name}! I’ll reply to ${obj.email} soon.`);
  form.reset();
});
