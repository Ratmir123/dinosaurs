# -*- coding: utf-8 -*-
"""
Builds the public "Dinosaurs" prompt pack page.

Paths are derived from this file's location, so the whole project can be moved
or cloned anywhere. The only outside dependency is the folder of raw prompts,
expected next to the site folder as "Dinosaurs". Override it with the DINO_SRC
environment variable if you keep it somewhere else.

Run:  python _build/build.py
"""

import html
import os
import re
import subprocess
import zipfile
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent      # the site folder, deployed as is
BUILD = Path(__file__).resolve().parent           # this folder, never deployed
SRC = Path(os.environ.get("DINO_SRC") or (OUT.parent / "Dinosaurs"))

A_VID = OUT / "assets" / "v"
A_POS = OUT / "assets" / "p"
A_REF = OUT / "assets" / "r"
A_TXT = OUT / "assets" / "txt"
ZIP_NAME = "dinosaurs-prompt-pack.zip"

# where the site actually lives, used for absolute link-preview urls.
# change this line first if the page moves to a custom domain.
SITE_URL = "https://ridge-dinosaurs-prompts.vercel.app"

# the reel the proof band points at. profile link until the post url is known.
REEL_URL = "https://www.instagram.com/by.ridge/"

FFMPEG = "ffmpeg"

# ink-2, so a transparent reference lands on the same surface the page uses
REF_BG = (24, 18, 17)

# --------------------------------------------------------------------------
# scene data
# --------------------------------------------------------------------------

SCENES = [
    dict(
        id="trex",
        num="01",
        title="The Leash",
        nav="Leash",
        folder="1)T-rex",
        video="T-rex.mp4",
        prompt="Prompt1.txt",
        poster_t=1.95,
        deck="A boy walks his cat-sized pet raptor down the pavement. A man in a suit lights a cigar with the steel "
             "leash of a full-grown T-rex hanging slack from his fist. Nobody in the frame finds any of it worth "
             "looking at. The only reaction in the shot belongs to whoever is holding the camera.",
        look=[
            "Scale is proven with objects, not adjectives. His head rides level with the roof ridges, one foot is as long as the parked sedan is wide, and the frame cannot hold his feet and his head at the same time.",
            "The camera never walks. It holds one spot on the house side of the street for all eight seconds and gets closer only by zooming, so the compression changes and the parallax does not.",
            "The reveal is a tilt up the cable. It starts on a fist, climbs a leg that fills the frame edge to edge, and ends on a bored head against a blown out sky.",
        ],
        refs=[],
    ),
    dict(
        id="football",
        num="02",
        title="The Tail",
        nav="Tail",
        folder="2)FootballDino",
        video="Football.mp4",
        prompt="Prompt2.txt",
        poster_t=6.25,
        deck="A player strikes at a goal with an ankylosaurus standing in it. The animal is grazing and never lifts "
             "his head. The tail swats once, flat and level, and the ball goes the whole length of the pitch into the "
             "other net.",
        look=[
            "Both goals stay inside the same framing for the first three seconds, so the distance the ball covers is something the viewer measures instead of being told.",
            "The tail is written as a stiff lever driven from the hips, swinging in one flat horizontal plane. Write it as a whip and it curls, and the hit stops reading as weight.",
            "Every human in the shot is astonished and the animal is not. The whole thing lives in that gap, so nobody mugs, nobody performs and nobody looks at the lens.",
        ],
        refs=[],
    ),
    dict(
        id="slide",
        num="03",
        title="The Slide",
        nav="Slide",
        folder="3)SlideDino",
        video="Slide.mp4",
        prompt="Prompt3.txt",
        poster_t=0.30,
        deck="A sauropod lies across a courtyard and four kids use him as playground equipment: up the tail, along "
             "the back, down the neck into the sandpit. The old woman on the bench has read through this every "
             "afternoon for years and does not look up once.",
        look=[
            "One focal length for the whole take and no zoom anywhere. The framing changes only because the operator turns, which is what keeps it reading as an afternoon somebody filmed rather than a shot somebody designed.",
            "The animal barely moves and still acts. A ribcage, two nostrils and one open wet eye tracking each kid down the neck and rolling back is the entire performance.",
            "The tell is a stripe of hide along the top of the neck, worn smooth and polished pale. One detail that says this has been happening for years.",
        ],
        refs=[],
    ),
    dict(
        id="vet",
        num="04",
        title="The Check Up",
        nav="Check up",
        folder="4)CuteDino",
        video="Cute.mp4",
        prompt="Prompt4.txt",
        poster_t=6.35,
        deck="A months-old dinosaur on a vet's steel table, shaking the way a small frightened dog shakes. Her girl "
             "waits beside her with her hands on the table because she has been told not to interfere. The moment "
             "it is over she takes hold of her.",
        look=[
            "The shaking is written as a constant, present in every frame, spiking on contact and settling back. It is the thing the shot is actually built on.",
            "Whatever the vet is holding never comes into view. His own back and near shoulder stay between his hands and the lens for the rest of the take, so the picture carries her reaction and nothing else.",
            "Baby proportions get spelled out: oversized head, oversized feet, almost no muzzle, soft skin that compresses where it is touched. Leave that out and you get a small adult reptile.",
        ],
        refs=[],
    ),
    dict(
        id="bus",
        num="05",
        title="The Bus",
        nav="Bus",
        folder="5)BusDino",
        video="Bus.mp4",
        prompt="Prompt5.txt",
        poster_t=0.55,
        deck="A triceratops at a roadside stop with an open passenger rig strapped to his back. He is not an animal "
             "being ridden, he is a vehicle that breathes. The last passenger boards, the conductor slaps his flank "
             "twice, and he pulls away from the kerb like a bus.",
        look=[
            "The logo is the only attached file in this pack, and the prompt says out loud that it is artwork and nothing else. No character, no style, no environment comes from it.",
            "The mark is written as paint on living skin: matte, chalky, hairline cracked, dust in its lower edges, one corner rubbed thin where the harness crosses it. That is what stops it reading as a decal laid over the picture.",
            "The crash zoom lands on the flank and then holds almost still for a full second. Holding is what lets the letterforms stay stable frame to frame.",
        ],
        refs=[
            ("Ridge2DLogo.png", "logo", "Logo artwork",
             "Used as a flat graphic only, painted onto the hide inside the scene. Swap it for your own mark, or cut the block out entirely and the shot still runs."),
        ],
    ),
]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print("  ! ffmpeg failed:", " ".join(str(c) for c in cmd[:6]), "...")
        print(p.stderr[-800:])
    return p.returncode == 0


