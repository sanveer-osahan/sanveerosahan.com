# Palette research — the presentation, re-cut for video

Working notes for `references/designing-a-multi-tenant-system/presentation.html`.

The question: the presentation currently reuses the site palette (paper-cream `#f6f1e6`,
ink `#25201b`, one burnt-sienna accent `#8a4423`) and it reads dull. It will be
presented in a YouTube video. What palette and type should it use instead?

Every contrast ratio below is measured, not quoted: WCAG 2.2's own relative-luminance
formula `L = 0.2126·R + 0.7152·G + 0.0722·B` with the sRGB linearisation
`R = RsRGB/12.92 if RsRGB <= 0.04045 else ((RsRGB+0.055)/1.055)^2.4`
(<https://www.w3.org/TR/WCAG22/#dfn-relative-luminance>), and the ratio
`(L1 + 0.05) / (L2 + 0.05)` (<https://www.w3.org/TR/WCAG22/#dfn-contrast-ratio>).

---

## Recommendation

**Use Open Color** (<https://yeun.github.io/open-color/>, source
<https://github.com/yeun/open-color>), in the subset Excalidraw itself draws with —
Excalidraw's stroke picks *are* Open Color index 4, i.e. weight 800
(<https://github.com/excalidraw/excalidraw/blob/master/packages/common/src/colors.ts>).
So this is not a new look bolted onto the Excalidraw style; it is the Excalidraw
style's own palette, which the presentation currently overrides with the article's
cream.

**Record the light theme.** Keep the dark theme working, but shoot in light: on a
light ground the ink carries the signal in luma, which survives 4:2:0 and an 8 Mbps
1080p stream best (see §2).

### Light theme — the recording theme

| Role | Token in `presentation.html` | Open Color | Hex | Contrast vs `--bg` |
| --- | --- | --- | --- | --- |
| Page background | `--bg` | gray-1 | `#f1f3f5` | — |
| Card / panel | `--surface` | gray-0 | `#f8f9fa` | 1.06 : 1 |
| Recessed fill | `--surface-2` | gray-2 | `#e9ecef` | 1.06 : 1 |
| Hairline | `--line` | gray-3 | `#dee2e6` | 1.17 : 1 |
| Strong rule / wire | `--line-strong`, `--wire` | gray-5 | `#adb5bd` | 1.87 : 1 |
| **Ink** (text + all diagram strokes) | `--ink`, `--theme-text` | Excalidraw `black` | **`#1e1e1e`** | **14.99 : 1** |
| Muted text | `--muted` | gray-7 | `#495057` | 7.35 : 1 |
| **Accent family (primary)** | `--accent` | **grape-800** | **`#9c36b5`** | **5.23 : 1** |
| Accent tint (filled regions) | `--accent-soft` | grape-800 @ 12% α | `#e7dced` composite | 1.19 : 1 vs bg; ink on it 12.59 : 1 |
| Secondary 1 — "good / provisioned" | `--accent-2` | teal-900 | `#087f5b` | 4.50 : 1 |
| Secondary 2 — "attention / crossing a boundary" | `--accent-3` | orange-900 | `#d9480f` | 3.87 : 1 |
| Secondary 3 — **negation only** (the cross, the blocked call) | `--accent-danger` | red-900 | `#c92a2a` | 4.91 : 1 |

`--theme-text` is the hsl-channel twin of `--ink` that the diagram components read
(`color:hsl(var(--theme-text))`). For `#1e1e1e` that is `0deg 0% 12%`.

### Dark theme — twins

| Role | Open Color | Hex | Contrast vs `--bg` `#212529` |
| --- | --- | --- | --- |
| `--bg` | gray-9 | `#212529` | — |
| `--surface` | gray-8 | `#343a40` | 1.34 : 1 |
| `--line` / `--wire` | gray-7 | `#495057` | 1.89 : 1 |
| `--ink` / `--theme-text` | gray-0 | `#f8f9fa` (`210deg 17% 98%`) | 14.63 : 1 |
| `--muted` | gray-4 | `#ced4da` | 10.32 : 1 |
| `--accent` | grape-300 | `#e599f7` | 7.52 : 1 |
| `--accent-2` | teal-300 | `#63e6be` | 9.99 : 1 |
| `--accent-3` | orange-300 | `#ffc078` | 9.60 : 1 |
| `--accent-danger` | red-300 | `#ffa8a8` | 8.39 : 1 |

Against `--surface` `#343a40` these land at 5.61 : 1 (grape-300), 7.45 : 1 (teal-300),
7.16 : 1 (orange-300), 6.26 : 1 (red-300), ink 10.91 : 1 — all still ≥ 4.5 : 1.

### Why these, in one line each

- **Personality without a new style.** Grape-800 `#9c36b5` is 54% saturation at 46%
  lightness; the current accent `#8a4423` is 60% at 34% — nearly the same saturation
  figure but so dark it reads brown-grey once the stream has been through 4:2:0.
  Lifting lightness, not saturation, is what buys visible colour on video.
- **Hue separation.** grape 288°, teal 162°, orange 17°, red 0° (red reserved for
  negation only). Carbon's categorical palette is explicitly ordered to "maximize
  contrast between neighboring colors"
  (<https://carbondesignsystem.com/data-visualization/color-palettes/>) — wide hue
  steps are the mechanism, and these are wide.
- **No pure white, no pure black.** `#f1f3f5` has relative luminance 0.894, not 1.0;
  `#212529` has 0.018, not 0.0. That leaves headroom for exactly the overshoot that
  EBU R 103 reserves range for (§2).
- **Text safety is measured, not assumed.** Ink 14.99 : 1 and the primary accent
  5.23 : 1 both clear WCAG 1.4.3's 4.5 : 1 for body text
  (<https://www.w3.org/TR/WCAG22/#contrast-minimum>). Orange-900 at 3.87 : 1 does
  **not** — it clears 1.4.11's 3 : 1 for graphics
  (<https://www.w3.org/TR/WCAG22/#non-text-contrast>) and is therefore a stroke and
  fill colour, never small label text. That constraint is why it sits at secondary 2.

### Type, for video

Keep the voice (Newsreader display / Inter sans / JetBrains Mono / Excalifont for the
hand labels). Change the scale, not the faces:

- Body goes from `16px` to **`clamp(22px, 1.9vw, 28px)`**, h1 to ~`64px`, h2 to ~`40px`,
  h3 to ~`30px`. Derivation in §1.
- Drop Newsreader for the *smallest* text (`.eyebrow` at `.72rem`, table cells).
  WCAG 2.2's own note is that "Fonts with extraordinarily thin strokes or unusual
  features" are harder to read, and that anti-aliasing can render thin text fainter
  than its specified colour — the advice is to pick a thicker face or exceed the
  required ratio (<https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum>).
  A serif at 11px in a 4:2:0 stream is the worst case of both.
- Excalifont diagram labels: `rough.py` draws them at `size=14`–`18` in user units
  on viewBoxes 440–1100 wide. At a 1080-tall frame that is roughly 1.3–1.9% of frame
  height. Raise the base label size in each generator so labels land near 2.5–3%.

---

## 1. What video delivery demands of a palette and of type

### Contrast

- WCAG 2.2 SC 1.4.3 Contrast (Minimum), AA: text and images of text need **4.5 : 1**;
  **3 : 1** for large-scale text. Exceptions: inactive components, pure decoration,
  invisible text, text in a picture with significant other visual content, and
  logotypes. <https://www.w3.org/TR/WCAG22/#contrast-minimum>
- SC 1.4.6 Contrast (Enhanced), AAA: **7 : 1**, and **4.5 : 1** for large-scale text.
  <https://www.w3.org/TR/WCAG22/#contrast-enhanced>
- SC 1.4.11 Non-text Contrast, AA: **3 : 1** against adjacent colours for "parts of
  graphics required to understand the content". This is the clause that governs the
  diagram strokes, the arrowheads, the dotted boundary frames and the cross.
  <https://www.w3.org/TR/WCAG22/#non-text-contrast>
- "Large scale (text)" is defined as **at least 18 point, or 14 point bold**
  (<https://www.w3.org/TR/WCAG22/#dfn-large-scale>). The Understanding document gives
  the conversion: "The ratio between sizes in points and CSS pixels is `1pt = 1.333px`,
  therefore `14pt` and `18pt` are equivalent to approximately `18.5px` and `24px`."
  <https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum>

So **24px is the floor at which 3 : 1 is permissible at all**. Anything below it in
the frame needs the full 4.5 : 1. The recommendation keeps every text colour above
4.5 : 1 anyway, because video adds its own losses on top.

### Minimum text size in a 1080p and a 4K frame

YouTube's recommended 16:9 resolutions: 1080p = **1920×1080**, 1440p = **2560×1440**,
2160p/4K = **3840×2160**; "The standard aspect ratio for YouTube on a computer is 16:9."
<https://support.google.com/youtube/answer/6375112>

The size that matters is not the authored `px` but the **fraction of frame height**,
because the viewer's phone scales the whole frame. Two first-party anchors:

- BBC, on subtitle size: the current size is **8% of the video height** per line of
  subtitle text, with smaller steps down to 0.25 of that, and every line of text
  should fit within around 8% of the height of the video. BBC research found "a clear
  preference for larger font sizes on the smallest screen", with no reliable
  recommendation possible for tablet and desktop.
  <https://bbc.github.io/gaad/how_big_should_subtitles_be/index.html>
- WCAG's 24px large-text floor, above.

Derivation (mine, flagged as such): captions get 8% of frame height; captions are a
single short line read at a glance. Continuous body prose can be smaller but not by
much on a phone. Targeting **≈3% of frame height** for body text gives **~32px in a
1080-tall frame** and **~65px in a 2160-tall frame** — which is why the body step
above goes to `clamp(22px, 1.9vw, 28px)` and the page is then captured at a browser
window around 1280–1440 CSS px wide and scaled to 1920 (≈1.4× magnification), rather
than captured 1:1 at 1920 where 16px prose is 1.5% of frame height and unreadable on
a phone.

Practical consequence for this file: `--step` is `clamp(1.8rem, 1.2rem + 1.8vw, 3rem)`
and `.page` is `max-width:1080px`. For a 1920-wide capture the page is better framed
at `max-width:1440px` with the type scale above than left at 1080px and upscaled.

### Safe areas

EBU R 95, *Safe areas for 16:9 television production* (v1.1, June 2017,
<https://tech.ebu.ch/publications/r095>, PDF <https://tech.ebu.ch/docs/r/r103.pdf>'s
sibling <https://tech.ebu.ch/docs/r/r095.pdf>): the **action safe area is 3.5%** and
the **graphics safe area is 5%**, applied top, bottom and sides — i.e. 7% and 10% of
the full frame. At 1920×1080 that is **96px left/right and 54px top/bottom of graphics
safe margin**. The presentation's `padding-inline:20px` is well inside that at a
1080px page width centred in a 1920 frame, but a full-bleed capture would not be.

(The R 95 PDF body is a scan; the percentages above come from the EBU publication page's
own summary and FAQ, which is first-party.)

### Why pure white and pure black hurt a compressed stream

- EBU R 103, *Video signal tolerance in digital television systems* v3.0
  (<https://tech.ebu.ch/docs/r/r103.pdf>): each RGB primary should sit between 0% and
  100% of the narrow range; material is accepted if R, G and B fall between **−5% and
  105%** and luminance between **−1% and 103%**. R 103 recommends a range of acceptable
  code values *beyond* the nominal video range specifically to absorb **filtering
  overshoots, compression artefacts** and rapid lighting changes. Content authored at
  exactly 0% and 100% has no such headroom: every ringing artefact around a hard edge
  clips instead of being absorbed. In 10-bit SDI, black is luma code 64 and nominal
  white 940; codes below 4 and above 1019 are reserved for signalling and are never
  visible.
- An out-of-gamut error should only be flagged when it covers more than 1% of the
  active screen, because, in the EBU's words, trying to "cure" small gamut errors can
  degrade quality more than the errors themselves (same document). Large flat areas of
  `#ffffff` are exactly the 1%-plus case.
- Separately: a large flat field of maximum luma next to near-black ink maximises the
  local contrast an encoder has to spend bits on at an 8 Mbps 1080p budget (§2).

`#f1f3f5` (L = 0.894) and `#212529` (L = 0.018) back off both ends deliberately.

---

## 2. What compression does to saturated colour

### The bitrate budget

YouTube's own recommended upload encoding settings
(<https://support.google.com/youtube/answer/1722171>): container MP4 with the moov
atom at the front, video codec H.264 High Profile, closed GOP of half the frame rate,
CABAC, variable bitrate, and **chroma subsampling 4:2:0**. SDR bitrate targets:
**1080p24–30 = 8 Mbps**, 1080p48–60 = 12 Mbps, 1440p = 16 Mbps, 2160p = 35–45 Mbps.

And the viewer does not necessarily get what you uploaded: "To give you the best
viewing experience, YouTube changes the quality of your video stream based on your
viewing conditions," with the factors listed as internet connection speed, video
player or screen size, the quality of the original upload, and the browser
(<https://support.google.com/youtube/answer/91449>). A thin hairline that only just
survives 1080p does not survive the Data-saver rendition.

### What 4:2:0 actually does

The AV1 specification defines the chroma formats by two flags —
"`subsampling_x`, `subsampling_y` specify the chroma subsampling format" — where
`subsampling_x = 0, subsampling_y = 0` is YUV 4:4:4, `1, 0` is YUV 4:2:2, and
**`1, 1` is YUV 4:2:0** (<https://aomediacodec.github.io/av1-spec/>, Color config
semantics). The same spec derives the chroma plane size from those flags: the output
chroma plane `OutputFrameU` "is ( outputW >> subsampling_x ) samples across by
( outputH >> subsampling_y ) samples down", and the tile writer shifts
`w = w >> subsampling_x`, `h = h >> subsampling_y` (Large scale tile decoding process).

So in 4:2:0 the two chroma planes are **half the width and half the height of the luma
plane — one quarter of the samples.** The spec also notes that for subsampled streams
the chroma sample sits "Horizontally co-located with (0, 0) luma sample, vertical
position in the middle between two luma samples" (`chroma_sample_position`,
`CSP_VERTICAL`) — i.e. chroma is additionally offset from the luma grid it has to
line up with.

### Why that is fatal for thin saturated strokes

WCAG's own relative-luminance weights (which are the BT.709 luma weights) are
`0.2126·R + 0.7152·G + 0.0722·B`
(<https://www.w3.org/TR/WCAG22/#dfn-relative-luminance>). Green carries 72% of luma;
**red carries 21% and blue 7%**. A saturated red or blue stroke on a neutral ground
therefore differs from that ground mostly in *chroma* — and chroma is the quarter-
resolution, spatially offset plane. `rough.py` draws at `stroke-width:1.8` on a 440–1100
unit viewBox; after layout and encoding that is a one- to two-pixel line. A one-pixel
line whose signal lives in a half-resolution plane is reconstructed from neighbouring
samples: it blurs, fringes, and wanders off the luma edge.

Two consequences, both baked into the recommendation:

1. **The strokes stay ink.** `#1e1e1e` on `#f1f3f5` is a 14.99 : 1 *luma* difference.
   It survives every rendition down to 360p. Accent colour goes on things with area —
   filled regions, band backgrounds, a thick underline, a label's own box — not on
   hairlines.
2. **No saturated red (or blue) text on a dark ground.** It is the worst case of both
   effects at once: the hue with little luma weight, on a background where the encoder
   has the fewest bits, in glyph-sized strokes. That is why red-900 `#c92a2a` here is
   reserved for negation (the cross, the blocked call) on the light theme and lifted to
   red-300 `#ffa8a8` on the dark theme, where it is a light tint carrying real luma
   (8.39 : 1) rather than a dark saturated one.

---

## 3. First-party palettes considered

### Open Color — **recommended**

<https://yeun.github.io/open-color/> · <https://github.com/yeun/open-color>

Its own README: "an open-source color scheme optimized for UI like font, background,
border, etc.", with the stated goals "All colors shall have adequate use", "Provide
general color for UI design", "All colors will be beautiful in itself and harmonious",
and — the one that matters here — "At the same brightness level, the perceived
brightness will be constant". 13 hues × 10 steps (0 = lightest, 9 = darkest).
<https://raw.githubusercontent.com/yeun/open-color/master/README.md>

Caveat it states about itself: the colours may change in future versions, so it advises
against using an Open Color as a *main identity* colour. For a presentation that is
fine — it is not the site's brand colour, and the hexes get pinned in CSS anyway.

What it gives this presentation: a palette whose steps are tuned to equal perceived
brightness, so swapping grape for teal for orange at the same index does not change
how heavy the ink feels — exactly what a diagram with three accents needs. Measured
ratios for the steps recommended above (light bg `#f1f3f5`, dark bg `#212529`):

| Open Color | Hex | on `#f1f3f5` | on `#212529` |
| --- | --- | --- | --- |
| gray-7 | `#495057` | 7.35 | 1.89 |
| grape-800 | `#9c36b5` | 5.23 | 2.65 |
| grape-900 | `#862e9c` | 6.54 | 2.12 |
| grape-300 | `#e599f7` | 1.95 | 7.52 |
| teal-900 | `#087f5b` | 4.50 | 3.08 |
| teal-800 | `#099268` | 3.55 | 3.91 |
| teal-300 | `#63e6be` | 1.47 | 9.99 |
| orange-900 | `#d9480f` | 3.87 | 3.59 |
| orange-300 | `#ffc078` | 1.53 | 9.60 |
| red-900 | `#c92a2a` | 4.91 | 2.83 |
| red-300 | `#ffa8a8` | 1.74 | 8.39 |
| blue-800 | `#1971c2` | 4.51 | 3.07 |
| yellow-800 | `#f08c00` | 2.23 | 6.21 |

Note yellow: `#f08c00` is 2.23 : 1 on light — it fails even 1.4.11's 3 : 1. Yellow is a
dark-theme-only accent. That is the kind of trap the measured table exists to catch.

### Excalidraw's own palette — the provenance

<https://github.com/excalidraw/excalidraw/blob/master/packages/common/src/colors.ts>

- `DEFAULT_ELEMENT_STROKE_PICKS` = `#1e1e1e` (its standalone `black`), red[4] `#e03131`,
  green[4] `#2f9e44`, blue[4] `#1971c2`, yellow[4] `#f08c00`.
- `DEFAULT_ELEMENT_BACKGROUND_PICKS` = `transparent`, red[1] `#ffc9c9`,
  green[1] `#b2f2bb`, blue[1] `#a5d8ff`, yellow[1] `#ffec99`.
- `DEFAULT_CANVAS_BACKGROUND_PICKS` = `#ffffff`, `#f8f9fa` (its comment: "radix slate2",
  and also Open Color gray-0), `#f5faff` ("radix blue2"), `#fffce8` ("radix yellow2"),
  `#fdf8f6` ("radix bronze2").
- The file's own comment maps its array indexes `[0, 2, 4, 6, 8]` to Open Color weights
  `50, 200, 400, 600, 800`. So **index 4 = weight 800** (strokes) and
  **index 1 = weight 200** (backgrounds).

This is the single strongest argument for Open Color here: the "Excalidraw style" the
presentation already uses *is* Open Color 800 strokes over Open Color 200 fills on a
near-white canvas. The dullness is not the style; it is the cream override.

Why not take Excalidraw's four picks verbatim: `#f08c00` is 2.23 : 1 on light (above),
`#e03131` is 4.06 : 1 and `#2f9e44` is 3.27 : 1 — only blue clears 4.5 : 1. Shifting to
step 900 for the secondaries, as recommended, fixes that while staying in the family.

### Radix Colors — the step discipline, worth borrowing even if not the palette

<https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale>

The 12-step contract, which is the clearest first-party statement of *which step is
allowed where*:

- **1–2** app background and subtle component background (cards, code blocks, sidebars)
- **3–5** component backgrounds: 3 normal, 4 hover, 5 pressed/selected
- **6** subtle border/separator on non-interactive elements (headers, cards, alerts);
  **7** subtle border on interactive components; **8** stronger border and focus ring
- **9** solid background — "has the highest chroma of all steps in the scale";
  covers accent borders, logos, overlays. **10** its hover state
- **11** low-contrast text; **12** high-contrast text

Radix guarantees 11 and 12 against a **step 2** background (not step 1), and the
guarantee is in **APCA Lc — step 11 to Lc 60, step 12 to Lc 90** — not WCAG ratios.
That is why the recommendation above re-measures in WCAG terms rather than trusting a
step number.

Radix aliasing docs (<https://www.radix-ui.com/colors/docs/overview/aliasing>) map one
scale to `--accent-1 … --accent-12` and use gray/slate for neutral roles; they do not
state a cap on the number of scales, and their own examples run four or five
(blue, green, yellow, red, + gray).

What Radix would give this presentation: the step→role contract. It is the right mental
model for "which grape do I use for a fill vs a stroke vs a label". Not recommended as
the palette itself, because Open Color is what Excalidraw's geometry already belongs to,
and Radix's steps are tuned for interactive UI states this static page has none of.

### IBM Carbon

- Accessibility colour guidance (<https://carbondesignsystem.com/guidelines/accessibility/color/>):
  body text and images of text **4.5 : 1**; large text — defined as at least **24px
  regular/light or 19px semi-bold** — **3 : 1**; UI components' state and boundary cues
  **3 : 1** against adjacent colours, citing WCAG 1.4.11. Text over gradients or images
  must meet contrast *everywhere it appears*, and parallax or animated layouts are
  flagged as the risk case. And: "Don't rely on color alone to convey meaning" —
  covering conveying information, indicating an action, prompting a response, and
  distinguishing one element from another; it suggests checking with a colour-blindness
  simulator.
- Data-visualization colour palettes (<https://carbondesignsystem.com/data-visualization/color-palettes/>):
  the 14-colour categorical palette "should be applied in sequence strictly as
  described", and the sequence is "carefully curated to maximize contrast between
  neighboring colors" — purple 70 `#6929c4`, cyan 50 `#1192e8`, teal 70 `#005d5d`,
  magenta 70 `#9f1853`, red 50 `#fa4d56`, red 90 `#570408`, green 60 `#198038`,
  blue 80 `#002d9c`, magenta 50 `#ee538b`, yellow 50 `#b28600`, teal 50 `#009d9a`,
  cyan 90 `#012749`, orange 70 `#8a3800`, purple 50 `#a56eff`. You may override the
  sequence with a fixed single colour (purple 70, blue 80, cyan 50 or teal 70) when the
  number of categories is predictable. Carbon does **not** state a numeric cap on hues,
  and it discourages multiple gradients in one chart.
- Carbon's colour usage page (<https://carbondesignsystem.com/elements/color/usage/>)
  is about layer tokens, not accent counts; it states that all colour should be redlined
  with Carbon tokens because hard-coded values do not follow a mode switch — the same
  argument for keeping every value in `presentation.html` behind a custom property.

What Carbon would give this presentation: the ordered-sequence idea (pick hues in a
fixed order chosen for neighbour contrast) and the "one fixed colour when the number of
categories is predictable" rule. This diagram set has a predictable, small number of
categories — so take the override, not the 14-step sequence.

### Tailwind

<https://tailwindcss.com/docs/colors> — 22 hues × 11 steps (50 lightest … 950 darkest),
described by Tailwind as "a vast, beautiful color palette out of the box, carefully
crafted by expert designers". It publishes values in **OKLCH** (with a nearest-hex
option in the picker) but states no rule for which step belongs to text vs background
vs border — only examples (`text-gray-950` headings, `text-gray-700`/`500` body,
`border-pink-300`, `bg-pink-100`). Sample values: amber-600 `oklch(66.6% 0.179 58.318)`,
orange-500 `oklch(70.5% 0.213 47.604)`, teal-600 `oklch(60% 0.118 184.704)`,
indigo-600 `oklch(51.1% 0.262 276.966)`.

What it would give this presentation: nothing Open Color does not, plus a conversion
step (the file is hex/hsl throughout) and no published step→role contract. Not
recommended. Its OKLCH basis would matter if the goal were wide-gamut P3, but YouTube's
recommended SDR pipeline is BT.709 8-bit 4:2:0 anyway.

### Catppuccin

<https://github.com/catppuccin/palette/blob/main/palette.json> — published, versioned,
four flavours with named roles. Latte (light): base `#eff1f5`, mantle `#e6e9ef`,
crust `#dce0e8`, text `#4c4f69`, subtext0 `#6c6f85`, surface0–2
`#ccd0da`/`#bcc0cc`/`#acb0be`, overlay0–2 `#9ca0b0`/`#8c8fa1`/`#7c7f93`, and accents
rosewater `#dc8a78`, flamingo `#dd7878`, pink `#ea76cb`, mauve `#8839ef`, red `#d20f39`,
maroon `#e64553`, peach `#fe640b`, yellow `#df8e1d`, green `#40a02b`, teal `#179299`,
sky `#04a5e5`, sapphire `#209fb5`, blue `#1e66f5`, lavender `#7287fd`. Mocha (dark):
base `#1e1e2e`, mantle `#181825`, crust `#11111b`, text `#cdd6f4`, subtext0 `#a6adc8`,
surface0–2 `#313244`/`#45475a`/`#585b70`, overlay0–2 `#6c7086`/`#7f849c`/`#9399b2`,
accents rosewater `#f5e0dc`, flamingo `#f2cdcd`, pink `#f5c2e7`, mauve `#cba6f7`,
red `#f38ba8`, maroon `#eba0ac`, peach `#fab387`, yellow `#f9e2af`, green `#a6e3a1`,
teal `#94e2d5`, sky `#89dceb`, sapphire `#74c7ec`, blue `#89b4fa`, lavender `#b4befe`.

What it would give this presentation: the most personality of any option, and a genuine
light/dark pair with matched role names — a near drop-in for the file's two-theme
structure. Two reasons it is the runner-up rather than the pick: Latte's `text #4c4f69`
is a low-contrast body ink by design (it is an editor theme, tuned for syntax
differentiation, not for a 360p rendition), and Mocha's accents are pastels around
70–85% lightness, which is the right call for a dark editor but gives up the luma
separation a compressed stream needs when the same colour has to work on light too.
If the brief ever becomes "code-editor aesthetic", Catppuccin is the answer.

### Rosé Pine

<https://rosepinetheme.com/palette/> publishes three variants (Rosé Pine, Moon, Dawn)
with 15 named roles each — base, surface, overlay, muted, subtle, text, love, gold,
rose, pine, foam, iris, and three highlight levels. The hex values live on the
per-role pages (`/palette/base` etc.) rather than the index, so they are not quoted
here. Same verdict as Catppuccin: a beautiful editor palette whose low-contrast muted
roles are the wrong starting point for video, and with no published contrast data.

---

## 4. Applying one accent family with restraint to a hand-drawn diagram

Four rules, each tied to a source that states it.

**1. Ink is not accent. The drawing stays monochrome; colour marks, it does not draw.**
WCAG 1.4.11 requires 3 : 1 for "parts of graphics required to understand the content"
(<https://www.w3.org/TR/WCAG22/#non-text-contrast>). Every stroke in these diagrams —
every box edge, arrow, arrowhead, cross, cylinder wall — is required to understand the
content, so every one of them must hold 3 : 1 on its own. Ink at 14.99 : 1 does;
orange-900 at 3.87 : 1 does but with almost no margin for the encoder to eat. Keep the
geometry in ink and spend accent on emphasis.

**2. Colour is never the only carrier of a distinction.** Carbon states it plainly:
"Don't rely on color alone to convey meaning", covering conveying information,
indicating an action, and "distinguishing one visual element from another"
(<https://carbondesignsystem.com/guidelines/accessibility/color/>). The diagrams already
honour this — `tenant-context.html` uses a *dotted* arrow for the tenant the request
never reaches, `tenant-isolation.html` draws a *cross*. Keep the dash pattern and the
cross; let red be the second signal, not the first.

**3. Filled regions, not coloured lines.** Accent goes on area. Measured, over
`#f1f3f5`:

| Fill | Composite | vs background | Ink on it |
| --- | --- | --- | --- |
| grape-800 @ 8% | `#eae4f0` | 1.12 : 1 | 13.38 : 1 |
| grape-800 @ 12% | `#e7dced` | 1.19 : 1 | 12.59 : 1 |
| grape-800 @ 18% | `#e2d1e9` | 1.30 : 1 | 11.54 : 1 |
| teal-900 @ 12% | `#d5e7e4` | 1.15 : 1 | 13.00 : 1 |
| orange-900 @ 12% | `#f0e1d9` | 1.15 : 1 | 13.08 : 1 |

**12% is the sweet spot**: the region is clearly tinted, and the ink over it still holds
~12.6 : 1, far above the 4.5 : 1 floor. The alternative is Excalidraw's own index-1
(weight 200) backgrounds — grape-100 `#f3d9fa` reads 1.17 : 1 against the background
with ink at 12.79 : 1 on it, which is the same place by a different route. Either works;
the alpha version has the advantage that one `--accent` value drives both the stroke and
the fill.

A fill at 1.1–1.3 : 1 against the page is *below* 3 : 1 — that is intentional and
allowed: the fill is not a part of the graphic required to understand the content, it is
a grouping cue, and the boundary it reinforces is already drawn in ink at 14.99 : 1.

**4. How many accent hues one diagram can hold.** No first-party source states a hard
number, so this is a reasoned limit, not a quoted one:

- Radix's model is **one** accent scale aliased to `--accent-1…12`, plus a gray
  (<https://www.radix-ui.com/colors/docs/overview/aliasing>); its own examples extend to
  four or five scales, and all of those extras are *semantic* (green = success,
  yellow = warning, red = danger), not decorative.
- Carbon's categorical sequence is ordered to "maximize contrast between neighboring
  colors" and it permits a **single fixed colour** when the number of categories is
  predictable (<https://carbondesignsystem.com/data-visualization/color-palettes/>).

Both point the same way: **one accent per diagram, by default.** Two when the diagram
draws a genuine pair (`tenancy-models` draws B2C beside B2B — one accent each is the
whole point). Three only when the third is a semantic state, not a third category
(`tenant-isolation`: ink for the structure, grape for the tenant in scope, red for the
blocked call). Four hues in one drawing is where it stops being a diagram with emphasis
and becomes a chart, at which point the reader starts decoding a legend instead of
following the shape. Reserve red for negation everywhere, so that red always means the
same thing across all eight components.

Per-component assignment that follows from this:

| Component | Accents |
| --- | --- |
| `tenancy-models` | grape (B2B) + ink (B2C) — the asymmetry is the point |
| `onboarding` | grape on the provisioned tenant resources only |
| `identity` | grape for owner, teal for member |
| `tenant-context` | grape on the routed path; the unreached tenant stays ink + dotted |
| `tenant-isolation` | grape in-scope, red on the cross |
| `core-entities` | grape on the store (cylinder + the three tables); steps stay ink |
| `api-sequence` | the three bands take 12% fills: ink/gray (Unsecured), teal (User scoped), grape (Tenant scoped); all strokes ink |
| `worked-examples` | keep `--slack-ink` `#4a154b` and `--gws-ink` `#1a73e8`; they are logotypes, exempt under WCAG 1.4.3's logotype exception (<https://www.w3.org/TR/WCAG22/#contrast-minimum>) |

---

## 5. How to apply it here

**Do not make these changes yet — this section is the mechanism, not a patch.**

### 5.1 `presentation.html` — the custom properties

All three palette blocks live in the second `<style>` element, near the top:

- `:root{…}` (the light theme) — currently `--bg:#f6f1e6` … `--display-tracking:-.015em`
- `@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){…}}`
- `:root[data-theme="dark"]{…}` — a verbatim duplicate of the media-query block

Every value must change in **all three** blocks or the themes diverge. The tokens to
re-point, with their current values:

| Token | Now (light) | Now (dark) | Note |
| --- | --- | --- | --- |
| `--bg` | `#f6f1e6` | `#131110` | → `#f1f3f5` / `#212529` |
| `--surface` | `#fbf6ec` | `#1a1715` | → `#f8f9fa` / `#343a40` |
| `--surface-2` | `#efe7d6` | `#221e1a` | → `#e9ecef` / gray-7 `#495057` |
| `--ink` | `#25201b` | `#f4f0e3` | → `#1e1e1e` / `#f8f9fa` |
| `--muted` | `#4a4239` | `#c8c1ae` | → `#495057` / `#ced4da` |
| `--line` | `#d9cfb9` | `#2a2622` | → `#dee2e6` / `#343a40` |
| `--line-strong` | `#b8ad9b` | `#4f4a42` | → `#adb5bd` / `#495057` |
| `--accent` | `#8a4423` | `#c89761` | → `#9c36b5` / `#e599f7` |
| `--wire` | `#b8ad9b` | `#4f4a42` | → `#adb5bd` / `#495057`; used by `.wires path{stroke:var(--wire)}` |
| `--theme-text` | `28deg 16% 13%` | `42deg 35% 92%` | **this is the diagram ink** → `0deg 0% 12%` / `210deg 17% 98%` |
| `--slack-ink` | `#4a154b` | `#c99dca` | leave: logotype |
| `--gws-ink` | `#1a73e8` | `#8ab4f8` | leave: logotype |
| `--shadow` | rgba on `37,32,27` | rgba on black | re-tint to `33,37,41` so the shadow is not warm against a cool ground |

Tokens to **add** (same three blocks), because nothing equivalent exists today:

```
--accent-2        /* #087f5b light / #63e6be dark */
--accent-3        /* #d9480f light / #ffc078 dark */
--accent-danger   /* #c92a2a light / #ffa8a8 dark */
--accent-soft     /* colour-mix or rgba at 12% of --accent */
```

Also: the bare `<style>` in `<head>` hard-codes `body{…background:#fafafa}` as the
pre-font flash colour — change it to `#f1f3f5` or the first paint flashes the wrong
ground on camera. And `color-scheme:light dark` on `:root` stays as is.

`.draft-badge` uses `--accent`; with grape it becomes a purple "DRAFT" chip. Either
re-point it to `--muted` or drop the badge for the recording.

### 5.2 Type scale, same file

`h1{font-size:clamp(30px,4.6vw,42px)}`, `h2{clamp(22px,3vw,27px)}`,
`h3{clamp(18px,2.4vw,21px)}`, `body{font-size:16px}`, `.eyebrow{font-size:.72rem}`,
`.page{max-width:1080px}`, `--step:clamp(1.8rem,1.2rem+1.8vw,3rem)`. Per §1, raise the
body step and the page width together; the headings are already relative so they follow
`vw`, but their `clamp` ceilings (42/27/21px) will cap out and need lifting too.

### 5.3 `components/rough.py` and the eight generators

Today the colour path is: each component's `<figure>` sets
`color:hsl(var(--theme-text, 28deg 16% 13%))`, the SVG root sets
`stroke="currentColor" fill="none"`, every `rough.py` primitive emits a `<path>` with
**no** stroke attribute (so it inherits), and `text()`/`label()` emit
`fill="currentColor" stroke="none"`. One `color` drives the whole drawing. That is why
the accent cannot currently reach the ink.

Two ways to break the single-colour assumption. **Prefer (A).**

**(A) Group-scoped `currentColor` — no change to any primitive.**
`currentColor` resolves per element, so re-declaring `color` on an SVG `<g>` recolours
every descendant stroke *and* every text fill, with no new attributes anywhere.

1. Add one helper to `rough.py`, beside `frame()`:

   ```python
   def group(content, cls):
       """Wrap geometry in a <g> whose class re-declares `color`."""
       return f'<g class="{cls}">{content}</g>'
   ```

2. In each `*.gen.py`, wrap only the geometry that should take accent:
   `group(arrow(...) + label(...), "dg-accent")`.

3. Extend the `<style>` block that every generator already emits — the one that sets
   `--dg-font-hand` and `color` — with the accent classes:

   ```css
   .diagram-core-entities .dg-accent  { color: var(--accent,        #9c36b5); }
   .diagram-core-entities .dg-accent-2{ color: var(--accent-2,      #087f5b); }
   .diagram-core-entities .dg-danger  { color: var(--accent-danger, #c92a2a); }
   .diagram-core-entities .dg-fill    { fill:  var(--accent-soft, rgba(156,54,181,.12)); stroke: none; }
   ```

   The `var(--accent, …)` fallback matters: each component is also a standalone file
   (`core-entities.html` opened directly) where `--accent` is undefined, exactly as
   `--theme-text` already carries the fallback `28deg 16% 13%`.

4. Filled regions need the SVG root's `fill="none"` overridden locally. Add a
   `fill_rect()` to `rough.py` that emits a plain (non-sketchy) `<rect>` or a `<path>`
   with `fill="var(--accent-soft)" stroke="none"`, drawn *before* the stroke pass so the
   ink sits on top.

5. Run the generators, then `python3 references/designing-a-multi-tenant-system/components/sync.py`
   from the repository root. The README's rule holds: never edit a copy by hand.

**(B) Per-primitive `color=` kwarg.** Thread an optional colour through
`path()` (line 60 — the single chokepoint for every stroked shape, since `rect`,
`srect`, `ellipse`, `arrow`, `sarrow`, `cylinder` and `frame` all funnel through it) and
separately through `text()` (line ~128, hard-coded `fill="currentColor"`) and `label()`
(line ~140, same, plus `opacity="0.85"`). Each would emit
`stroke="var(--accent, #9c36b5)"` / `fill="var(--accent, #9c36b5)"` when given a colour.
More call-site churn, two places to keep in sync for strokes vs text, and `cylinder()`
would need to forward the colour to its three internal `path()` calls. Only worth it if
a single shape ever needs a stroke colour different from its own label.

### 5.4 Follow-on files

- `worked-examples.gen.py` lifts the Slack and Google panels, the brand sprite and the
  panel CSS straight out of `presentation.html` and scopes it under `.diagram-worked`.
  It picks up the new tokens for free — but re-run it after editing the presentation,
  then `sync.py`.
- `README.md`'s component table says of several files "It draws in `currentColor`, so
  one drawing serves the light and the dark theme." Under (A) that stays true (the
  groups re-declare `color`, still one drawing for both themes); under (B) it does not,
  and the table needs rewording.
- `src/styles/global.css` and `src/content/articles/designing-a-multi-tenant-system.md`
  are the *article*, which keeps the paper-cream site palette. The components are shared
  between the article and the presentation via `sync.py`, so any accent added to a
  component appears on the site too — the `var(--accent, fallback)` form means the
  article renders them in the site's `#8a4423`, not grape, which is the right outcome.
  Verify after the first sync.

### 5.5 Capture settings that follow from §1 and §2

- Record the **light theme**, 1920×1080 at 30 fps, browser window ~1280–1440 CSS px
  wide, zoomed so body text lands near 3% of frame height.
- Keep content inside the EBU R 95 graphics safe area: 5% / 96px left and right,
  54px top and bottom of a 1080 frame.
- Export H.264 High Profile, 4:2:0, closed GOP of 15, VBR at **8 Mbps or above** for
  1080p30 per YouTube's own table; uploading at 1440p (16 Mbps) buys a better 1080p
  rendition because YouTube transcodes down from what you give it.
- Check the result at the Data-saver rendition, not just at 1080p: that is where a
  1.8px accent stroke disappears and where the ink-only decision pays off.
