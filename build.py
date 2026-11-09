#!/usr/bin/env python3
"""Generates the static site from _src/<lang>/ (ui.json plus one HTML fragment per page).

English is written to the site root, every other language to <lang>/. Run: python build.py
Pages: index.html, privacy.html, delete-account.html in every language.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
BASE = "https://milanbenicky.github.io/miben-web/"
LANGS = ["en"]  # order of the switcher; English is the source and x-default. Only English is published (de, fr, es, ru are in git history)
PAGES = [("index", "index.html", "home"), ("privacy", "privacy.html", "privacy"), ("delete-account", "delete-account.html", "delete")]

LAYOUT = """<!doctype html>
<html lang="{html_lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
{alternates}
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
<header>
  <div class="wrap">
    <a class="brand" href="index.html">MiBeN</a>
    <nav>
{nav}
    </nav>
  </div>
{langs_block}</header>
<main class="wrap">
{notice}{body}</main>
<footer>
  <div class="wrap">
    <p>{address}</p>
    <p>{ico}: 55611541</p>
    <p>{dic}: 2122061480</p>
    <p>{icdph}: SK2122061480</p>
    <p>{duns}: 983942274</p>
  </div>
</footer>
</body>
</html>
"""


def out_dir(lang):
    return ROOT if lang == "en" else ROOT / lang


def rel(cur, target, filename):
    """Relative link from a page of language `cur` to `filename` of language `target`."""
    up = "" if cur == "en" else "../"
    return up + ("" if target == "en" else target + "/") + filename


def main():
    ui = {l: json.loads((ROOT / "_src" / l / "ui.json").read_text(encoding="utf-8")) for l in LANGS}
    for lang in LANGS:
        d = out_dir(lang)
        d.mkdir(exist_ok=True)
        u = ui[lang]
        for key, filename, navkey in PAGES:
            body = (ROOT / "_src" / lang / f"{key}.html").read_text(encoding="utf-8")
            nav = "\n".join(
                '      <a href="{}"{}>{}</a>'.format(f, ' aria-current="page"' if k == key else "", u["nav"][n])
                for k, f, n in PAGES)
            langs = "\n".join(
                '    <a href="{}" hreflang="{}" lang="{}"{}>{}</a>'.format(
                    rel(lang, t, filename), ui[t]["html_lang"], ui[t]["html_lang"],
                    ' aria-current="true"' if t == lang else "", ui[t]["name"])
                for t in LANGS)
            alternates = "\n".join(
                '<link rel="alternate" hreflang="{}" href="{}">'.format(
                    ui[t]["html_lang"], BASE + ("" if t == "en" else t + "/") + filename) for t in LANGS)
            alternates += '\n<link rel="alternate" hreflang="x-default" href="{}">'.format(BASE + filename)
            # With a single language there is nothing to switch to and no alternates to announce.
            langs_block = '  <div class="wrap langs">\n{}\n  </div>\n'.format(langs) if len(LANGS) > 1 else ""
            if len(LANGS) == 1:
                alternates = ""
            notice = ""
            if lang != "en":
                notice = '  <p class="notice">{} <a href="{}" hreflang="en" lang="en">{}</a></p>\n'.format(
                    u["notice"], rel(lang, "en", filename), u["english_link"])
            html = LAYOUT.format(
                html_lang=u["html_lang"], title=u["pages"][key]["title"], description=u["pages"][key]["description"],
                canonical=BASE + ("" if lang == "en" else lang + "/") + filename, alternates=alternates,
                up="" if lang == "en" else "../", nav=nav, langs_block=langs_block, notice=notice, body=body,
                address=u["footer"]["address"], ico=u["footer"]["ico"], dic=u["footer"]["dic"],
                icdph=u["footer"]["icdph"], duns=u["footer"]["duns"])
            (d / filename).write_text(html, encoding="utf-8", newline="\n")
    print("built", len(LANGS), "languages")


if __name__ == "__main__":
    main()
