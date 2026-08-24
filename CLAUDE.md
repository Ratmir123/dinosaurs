# Dinosaurs, prompt pack

Read this before touching anything in this folder.

## What this is

The second free prompt pack given away to Ratmir's Instagram audience (@by.ridge, brand name Ridge).
Same machine as the Odyssey pack, different subject. Someone comments a keyword under the reel, an
Instagram automation DMs them this link, and the page hands over everything used to make the shots.

Five shots on one question: what if dinosaurs were still alive, and friendly? A T-rex on a leash at
the kerb, an ankylosaurus in a goal mouth, a sauropod being used as a slide, a baby dinosaur at the
vet, a triceratops running a bus route. For each step
the page shows the finished clip, the full prompt with a copy button, and a short note on what the
prompt is actually doing. One zip holds all of it.

**The thing that makes this pack different from the Odyssey one: there are no reference images.**
Four of the five prompts were run with nothing attached at all. Everything in the picture is written
out in the text, which is why the prompts are 2,800 to 3,800 words each. Shot 05 attaches exactly one
file, the Ridge logo painted onto the animal's flank, and the prompt states in two separate blocks
that the file is artwork only and that nothing else in the frame takes any appearance from it.

The pack is deliberately ungated. No email, no sign up, no form. The follow ask lives in the DM flow,
not on the page.

## Live

| | |
|---|---|
| URL | https://ridge-dinosaurs-prompts.vercel.app |
| Hosting | Vercel, project `ridge-dinosaurs-prompts`, scope `ratmir-s-projects1` |
| Repo | https://github.com/Ratmir123/dinosaurs (public) |
| Deploys | CLI only. The Vercel GitHub App is not installed, so pushing to GitHub does not deploy |

The Odyssey pack is a separate project in a separate folder (`../the-odyssey-site`) with its own
repo and its own Vercel project. The two share a design system and nothing else. Do not touch it
from here.

## Layout

```
index.html                     the entire page, CSS and JS inlined, generated
assets/v/*.mp4                 web encodes of the five shots, 1.5 to 3 MB each, lazy loaded
assets/p/*.jpg                 video posters
assets/r/logo.webp             the one reference shown on the page
assets/txt/*.txt               per shot prompt downloads
assets/og.jpg                  link preview card
dinosaurs-prompt-pack.zip      14 MB, the actual giveaway, generated
vercel.json                    cache headers, forces the zip to download instead of opening
_build/build.py                the generator, single source of truth for page copy and structure
_build/index.template.html     the design: all CSS, all JS, the shell around the generated parts
CLAUDE.md, DEPLOY.md           docs, not uploaded to the site
```

`index.html` and the zip are build output. Never hand edit them, the next build overwrites both.
Page copy lives in `_build/build.py`, design lives in `_build/index.template.html`.

## Source of truth for content

Raw prompts and clips live outside this repo, next to it:

```
Desktop/Dinosaurs/1)T-rex/          Prompt1.txt, T-rex.mp4
Desktop/Dinosaurs/2)FootballDino/   Prompt2.txt, Football.mp4
Desktop/Dinosaurs/3)SlideDino/      Prompt3.txt, Slide.mp4
Desktop/Dinosaurs/4)CuteDino/       Prompt4.txt, Cute.mp4
Desktop/Dinosaurs/5)BusDino/        Prompt5.txt, Bus.mp4, Ridge2DLogo.png
```

`build.py` finds it at `../Dinosaurs` relative to this folder, or wherever `DINO_SRC` points.
Editing a `PromptN.txt` there and rebuilding updates the page and the zip together.

**If that folder is gone**, the pack zip in this repo contains every prompt, the logo at full
resolution and a usable encode of every clip, so the content is recoverable from the repo alone.
The only things not in it are the high bitrate master mp4s, and the build keeps the existing
`assets/v/*.mp4` rather than re-encoding when the masters are missing.

## Commands

Rebuild after any edit:

```bash
python _build/build.py
```

Deploy to production:

```bash
vercel deploy --prod --yes --scope ratmir-s-projects1
```

Keep the repo in step:

```bash
git add -A && git commit -m "update" && git push
```

Media is only regenerated when the output file is missing, so delete the specific webp, poster or
mp4 you want redone. Deploys deduplicate unchanged files by hash, so a redeploy uploads only what
actually moved.

## Design system

Same system as the Odyssey pack, one colour axis moved. Do not drift from it.

- **Type**: Archivo, variable width axis, `font-stretch: 112-118%` on display sizes. Geist Mono for
  data, labels and prompt text. Inter is banned, it is the training data default.
- **Colour**: OKLCH only, no pure black. Warm red tinted charcoal ramp `--ink`, `--ink-2`, `--ink-3`.
  One accent, `--accent`, a pastel red at `oklch(0.790 0.118 24)`, which is the sRGB gamut edge for
  that hue and lightness. Push the chroma any higher and the red channel clips, the browser clamps
  it, and the token stops meaning what it says. The stats band is the single drenched surface.
- **Type scale**: 11 / 13 / 15 / 17 px plus display clamps. Weights 400, 500, 700, nothing else.
- **Spacing**: 4 px grid for padding, radii and control heights.
- **Motion**: one curve, `--out: cubic-bezier(.23,1,.32,1)`. Only transform and opacity animate.
  Every pressable element scales to .97 on `:active`.
