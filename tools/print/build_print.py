#!/usr/bin/env python3
"""Build Bookvault print files (interior 152x229 mm + cover) for one BookClassics title.

usage: build_print.py <slug> <book_dir> <out_dir>
prints one JSON line: {"slug", "pages", "interior", "cover", "lang"} or {"slug", "error"}
"""
import glob, html, json, os, re, subprocess, sys, tempfile

MAX_PAGES = 1071       # Bookvault 70gsm cream perfect bound
MIN_PAGES = 32
SPINE_MM_PER_PAGE = 0.056

slug, book_dir, out_dir = sys.argv[1:4]


def site_meta(slug):
    """Title, author, back-cover blurb and year from the public book page (JSON-LD)."""
    import urllib.request
    try:
        page = urllib.request.urlopen("https://bookclassics.org/books/%s/" % slug, timeout=30).read().decode("utf-8")
    except Exception:
        return {}
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        try:
            d = json.loads(blk)
        except Exception:
            continue
        for x in (d if isinstance(d, list) else d.get("@graph", [d])):
            if isinstance(x, dict) and x.get("@type") in ("Book", ["Book"]) and x.get("description"):
                desc = x["description"]
                m = re.search(r"Editions? in [^.]*\.\s*(.*)$", desc)
                desc = (m.group(1) if m else desc).strip()
                if desc.endswith("…"):
                    cut = max(desc.rfind(". "), desc.rfind("? "), desc.rfind("! "))
                    if cut > 40:
                        desc = desc[:cut + 1]
                    else:
                        c = desc.rfind(", ")
                        desc = desc[:c] + "." if c > 60 else desc.rstrip("…").rsplit(" ", 1)[0] + "."
                if desc.startswith("Read "):
                    desc = ""
                return {"blurb": desc, "year": str(x.get("datePublished") or "")}
    return {}


meta = site_meta(slug)


def fail(msg):
    print(json.dumps({"slug": slug, "error": msg}))
    sys.exit(0)


src = os.path.join(book_dir, slug + ".html")
if not os.path.exists(src):
    alts = sorted(glob.glob(os.path.join(book_dir, slug + "-??.html")))
    if not alts:
        fail("no html")
    src = alts[0]
doc = open(src, encoding="utf-8").read()
lang = (re.search(r'<html[^>]*lang="([a-z]{2})', doc) or [None, "en"])[1]
rtl = lang in ("ar", "he", "fa", "ur")


def clean(x):
    x = re.sub(r"<br\s*/?>", " ", x)
    x = re.sub(r"<[^>]+>", "", x)
    return re.sub(r"\s+", " ", html.unescape(x)).strip()


head_html = doc[: doc.find("</header>")] if "</header>" in doc else ""
title = clean((re.search(r"<h1[^>]*>(.*?)</h1>", head_html, re.S) or [None, ""])[1]) or meta.get("title", slug)
author = clean((re.search(r'<p class="author"[^>]*>(.*?)</p>', head_html, re.S) or [None, ""])[1]) or meta.get("author", "")
translator = clean((re.search(r'<p class="translator"[^>]*>(.*?)</p>', head_html, re.S) or [None, ""])[1])

start = doc.find("</nav>")
body = doc[start + 6:] if start >= 0 else doc[doc.find("</header>") + 9:]
blocks = []
for tag, _, inner in re.findall(r"<(h[1-4]|p|li|blockquote)([^>]*)>(.*?)</\1>", body, re.S):
    x = clean(inner)
    if not x or "EbookClassics" in x or "BookClassics" in x or x.startswith("Public domain text"):
        continue
    if tag in ("h1", "h2"):
        blocks.append(("h", x) if len(x) <= 120 else ("p", x))
    elif tag in ("h3", "h4"):
        blocks.append(("s", x) if len(x) <= 90 else ("p", x))
    else:
        blocks.append(("p", x))
if sum(len(t) for k, t in blocks if k == "p") < 2000:
    fail("too little text")


