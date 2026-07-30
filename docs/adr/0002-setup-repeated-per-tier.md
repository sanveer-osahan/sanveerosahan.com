# Setup instructions repeated in full in every tier section

## Status

accepted

## Context

"Set Up your AI Coding Agent" is structured as a price ladder: API billing, then
premium subscriptions, then the entry subscriptions, then free. Each tier gets
its own `### Setting It Up` containing a nested tabset, agent (Claude Code,
Codex) crossed with operating system (macOS, Windows, Linux).

Across those tiers the install commands and the first-task walkthrough are
identical. Only authentication differs: an API key, a subscription sign-in, or a
local model. The first tier section alone runs about 137 lines in a post of
roughly 283, so repeating it four times means several hundred lines of
near-duplicate HTML.

The alternative was hoisting install and the first-task demo into a single shared
step ahead of the tier sections, leaving each tier to cover only how you pay.

## Decision

Every tier section carries its own complete `[agent] × [OS]` tabset, including
install steps byte-identical to the other tiers. Nothing is hoisted.

## Why

The post is a ladder and readers do not read it front to back. Someone who has
decided their budget jumps straight to that band, sets the agent up, and leaves.
A section that opens with "install it as described three sections above" fails
exactly the reader it was written for, and the failure is worst for the least
technical reader, who is the stated audience.

Duplication is the cheaper mistake here. It costs maintenance effort, which falls
on the author. Hoisting costs comprehension, which falls on the reader.

## Consequences

- Roughly four copies of the same install block by the end of the post, kept in
  sync by hand. When an install command changes, grep every tier section rather
  than editing one place.
- Tabset `input` elements need unique `name` and `id` values per tier, or radio
  groups in different sections will interfere with each other.
- Instructions that are correct for one tier and wrong for another must be scoped
  rather than stated absolutely. The API section's "Do not run plain `codex
  login`" is the first instance: that command is correct on a subscription and
  wrong on API billing, so the warning names the billing mode it applies to.
