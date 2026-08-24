# Deploy

Full project context is in [CLAUDE.md](CLAUDE.md). This file is the short operational loop.

Live: <https://ridge-dinosaurs-prompts.vercel.app>
Vercel project `ridge-dinosaurs-prompts`, scope `ratmir-s-projects1`.

## Change something

1. Page copy, shot text, order, posters, reel link: `_build/build.py`
2. Design, CSS, JS, page shell, the stats band numbers: `_build/index.template.html`
3. Prompt text itself: the `PromptN.txt` files in `../Dinosaurs`

## Rebuild

```bash
python _build/build.py
```

Regenerates `index.html`, the per shot `.txt` files and the pack zip. Media is only rebuilt when the
output file is missing, so delete the specific webp, poster or mp4 you want redone.

## Ship

```bash
vercel deploy --prod --yes --scope ratmir-s-projects1
```

Then keep the repo in step:

```bash
git add -A && git commit -m "update" && git push
```

Pushing does not deploy by itself. To make it deploy, open the project on vercel.com, Settings, Git,
Connect Git Repository, pick `Ratmir123/dinosaurs`. After that the CLI command becomes optional.

## Custom domain

Add the domain in the project settings on vercel.com, then point the registrar at Vercel: CNAME to
`cname.vercel-dns.com` for a subdomain, or an A record to `76.76.21.21` for an apex domain. HTTPS is
issued automatically. Then set `SITE_URL` at the top of `_build/build.py` and rebuild, so link
previews point at the new address too.

## Sanity check after a deploy

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://ridge-dinosaurs-prompts.vercel.app/
```

```bash
curl -sI https://ridge-dinosaurs-prompts.vercel.app/dinosaurs-prompt-pack.zip | grep -i -E "content-length|content-disposition"
```

The zip should report 14833433 bytes until the pack contents actually change.
