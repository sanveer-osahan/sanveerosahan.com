# Designing a Multi-Tenant System — reference

Working material for the draft article
`src/content/articles/designing-a-multi-tenant-system.md`.

`presentation.html` is the presentation that explains the B2B multi-tenant model:
one product → one tenant per company → many users per tenant, with Slack
workspaces and Google Workspace domains as the two worked examples.

It is a reference only. This folder sits outside `src/pages/` and `public/`, so
Astro never builds it and it never appears on the site. Open the file directly in
a browser to view it.

Published copy (private artifact): https://claude.ai/artifact/TPYibaehSV4BrS2ngVZY55

## components/

`components/` holds the diagrams that the article and the presentation share.
Each `*.html` file there is one component and is the single source of truth.

A file that uses a component marks the slot with a pair of comments:

```
<!-- component:tenancy-models start -->
<!-- component:tenancy-models end -->
```

`components/sync.py` copies each component into every slot it finds. Edit the
component, then run it from the repository root:

```
python3 references/designing-a-multi-tenant-system/components/sync.py
```

Never edit a copy by hand. The next sync overwrites it.

| File | What it is |
| --- | --- |
| `tenancy-models.html` | The B2C and B2B pair, drawn in the Excalidraw stroke style. It draws in `currentColor`, so one drawing serves the light and the dark theme. |
| `tenancy-models.gen.py` | Draws `tenancy-models.html` from `rough.py`, from a fixed random seed, so the output is the same every run. |
| `onboarding.html` | The sign-up flow: two users, one product, one workspace, and the tenant resources it provisions. Same stroke style and same `currentColor` rule as the pair above. |
| `onboarding.gen.py` | Draws `onboarding.html` from `rough.py`. |
| `identity.html` | One user in many tenants: who owns a workspace and who is a member of it. Each user gets its own row, and the row runs User, Product, Workspace. |
| `identity.gen.py` | Draws `identity.html` from `rough.py`. |
| `tenant-context.html` | One request, one tenant: the product routes a request that names Workspace 1 to Workspace 1 alone. The dotted arrow is the tenant the request never reaches. |
| `tenant-context.gen.py` | Draws `tenant-context.html` from `rough.py`. |
| `tenant-isolation.html` | Who may reach which tenant: the roles two users hold, and the cross on the call from User 1 to the workspace it does not belong to. |
| `tenant-isolation.gen.py` | Draws `tenant-isolation.html` from `rough.py`. |
| `core-entities.html` | Two users, two workspaces, the five steps, and the store that holds Users, Workspaces and Memberships. |
| `core-entities.gen.py` | Draws `core-entities.html` from `rough.py`. |
| `api-sequence.html` | The API calls as a sequence, in three bands: Unsecured, User scoped and Tenant scoped. |
| `api-sequence.gen.py` | Draws `api-sequence.html` from `rough.py`. |
| `simple-monolith.html` | The first deployment: users, one server, one database instance, and the common and per-tenant databases it serves. |
| `simple-monolith.gen.py` | Draws `simple-monolith.html` from `rough.py`. |
| `postgres-layout.html` | One Postgres data directory: `global/` and `pg_wal/` shared, one `base/<oid>/` directory per database with its table files, and one connection per database. |
| `postgres-layout.gen.py` | Draws `postgres-layout.html` from `rough.py`. |
| `rough.py` | The Rough.js stroke primitives that Excalidraw draws with: line, rectangle, curve, ellipse, cylinder, arrow, text, and a label that follows a connector. Every generator imports it. |
| `comicshanns.b64`, `comicshanns-subset.woff2` | Comic Shanns, an Excalidraw font, cut down to printable ASCII. Every generator inlines the base64 copy, so each component carries its own font. |
| `worked-examples.html` | The Slack and Google Workspace panels, exactly as the presentation draws them. |
| `worked-examples.gen.py` | Lifts those two panels, the brand sprite and the panel CSS out of `presentation.html`, scopes every rule under `.diagram-worked`, and writes `worked-examples.html`. The presentation stays the source: edit it, run this, then run `sync.py`. |
| `mark-slack.svg`, `mark-google.svg` | The brand marks, from [thesvg.org](https://thesvg.org/). `presentation.html` carries them as `<symbol>` elements. |
