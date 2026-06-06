# SETUP.md — Launch checklist for sanveerosahan.com

> Handoff file for continuing in a fresh Claude Code session.
> Goal: GitHub repo → Cloudflare Pages → live on sanveerosahan.com, deployed via GitHub Actions on every push to `main`.
> Check off items as completed. Delete this file when everything is done.

## Already done (previous session)

- [x] AstroPaper v6 theme scaffolded, personalized (name, domain, timezone, hero, about skeleton)
- [x] Example posts removed (theme docs backed up at `/tmp/astropaper-docs-backup`)
- [x] Starter post `src/content/posts/hello-world.md` (`draft: true`)
- [x] GitHub Actions workflow `.github/workflows/deploy.yml` — actions pinned to commit SHAs, builds with pnpm, deploys via wrangler to Pages project `sanveerosahan-com`
- [x] `git init` on branch `main` — **no commits yet**

## Decisions made (don't re-litigate)

| Decision | Choice |
|---|---|
| Stack | Astro + AstroPaper theme, markdown posts in `src/content/posts/` |
| Hosting | Cloudflare Pages (free), project name `sanveerosahan-com` |
| Deploy | GitHub Action on push to `main` (NOT Cloudflare git integration) |
| DNS | Move Namecheap nameservers → Cloudflare |
| Repo | **Public**, on PERSONAL GitHub account (not AtlanHQ), named `sanveerosahan.com` |
| Analytics | Cloudflare Web Analytics (enable at the end) |

## Remaining steps

### 1. Install dependencies + verify build

```bash
pnpm install   # may need user to run manually if sandbox blocks native builds (esbuild, sharp)
pnpm build     # must pass
pnpm dev       # preview at http://localhost:4321, user eyeballs it
```

### 2. Fill placeholders

Two `CHANGE-ME` markers (GitHub + LinkedIn URLs) in:
- `astro-paper.config.ts` (socials)
- `src/content/pages/about.md`

Ask user for handles. Also `<!-- TODO -->` blocks in about.md — ask user for 2-3 sentences or leave for later.

### 3. Commit + create GitHub repo

```bash
git add -A && git commit -m "Initial site: AstroPaper theme, personalized"
gh auth status   # confirm logged in as PERSONAL account, not work
gh repo create sanveerosahan.com --public --source . --push
```

⚠️ If `gh` is authed to an AtlanHQ/work account, re-auth or use `gh auth switch`. Repo must be on personal account.

### 4. Cloudflare setup (user does in browser, guide them)

1. Create free account at dash.cloudflare.com (skip if exists)
2. Copy **Account ID** (dashboard right sidebar, or Workers & Pages overview)
3. Create API token: My Profile → API Tokens → Create Token → Custom token:
   - Permission: **Account → Cloudflare Pages → Edit** (nothing else)
   - Account Resources: their account only
4. Create the Pages project (one-time, from local machine):
   ```bash
   npx wrangler pages project create sanveerosahan-com --production-branch main
   ```
   (will prompt browser login, or use `CLOUDFLARE_API_TOKEN=... npx wrangler ...`)

### 5. Set repo secrets

```bash
gh secret set CLOUDFLARE_API_TOKEN    # paste token when prompted
gh secret set CLOUDFLARE_ACCOUNT_ID   # paste account ID
```

Never echo the token into the terminal/logs.

### 6. First deploy

```bash
git commit --allow-empty -m "Trigger deploy" && git push   # or just push if step 3 didn't push
gh run watch   # watch the action
```

Verify at `https://sanveerosahan-com.pages.dev`.

### 7. Custom domain

1. Cloudflare dashboard → Add site → `sanveerosahan.com` → Free plan
2. Cloudflare shows 2 nameservers → user updates at Namecheap:
   Domain List → sanveerosahan.com → Nameservers → **Custom DNS** → paste both
3. Wait for Cloudflare "site active" email (minutes to ~24h)
4. Workers & Pages → `sanveerosahan-com` → Custom domains → add `sanveerosahan.com` AND `www.sanveerosahan.com`
5. Verify `https://sanveerosahan.com` loads with valid TLS

### 8. Finishing touches

- [ ] Enable Cloudflare Web Analytics (dashboard → Analytics → Web Analytics → add site); add the snippet via `src/layouts/Layout.astro` if not auto-injected
- [ ] Flip `draft: false` in `hello-world.md` when user is ready to publish
- [ ] Replace `public/favicon.svg` + `public/default-og.jpg` (still AstroPaper defaults) — optional
- [ ] Delete this file

## Notes for the agent

- Build script runs `astro check` — type errors fail the build.
- `package.json` has `pnpm.onlyBuiltDependencies: [esbuild, sharp]` — CI builds these automatically; local install may need user approval.
- Pages project name is `sanveerosahan-com` (dots not allowed) — must match `--project-name` in `.github/workflows/deploy.yml`.
- Writing posts: see README.md "Writing a post" section.