- **Banned**: neon glows, gradient text, glassmorphism, side stripe borders, three identical cards
  in a row, hero metric card grids.
- **Contrast**: measured in the browser, not guessed. Body text 5.2:1 or better, band labels 5.4:1
  or better. Current floor is `--dim` on `--ink` at 5.34:1 and the band labels at 5.92:1. Recheck by
  painting each token to a canvas and reading the pixels back, because `getComputedStyle` returns
  the `oklch()` string and a naive parser will read it as RGB and report nonsense.

The Odyssey band labels sit at 74% opacity. Here they are at 80%, because the pastel red band is
lighter than the acid lime one and 74% did not clear 5.4:1. Do not copy that number back across.

## Copy rules

- English. Sentence case. No emoji anywhere.
- **No em dashes, no en dashes.** Commas, colons, periods, parentheses. Checked with a script, the
  page has zero outside the prompt blocks. Keep it that way.
- No AI filler: elevate, seamless, unleash, dive in, game changer, unlock.
- Tone is a producer talking to another operator. Concrete, unbothered, no hype.
- The prompts themselves are never edited. Their em dashes and their length are the author's.

## Decisions already made

Do not quietly reverse these.

- **The stats band says `200,000` and `views in the first ten hours`.** Taken from the Instagram
  insights panel at capture: 23,811 interactions, 17,975 likes, 3,505 shares, 1,559 saves, all
  rounded up to 24K / 18K / 3.5K / 1.5K for presentation. Numbers are hardcoded in
  `index.template.html` inside `<section class="proof">`. Comments (61) are deliberately not shown.
- **The page sells the premise, not the format.** The hero asks "what if dinosaurs were still
  alive, and friendly?" and the two meta descriptions say the same thing. An earlier draft led with
  "it is 2003, somebody has a camcorder, and dinosaurs are boring" and Ratmir cut it: boring is what
  the shots are doing, not what the visitor is being offered. The 2003 camcorder look stays as a
  fact, on the per shot chips and as a trailing clause, never as the hook.
- **`REEL_URL` in `build.py` points at the profile, not the post.** The reel URL was not known when
  the page was built. Set it to the actual post and rebuild.
- **The model is not named on the page.** Chips say `16:9`, `SFX only`, `2003 camcorder`, all facts
  pulled from the prompts. Durations come from `ffprobe` on the masters.
- **There is no character sheet step.** The Odyssey pack opened with step 00 because four shots
  shared one face. Nothing is shared here, so the page is five shots and nothing else, and the
  `References` block only renders for the shot that actually has one.
- **The clips ship inside the zip.** The Odyssey zip was prompts and reference images only, and it
  was 45 MB of PNGs. This pack has almost no images, so without the clips the download would be
  four megabytes of text. The web encodes are the same frame size as the masters (1280x720) at
  crf 21, which keeps the zip at 14 MB and the download fast.
- **Reference tokens are cleaned at build time.** Copying an asset chip out of Higgsfield pastes
  `@[name](internal-id)`. The id belongs to Ratmir's library and is stripped by a regex in
  `read_prompt()`, leaving `@name`. These five prompts happen to carry no tokens, but the guard
  stays so a future edit cannot leak one.
- **The reference tile is padded, not cropped.** The one attached file is a square logo on
  transparency and a 16:9 cover crop ate it. `ref_webp()` trims the alpha bounding box, drops the
  mark onto an `--ink-2` canvas at 62% and letterboxes it to 16:9, so it matches every other tile
  on the page without being mangled.
- **The lightbox hides its arrows when a group holds one image.** `.lb.single` exists because
  `1 / 1` with two dead arrows under it looks broken.
- **The expand button under each prompt** centres with `transform: translateX(-50%)` alone. Mixing
  the `translate` property with a `transform` in `:active` double shifted it and clicks missed.
  When open it becomes `position: sticky` so it does not fly to the bottom of a 9000 px panel.
- **Scroll reveal is fail safe.** It measures rects on scroll, reveals anything already scrolled
  past, and force reveals after six seconds. The hidden state only applies when JS is running.

## Distribution

An Instagram comment on the breakdown post triggers an automated DM carrying this link. Keywords
should be spelling variants of "dinosaur" in Latin and Cyrillic, never short fragments, so the bot
only answers people who meant it. The DM asks for a follow before sending the link and says so
plainly, without pretending the platform requires it.

The automation is not wired up yet for this pack. Copy the Odyssey flow and swap the keyword set
and the link.

Suggested caption CTA: *All of it is free. Comment DINO and I will send you the five prompts and
the finished clips. No references needed, it is all in the text.*

## Known limits

- Vercel Hobby includes 100 GB of transfer a month. The 14 MB pack turns that into roughly 7,000
  downloads. The page itself is under a megabyte.
- Hobby is formally non commercial. A free pack under a personal brand is a grey area.
- First load is about 550 KB. Videos only download on play.
- This project and the Odyssey project share the same Vercel Hobby transfer allowance.

## History

- 2026-08-24: built and published, cloned from the Odyssey pack with a new palette, five video
  shots and no character sheet step.
