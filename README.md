# Evergreen Minimal Site

A minimal, recruiter‑friendly personal website for Matthew Hanson.

## Structure
- `index.html`, `about.html`, `cv.html`, `portfolio.html`, `blog.html`, `contact.html`
- `style.css`, `main.js`
- `assets/favicon.svg`, `assets/og-image.jpg`
- `robots.txt`, `sitemap.xml`
- `netlify.toml`

## Quick Start
1. Create a new GitHub repo and clone it.
2. Copy all files into the repo root.
3. Commit & push:
   ```bash
   git add -A
   git commit -m "Initial minimal site"
   git push origin main
   ```
4. **Netlify**: New Site → Import from Git → pick the repo → Build cmd: _none_, Publish dir: `/`.
5. Update links:
   - Replace social URLs in page footers.
   - Replace `https://example.com` in meta tags, `sitemap.xml`, and `robots.txt` with your real domain.
6. Contact form: Netlify Forms will capture submissions automatically thanks to `data-netlify="true"`. Check the Forms tab.
7. Custom domain/email: point DNS to Netlify; set up email forwarding or a mailbox provider when ready.

## Editing Projects
Open `portfolio.html` and edit the `window.projects` array (title, blurb, tags, stack, links).

## Theme
Accent is an indigo palette with accessible contrast in light/dark. Change via CSS variables in `style.css`.