def tq(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def short(s, n=48):
    s = s.split(":")[0].strip()
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


year = meta.get("year", "")
if rtl:
    font = '("Amiri", "Libertinus Serif")'
    colophon = (f"نُشر لأول مرة سنة {year}. " if year else "") + "هذه الطبعة تقدّم النص المتاح في الملك العام. \\\\ نشر BookClassics · bookclassics.org"
else:
    font = '("Libertinus Serif", "New Computer Modern")'
    colophon = (f"First published in {year}. " if year and year.isdigit() else "") + "This edition presents the public-domain text. \\\\ Published by BookClassics · bookclassics.org"


def interior(size, lead):
    hy = "true" if lang in ("en", "fr", "de", "es", "it", "pt", "nl") else "false"
    out = [f'''#set document(title: {tq(title)}, author: {tq(author)})
#set text(font: {font}, size: {size}, lang: "{lang}", hyphenate: {hy}{', dir: rtl' if rtl else ''})
#set par(justify: true, leading: {lead}, first-line-indent: 1.2em, spacing: {lead})
#set page(width: 152mm, height: 229mm, margin: (inside: 0.75in, outside: 0.6in, top: 0.75in, bottom: 0.7in))
#let chap(t) = {{
  v(1.6em, weak: true)
  block(width: 100%, breakable: false, sticky: true)[
  #v(0.6em)
  #align(center)[#line(length: 2.2em, stroke: 1pt + rgb("#9a6b2f")) #v(0.4em) #text(size: 14pt, weight: "semibold", t)]
  #v(0.6em)
  ]
}}
#let sub(t) = block(sticky: true, above: 0.9em, below: 0.5em, width: 100%, align(center, text(weight: "semibold", t)))
#page[
  #v(2in)
  #align(center)[#text(size: 26pt, weight: "semibold", {tq(title)}) #v(1em) #text(size: 13pt, style: "italic", fill: rgb("#9a6b2f"), {tq(author)})
  {('#v(0.8em) #text(size: 10pt, fill: luma(90), ' + tq(translator) + ')') if translator else ''}]
  #v(1fr)
  #align(center, text(size: 9pt, fill: luma(90))[BookClassics])
]
#page[
  #v(1fr)
  #set text(size: 8.5pt, fill: luma(80))
  {colophon}
]
#set page(
  header: context {{
    let n = counter(page).get().first()
    set text(size: 8pt, fill: luma(110))
    if calc.even(n) {{ align(start, {tq(short(author))}) }} else {{ align(end, emph({tq(short(title))})) }}
  }},
  footer: context align(center, text(size: 8.5pt, fill: luma(110), counter(page).display())),
)
#counter(page).update(1)
''']
    first = True
    for k, t in blocks:
        if k == "h":
            out.append(f"#chap({tq(t)})"); first = True
        elif k == "s":
            out.append(f"#sub({tq(t)})"); first = True
        else:
            out.append(f"#par(first-line-indent: 0pt, {tq(t)})" if first else f"#par({tq(t)})"); first = False
    return "\n".join(out) + "\n"


def compile_typ(text, pdf, tmp):
    typ = os.path.join(tmp, "x.typ")
    open(typ, "w", encoding="utf-8").write(text)
    r = subprocess.run(["typst", "compile", "--root", tmp, typ, pdf], capture_output=True, text=True)
    if r.returncode:
        fail("typst: " + r.stderr[-300:])


def npages(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    return int(re.search(r"Pages:\s+(\d+)", out).group(1))


os.makedirs(out_dir, exist_ok=True)
ipdf = os.path.join(out_dir, slug + "-bv-interieur.pdf")
cpdf = os.path.join(out_dir, slug + "-bv-couverture.pdf")
with tempfile.TemporaryDirectory() as tmp:
    pages = 0
    steps = (("11.5pt", "1.0em"), ("11pt", "0.9em"), ("10.5pt", "0.85em")) if rtl else (("10.5pt", "0.6em"), ("10pt", "0.55em"), ("9.5pt", "0.52em"))
    for size, lead in steps:
        compile_typ(interior(size, lead), ipdf, tmp)
        pages = npages(ipdf)
        if pages <= MAX_PAGES:
            break
    if pages > MAX_PAGES:
        os.remove(ipdf)
        fail(f"too long ({pages} pages)")
    pad = max(MIN_PAGES, pages + (pages % 2)) - pages
    if pad:
        t = interior(size, lead) + "#set page(header: none, footer: none)\n#hide[.]\n" + "#pagebreak()\n#hide[.]\n" * (pad - 1)
        compile_typ(t, ipdf, tmp)
        pages = npages(ipdf)
        if pages % 2:
            fail(f"odd pages {pages}")

    # ---- cover ----
    spine = round(pages * SPINE_MM_PER_PAGE, 3)
    width = round(3 + 152 + spine + 152 + 3, 3)
    img = None
    for cand in (slug + ".jpg", slug + "-cover.png"):
        p = os.path.join(book_dir, cand)
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            img = p; break
    if not img:
        fail("no cover image")
    from PIL import Image
    im = Image.open(img).convert("RGB")
    if im.width < 1800:
        f = 1800 / im.width
        im = im.resize((1800, round(im.height * f)), Image.LANCZOS)
    im.save(os.path.join(tmp, "front.jpg"), quality=92)
    blurb = meta.get("blurb", "")
    note = colophon.split(" \\\\")[0]
    left_x, right_x = "3mm", f"{3 + 152 + spine}mm"
    back_x, front_x = (right_x, left_x) if rtl else (left_x, right_x)
    spine_txt = ""
    if spine >= 6:
        fs = min(10, spine * 1.3)
        sep = " #h(1.2em) "
        spine_txt = f'''#place(top+left, dx: {3 + 152}mm, box(width: {spine}mm, height: 235mm, align(center+horizon, rotate({'-90deg' if rtl else '90deg'}, reflow: true, text(size: {fs:.2f}pt, fill: gold, [*{short(title, 60).replace('[', '(').replace(']', ')').replace('#', '')}*{sep}{short(author, 40).replace('#', '')}{sep}BookClassics])))))'''
    cover = f'''#set page(width: {width}mm, height: 235mm, margin: 0pt)
#set text(font: {font}{', dir: rtl' if rtl else ''})
#let navy = rgb("#13233a")
#let gold = rgb("#e9c77f")
#place(top+left, rect(width: 100%, height: 100%, fill: navy))
#place(top+left, dx: {back_x} + 0.6in, dy: 3mm + 1.2in, block(width: 4.8in)[
  #text(size: 20pt, fill: gold, weight: "bold", {tq(title)})
  #v(0.3em)
  #text(size: 12pt, fill: rgb("#f4ecdc"), style: "italic", {tq(author)})
  #v(1.2em)
  #set par(justify: true, leading: 0.75em)
  #text(size: 11.5pt, fill: rgb("#f4ecdc"), {tq(blurb)})
  #v(1.5em)
  #text(size: 9.5pt, fill: rgb("#cbbf9f"), {tq(note)})
])
#place(bottom+left, dx: {back_x} + 0.6in, dy: -(3mm + 0.6in), text(size: 10pt, fill: gold)[bookclassics.org])
#place(top+left, dx: {back_x} + {'0.6in' if rtl else '3.9in'}, dy: 235mm - 3mm - 1.25in - 0.35in, rect(width: 2.0in, height: 1.25in, fill: white))
#place(top+left, dx: {3 + 152}mm, rect(width: {spine}mm, height: 100%, fill: rgb("#0d1828")))
{spine_txt}
#place(top+left, dx: {"0mm" if rtl else right_x}, image("front.jpg", width: {155 if True else 0}mm, height: 235mm, fit: "cover"))
'''
    compile_typ(cover, cpdf, tmp)

print(json.dumps({"slug": slug, "title": title, "pages": pages, "lang": lang, "spine_mm": spine, "cover_w_mm": width,
                  "interior_bytes": os.path.getsize(ipdf), "cover_bytes": os.path.getsize(cpdf)}, ensure_ascii=False))