def fmt_bytes(n):
    if n >= 1024 * 1024:
        return f"{n / 1024 / 1024:.1f} MB"
    return f"{max(1, round(n / 1024))} KB"


def probe_duration(path):
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


def read_prompt(path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    txt = txt.replace("\r\n", "\n").strip() + "\n"
    # copying an asset chip out of Higgsfield pastes @[name](internal-id).
    # the id points at my library and means nothing to anyone else, so the
    # published prompt keeps the handle only: @name
    return re.sub(r"@\[([^\]]+)\]\([^)]*\)", r"@\1", txt)


def require_src():
    if not SRC.exists():
        raise SystemExit(
            f"source folder not found: {SRC}\n"
            "point DINO_SRC at the folder holding the numbered scene folders")


def ref_webp(src_path, dst_path):
    """Reference thumbnails are letterboxed onto ink-2 rather than cropped.

    The one reference in this pack is a square logo on transparency; a 16:9
    cover crop would eat it. Padding keeps the mark whole and keeps the tile
    the same shape as everything else on the page.
    """
    im = Image.open(src_path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        box = im.getbbox() or (0, 0, im.width, im.height)
        im = im.crop(box)
        flat = Image.new("RGB", im.size, REF_BG)
        flat.paste(im, (0, 0), im)
        im = flat
    else:
        im = im.convert("RGB")

    w, h = 1440, 810
    inner = im.copy()
    inner.thumbnail((round(w * 0.62), round(h * 0.62)), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), REF_BG)
    canvas.paste(inner, ((w - inner.width) // 2, (h - inner.height) // 2))
    canvas.save(dst_path, "WEBP", quality=86, method=6)


# --------------------------------------------------------------------------
# assets
# --------------------------------------------------------------------------

def build_media():
    for d in (A_VID, A_POS, A_REF, A_TXT):
        d.mkdir(parents=True, exist_ok=True)

    for s in SCENES:
        src_v = SRC / s["folder"] / s["video"]
        dst_v = A_VID / f"{s['id']}.mp4"
        dst_p = A_POS / f"{s['id']}.jpg"

        if not dst_v.exists():
            print(f"  encoding {s['id']}.mp4")
            run([FFMPEG, "-v", "error", "-y", "-i", str(src_v),
                 "-c:v", "libx264", "-preset", "slow", "-crf", "21",
                 "-profile:v", "high", "-level", "4.0", "-pix_fmt", "yuv420p",
                 "-movflags", "+faststart",
                 "-c:a", "aac", "-b:a", "128k", "-ac", "2",
                 str(dst_v)])
        if not dst_p.exists():
            run([FFMPEG, "-v", "error", "-y", "-ss", str(s["poster_t"]), "-i", str(src_v),
                 "-frames:v", "1", "-q:v", "3", str(dst_p)])

        # the web encode carries the same duration as the master, so the page can
        # be rebuilt even if the masters are not around
        s["duration"] = round(probe_duration(src_v if src_v.exists() else dst_v))

        for src_name, slug, role, note in s["refs"]:
            dst_r = A_REF / f"{slug}.webp"
            if not dst_r.exists():
                ref_webp(SRC / s["folder"] / src_name, dst_r)

        txt = read_prompt(SRC / s["folder"] / s["prompt"])
        s["prompt_text"] = txt
        (A_TXT / f"{s['id']}.txt").write_text(txt, encoding="utf-8")
        s["prompt_size"] = fmt_bytes(len(txt.encode("utf-8")))
        s["prompt_words"] = len(re.findall(r"\S+", txt))


def build_og():
    dst = OUT / "assets" / "og.jpg"
    if dst.exists():
        return
    src = SRC / "5)BusDino" / "Bus.mp4"
    font = "C\\:/Windows/Fonts/arialbd.ttf"
    vf = (
        "scale=1200:-2,crop=1200:630,"
        "eq=brightness=-0.06:saturation=1.02,"
        f"drawtext=fontfile='{font}':text='DINOSAURS':fontcolor=white:fontsize=92:"
        "x=72:y=352:shadowcolor=black@0.55:shadowx=0:shadowy=3,"
        f"drawtext=fontfile='{font}':text='FREE PROMPT PACK  /  5 SHOTS':fontcolor=0xFD9C95:"
        "fontsize=29:x=76:y=472:shadowcolor=black@0.6:shadowx=0:shadowy=2"
    )
    ok = run([FFMPEG, "-v", "error", "-y", "-ss", "0.55", "-i", str(src),
              "-frames:v", "1", "-vf", vf, "-q:v", "3", str(dst)])
    if not ok:
        run([FFMPEG, "-v", "error", "-y", "-ss", "0.55", "-i", str(src),
             "-frames:v", "1", "-vf", "scale=1200:-2,crop=1200:630", "-q:v", "3", str(dst)])


README = """DINOSAURS, PROMPT PACK
by Ratmir / Ridge

WHAT IS INSIDE
Five shots. Each folder holds the full prompt exactly as it was run and the
finished clip it produced.

  01 The Leash     prompt.txt + clip.mp4
  02 The Tail      prompt.txt + clip.mp4
  03 The Slide     prompt.txt + clip.mp4
  04 The Check Up  prompt.txt + clip.mp4
  05 The Bus       prompt.txt + clip.mp4 + logo artwork

THERE ARE NO REFERENCE IMAGES
Four of these five prompts were run with nothing attached. No character sheet,
no style board, no location plate. Everything in the picture is in the text,
which is the reason the text is this long. Shot 05 attaches one file, the logo
that gets painted onto the animal, and the prompt says out loud that the file
is artwork and that nothing else in the frame takes any look from it.

HOW TO RUN ONE
1. Paste prompt.txt into your generator.
2. For shot 05, load the logo into the reference slot. Or drop your own mark in
   its place, or delete the two logo blocks from the prompt and run it without.
3. Change nothing else on the first pass. Run it once as written, see what you
   get, and only then start pulling on it.

NOTES
These prompts are long on purpose. The length is not decoration. Every block is
there to kill a specific failure: a dinosaur that shrinks to horse size, a
second light source, a gimbal smooth camera, a tail that curls like a whip, an
animal that reacts to something it should ignore. Cut the "failed take" lines
and you get the failed take.

The clips in here are the web encodes, same frame size as the masters. They are
for reference and for reposting, not for grading.

Free to use, edit and post. No credit required. If it works, tell me,
I want to see it.

@by.ridge on Instagram
@cg_ridge on X
@by_ridge on YouTube
"""


def build_zip():
    dst = OUT / ZIP_NAME
    if dst.exists():
        dst.unlink()
    root = "Dinosaurs - Prompt Pack"
    print(f"  zipping {ZIP_NAME}")
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr(f"{root}/README.txt", README.replace("\n", "\r\n"))
        for s in SCENES:
            folder = f"{root}/{s['num']} {s['title']}"
            z.writestr(f"{folder}/prompt.txt", s["prompt_text"].replace("\n", "\r\n"))
            z.write(A_VID / f"{s['id']}.mp4", f"{folder}/clip.mp4")
            for src_name, slug, role, note in s["refs"]:
                z.write(SRC / s["folder"] / src_name, f"{folder}/references/{src_name}")
    return dst.stat().st_size


# --------------------------------------------------------------------------
# html
# --------------------------------------------------------------------------

def esc(t):
    return html.escape(t, quote=True)


def refs_html(s):
    if not s["refs"]:
        return ""
    figures = "\n".join(
        f'''          <figure class="ref">
            <button class="ref-shot" data-shot="{s['id']}" data-i="{n}" aria-label="Enlarge {esc(role)}">
              <img src="assets/r/{slug}.webp" alt="{esc(role)}" loading="lazy" decoding="async">
            </button>
            <figcaption>
              <span class="ref-role">{esc(role)}</span>
              <span class="ref-note">{esc(note)}</span>
            </figcaption>
          </figure>'''
        for n, (src_name, slug, role, note) in enumerate(s["refs"])
    )
    n_refs = len(s["refs"])
    plural = "file" if n_refs == 1 else "files"
    solo = " solo" if n_refs == 1 else ""
    return f'''
        <div class="block">
          <div class="block-head">
            <h3>Attached <em>{n_refs} {plural}, click to enlarge</em></h3>
          </div>
          <div class="refs{solo}">
{figures}
          </div>
        </div>'''


def prompt_html(s):
    return f'''
        <div class="block prose">
          <div class="block-head">
            <h3>Prompt <em>{s['prompt_words']} words, {s['prompt_size']}</em></h3>
            <div class="actions">
              <a class="btn ghost" href="assets/txt/{s['id']}.txt" download="dinosaurs-{s['id']}-prompt.txt">.txt</a>
              <button class="btn copy" data-copy="{s['id']}">
                <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>
                <span>Copy prompt</span>
              </button>
            </div>
          </div>
          <div class="prompt" data-open="false">
            <pre id="p-{s['id']}">{esc(s['prompt_text'])}</pre>
            <button class="expand">Show full prompt</button>
          </div>
        </div>'''


def shot_html(s):
    return f'''
      <section class="shot reveal" id="{s['id']}">
        <div class="shot-id">
          <span class="shot-num">{s['num']}</span>
          <span class="shot-rule"></span>
          <span class="shot-specs"><i>{s['duration']}s</i><i>16:9</i><i>SFX only</i><i>2003 camcorder</i></span>
        </div>
        <h2 class="shot-title">{esc(s['title'])}</h2>

        <figure class="player" data-video="assets/v/{s['id']}.mp4">
          <video preload="none" playsinline loop poster="assets/p/{s['id']}.jpg"></video>
          <button class="play" aria-label="Play {esc(s['title'])}">
            <span class="disc"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"/></svg></span>
            <span>Play the result</span>
          </button>
          <span class="load" aria-hidden="true">Loading</span>
        </figure>

        <div class="shot-body">
          <p class="deck">{esc(s['deck'])}</p>
          <ul class="look">
            {"".join(f"<li>{esc(x)}</li>" for x in s['look'])}
          </ul>
        </div>
{refs_html(s)}
{prompt_html(s)}
      </section>'''


def build_html(zip_size):
    tpl = (BUILD / "index.template.html").read_text(encoding="utf-8")
    shots = "\n".join(shot_html(s) for s in SCENES)
    nav = "\n".join(
        f'<a href="#{s["id"]}"><b>{s["num"]}</b>{esc(s.get("nav", s["title"]))}</a>' for s in SCENES)

    out = (tpl
           .replace("<!--SHOTS-->", shots)
           .replace("<!--NAV-->", nav)
           .replace("{{SITE}}", SITE_URL.rstrip("/"))
           .replace("{{REEL}}", REEL_URL)
           .replace("{{ZIP}}", ZIP_NAME)
           .replace("{{ZIP_SIZE}}", fmt_bytes(zip_size))
           .replace("{{N_PROMPTS}}", str(len(SCENES)))
           .replace("{{N_SHOTS}}", str(len(SCENES)))
           .replace("{{N_REFS}}", str(sum(len(s["refs"]) for s in SCENES)))
           .replace("{{N_WORDS}}", f"{sum(s['prompt_words'] for s in SCENES):,}".replace(",", " "))
           .replace("{{N_SECS}}", str(sum(s["duration"] for s in SCENES))))
    (OUT / "index.html").write_text(out, encoding="utf-8")
    return len(out.encode("utf-8"))


def main():
    print("building the dinosaurs pack")
    require_src()
    build_media()
    build_og()
    zsize = build_zip()
    hsize = build_html(zsize)
    print(f"  index.html  {fmt_bytes(hsize)}")
    print(f"  {ZIP_NAME}  {fmt_bytes(zsize)}")
    skip = {"_build", ".git"}
    total = sum(f.stat().st_size for f in OUT.rglob("*")
                if f.is_file() and not skip & set(f.parts))
    print(f"  deploy size {fmt_bytes(total)}")
    print("done ->", OUT)


if __name__ == "__main__":
    main()
