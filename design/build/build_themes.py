#!/usr/bin/env python3
"""Generate one FigCraft design per theme alternative for erme2.com.

Usage:  python3 design/build/build_themes.py <theme> <fonts-dir> > /tmp/<theme>.jsonl
        figcraft-cli run /tmp/<theme>.jsonl --out design/<theme>/<theme>.figcraft
Themes: christmas, terminal, blueprint, swiss, arcade. <fonts-dir> holds the @expo-google-fonts packages
(npm i @expo-google-fonts/ibm-plex-mono @expo-google-fonts/dm-serif-display @expo-google-fonts/vt323
 @expo-google-fonts/architects-daughter @expo-google-fonts/inter @expo-google-fonts/press-start-2p).

The copy is the live site's, shortened in places to fit a mockup. Each theme changes typography, layout
details and adds personal touches, not just colours (feedback: the current site reads as AI-generated).
"""
import json
import sys

steps = []
_n = 0


def S(command, params, ref=True):
    global _n
    step = {"command": command, "params": params}
    if ref:
        _n += 1
        step["as"] = f"n{_n}"
    steps.append(step)
    return {"$ref": step["as"]} if ref else None


def F(parent, name, layout=None, w=None, h=None, x=None, y=None, fill=None, **p):
    props = {"fill": fill}
    if layout:
        props["layout"] = layout
    for k in ("gap", "padding", "cornerRadius", "mainAlign", "crossAlign", "wrap", "crossGap", "clip",
              "stroke", "strokeWeight", "strokeSides", "dashes", "opacity", "rotation"):
        if k in p:
            props[k] = p[k]
    props["sizingH"] = p.get("sH", "fixed" if w else "hug")
    props["sizingV"] = p.get("sV", "fixed" if h else "hug")
    params = {"type": "frame", "name": name, "props": props, "select": False}
    for k, v in (("parent", parent), ("width", w), ("height", h), ("x", x), ("y", y)):
        if v is not None:
            params[k] = v
    return S("node.create", params)


FONT = {}  # theme sets: body, mono-ish fonts


def T(parent, text, size, font, color, w=None, fill=False, lh=None, ls=None, align=None, x=None, y=None, name=None, upper=False):
    fam, style = font
    props = {"fontFamily": fam, "fontStyle": style, "fontSize": size, "fill": color}
    if lh:
        props["lineHeight"] = lh
    if ls:
        props["letterSpacing"] = ls
    if align:
        props["textAlign"] = align
    if fill:
        props["sizingH"] = "fill"
        props["textAutoResize"] = "height"
    params = {"type": "text", "parent": parent, "text": text.upper() if upper else text, "props": props, "select": False}
    if x is not None:
        params["x"] = x
    if y is not None:
        params["y"] = y
    if name:
        params["name"] = name
    t = S("node.create", params)
    if w:
        S("node.set", {"ids": [t], "props": {"width": w, "textAutoResize": "height"}}, ref=False)
    return t


def grow(ref):
    S("node.set", {"ids": [ref], "props": {"sizingH": "fill"}}, ref=False)


def setp(ref, **props):
    S("node.set", {"ids": [ref], "props": props}, ref=False)


def ellipse(parent, x, y, d, fill, name="dot", stroke=None):
    props = {"fill": fill}
    if stroke:
        props.update(stroke=stroke, strokeWeight=1)
    S("node.create", {"type": "ellipse", "parent": parent, "x": x, "y": y, "width": d, "height": d, "props": props,
                      "select": False, "name": name}, ref=False)


def vec(parent, path, stroke=None, fill=None, sw=1.5, dashes=None, name="line"):
    props = {"fill": fill, "stroke": stroke, "strokeWeight": sw, "strokeCap": "round", "strokeJoin": "round"}
    if dashes:
        props["dashes"] = dashes
    S("node.create", {"type": "vector", "parent": parent, "x": 0, "y": 0, "path": path, "props": props,
                      "select": False, "name": name}, ref=False)


# ---------------------------------------------------------------- content (from the live site)
NAME = "Arduino Di Giosia"
ROLE = "Engineering Leader · Senior Engineer"
EYEBROW = "Engineering Leadership · Senior TypeScript/PHP"
H1 = "Hands-on engineering leadership."
LEAD = ("I build and modernise web platforms, APIs, payment systems, and business-critical tooling: close to the "
        "code, credible with engineers, effective with product and leadership, and comfortable managing teams.")
CTAS = [("@", "Email me"), ("GH", "GitHub"), ("in", "LinkedIn"), ("CV", "Download CV (PDF)")]
METRICS = [("20+", "years building web platforms, APIs, payments, and business tooling"),
           ("10-12", "engineers led across four remote teams and four time zones"),
           ("5-10M", "weekly clicks handled by affiliate tracking platforms"),
           ("v1 in minutes", "first version AI-generated from my CV, then iterated through issues and reviews")]
ROLES = [("VP of Engineering", "ClickTech", "Nottingham, remote", "Nov 2025 – Aug 2026",
          ["Led four remote teams while staying close to architecture and implementation.",
           "Rebuilt a central NestJS payments and subscriptions API.",
           "Eliminated production outages within roughly three weeks."]),
         ("Engineer III", "AJ Bell", "Manchester, hybrid", "Mar 2023 – Oct 2025",
          ["Customer-facing investment platform services, frontend and backend.",
           "REST APIs and third-party integrations, built for reliability.",
           "Security- and stability-first culture with rigorous review."]),
         ("Head of Development", "Moreniche", "Nottingham", "Mar 2017 – Mar 2023",
          ["Technical direction for affiliate, API, tracking, devops and design teams.",
           "Scaled tracking from about 1M to 5-10M clicks per week.",
           "Supported $2-5M/year in affiliate revenue."])]
PROJECTS = [("Yaup", "AI agent governance tooling", "One versioned policy and a planning gate across Codex, Claude Code, Cursor, Copilot and Gemini CLI."),
            ("Pane", "Data-access control plane", "Laravel control plane: auth, organisation isolation, encrypted connections, controlled CRUD."),
            ("Latte", "Frontend template", "React and TypeScript template for organisation apps powered by Pane."),
            ("erme2.com", "Open personal site", "This website: an AI-assisted workflow in public, from issue to review to deployment.")]
CONTACT = [("@", "me@erme2.com"), ("GH", "github.com/erme2"), ("in", "linkedin.com/in/arduinodigiosia"), ("CV", "Download CV (PDF)")]

W = 1440
PAD = 120
CW = W - 2 * PAD


def fonts(dirp, names):
    paths = {
        "plex": ["400Regular/IBMPlexMono_400Regular", "500Medium/IBMPlexMono_500Medium", "700Bold/IBMPlexMono_700Bold"],
        "dmserif": ["400Regular/DMSerifDisplay_400Regular", "400Regular_Italic/DMSerifDisplay_400Regular_Italic"],
        "vt323": ["400Regular/VT323_400Regular"],
        "architects": ["400Regular/ArchitectsDaughter_400Regular"],
        "inter": ["400Regular/Inter_400Regular", "500Medium/Inter_500Medium", "700Bold/Inter_700Bold", "900Black/Inter_900Black"],
        "pixel": ["400Regular/PressStart2P_400Regular"],
    }
    pkg = {"plex": "ibm-plex-mono", "dmserif": "dm-serif-display", "vt323": "vt323", "architects": "architects-daughter", "inter": "inter", "pixel": "press-start-2p"}
    for n in names:
        for f in paths[n]:
            S("text.loadFont", {"path": f"{dirp}/@expo-google-fonts/{pkg[n]}/{f}.ttf"}, ref=False)


PLEX = ("IBM Plex Mono", "Regular")
PLEX_M = ("IBM Plex Mono", "Medium")
PLEX_B = ("IBM Plex Mono", "Bold")


def page(name, bg):
    S("page.rename", {"name": "Desktop"}, ref=False)
    return F(None, name, layout="vertical", w=W, x=0, y=0, fill=bg, clip=True, sV="hug")


# ================================================================ CHRISTMAS: "Advent edition"
def christmas():
    PINE, PINE2, CREAM, RED, GOLD, SAGE = "#10281B", "#173A27", "#FBF5E6", "#C8312F", "#E0B84B", "#A9C2AE"
    SERIF, SERIF_I = ("DM Serif Display", "Regular"), ("DM Serif Display", "Italic")
    pg = page("Christmas · At home", PINE)

    # fairy-light string across the very top
    lights = F(pg, "Fairy lights", w=W, h=34)
    vec(lights, "M0 6 Q 180 30 360 8 T 720 8 T 1080 8 T 1440 6", stroke="#3B5E48", sw=1.5)
    for i in range(24):
        x = 30 + i * 59
        y = 14 + (8 if i % 2 else 2)
        ellipse(lights, x, y, 11, [RED, GOLD, "#F4EBD0", "#6FB98F"][i % 4], name=f"bulb {i + 1}")

    # nav
    nav = F(pg, "Nav", layout="horizontal", w=W, h=76, padding=[0, PAD, 0, PAD], mainAlign="spaceBetween", crossAlign="center")
    brand = F(nav, "Brand", layout="horizontal", gap=12, crossAlign="center")
    av = F(brand, "Photo", layout="horizontal", w=42, h=42, fill=GOLD, mainAlign="center", crossAlign="center", cornerRadius=21)
    T(av, "AD", 14, PLEX_B, PINE)
    bt = F(brand, "Name", layout="vertical")
    T(bt, NAME, 15, PLEX_B, CREAM)
    T(bt, ROLE, 12, PLEX, SAGE)
    links = F(nav, "Links", layout="horizontal", gap=28)
    for l in ("Profile", "Experience", "Projects", "Workflow", "Contact"):
        T(links, l, 14, PLEX_M, CREAM)
    stripe = F(pg, "Candy stripe", w=W, h=6, fill=RED)
    for i in range(0, W, 24):
        vec(stripe, f"M{i} 6 L{i + 12} 0", stroke=CREAM, sw=6)

    # hero: copy + advent calendar of metrics
    hero = F(pg, "Hero", layout="horizontal", w=W, padding=[72, PAD, 96, PAD], gap=72, crossAlign="center")
    left = F(hero, "Copy", layout="vertical", gap=22)
    grow(left)
    T(left, "Christmas at home · Nottingham, December 2026", 13, PLEX_B, GOLD, ls="6%", upper=True)
    T(left, "Hands-on\nengineering\nleadership.", 82, SERIF, CREAM, lh=84, fill=True)
    T(left, LEAD, 17, PLEX, SAGE, lh=28, fill=True)
    cta = F(left, "CTAs", layout="horizontal", gap=10, wrap=True, crossGap=10)
    grow(cta)
    for i, (ic, label) in enumerate(CTAS):
        b = F(cta, label, layout="horizontal", gap=10, padding=[10, 16, 10, 10], cornerRadius=24, crossAlign="center",
              fill=RED if i == 0 else None, **({} if i == 0 else {"stroke": CREAM, "strokeWeight": 1}))
        c = F(b, "Icon", layout="horizontal", w=26, h=26, cornerRadius=13, fill=GOLD, mainAlign="center", crossAlign="center")
        T(c, ic, 11, PLEX_B, PINE)
        T(b, label, 14, PLEX_B, CREAM)
    # a family house at night: the four numbers sit in its lit windows
    art = F(hero, "House at night", w=500, h=470)
    S("node.create", {"type": "ellipse", "parent": art, "x": 380, "y": 6, "width": 54, "height": 54, "select": False,
                      "name": "Moon", "props": {"fill": "#F4EBD0"}}, ref=False)
    F(art, "Snowy garden", w=500, h=60, x=0, y=410, fill="#F4F1E8", cornerRadius=30)
    F(art, "Chimney", w=44, h=80, x=330, y=40, fill="#6E2A26")
    vec(art, "M10 140 L250 30 L490 140 Z", fill="#2A1B17", stroke=GOLD, sw=2, name="Roof")
    for i in range(9):
        ellipse(art, 30 + i * 52, 128 - (abs(i - 4) * 0) , 10, [RED, GOLD, "#6FB98F", "#F4EBD0"][i % 4], name=f"roof light {i}")
    body = F(art, "House", w=460, h=280, x=20, y=140, fill="#8B2E2A", stroke="#5E1D1A", strokeWeight=2)
    spots = [(20, 26), (290, 26), (20, 150), (290, 150)]
    for i, (v, label) in enumerate(METRICS):
        x, y = spots[i]
        win = F(body, f"Window {i + 1}", layout="vertical", gap=2, w=150, h=104, x=x, y=y, padding=[10, 12, 10, 12],
                fill="#FFD98A", stroke="#F4F1E8", strokeWeight=4)
        T(win, v, 22 if len(v) < 8 else 15, SERIF, "#3A1A10")
        T(win, label, 10, PLEX, "#5A3A20", fill=True, lh=13)
    F(body, "Door", w=80, h=140, x=190, y=140, fill="#2E6B48", stroke="#F4F1E8", strokeWeight=3)
    S("node.create", {"type": "ellipse", "parent": body, "x": 208, "y": 162, "width": 44, "height": 44, "select": False,
                      "name": "Wreath", "props": {"fill": None, "stroke": "#1F5136", "strokeWeight": 9}}, ref=False)
    ellipse(body, 226, 196, 8, RED, name="Bow")
    ellipse(body, 252, 220, 6, GOLD, name="Door knob")
    T(art, "Current signal: all the lights are on", 16, SERIF_I, GOLD, x=0, y=0)

    def tartan(name):
        band = F(pg, name, w=W, h=18, fill="#9E2B25", clip=True)
        for i in range(0, W, 36):
            F(band, "v", w=10, h=18, x=i, y=0, fill="#1F4D33")
            F(band, "v2", w=2, h=18, x=i + 18, y=0, fill=GOLD)
        F(band, "h", w=W, h=4, x=0, y=7, fill="#1F4D33")
        return band

    tartan("Tartan 1")
    # experience as gift tags
    sec = F(pg, "Experience", layout="vertical", w=W, padding=[80, PAD, 80, PAD], gap=32, fill=CREAM)
    T(sec, "This year's gifts to the teams I worked with", 44, SERIF, PINE)
    row = F(sec, "Tags", layout="horizontal", gap=24)
    grow(row)
    for title, co, place, dates, bullets in ROLES:
        tag = F(row, f"Tag {co}", layout="vertical", gap=10, padding=[26, 24, 26, 24], fill="#FFFFFF", cornerRadius=10,
                stroke="#E6DCC4", strokeWeight=1)
        grow(tag)
        top = F(tag, "Top", layout="horizontal", mainAlign="spaceBetween", crossAlign="center")
        grow(top)
        T(top, dates, 12, PLEX_B, RED)
        ellipse(top, 0, 0, 14, CREAM, name="tag hole", stroke="#C9BC9C")
        T(tag, f"{title}", 24, SERIF, PINE, fill=True)
        T(tag, f"{co} · {place}", 13, PLEX_M, "#5B6B60")
        for b in bullets:
            T(tag, f"✶  {b}", 13, PLEX, "#36423A", fill=True, lh=19)

    tartan("Tartan 2")
    # projects as wrapped presents
    sec = F(pg, "Projects", layout="vertical", w=W, padding=[80, PAD, 80, PAD], gap=32)
    T(sec, "Under the tree: personal projects", 44, SERIF, CREAM)
    row = F(sec, "Presents", layout="horizontal", gap=24)
    grow(row)
    for i, (name, label, body) in enumerate(PROJECTS):
        box = F(row, f"Present {name}", w=282, h=300, fill=[RED, GOLD, "#2E6B48", CREAM][i], cornerRadius=6, clip=True)
        ribbon = CREAM if i in (0, 2) else RED
        F(box, "Ribbon V", w=26, h=300, x=128, y=0, fill=ribbon)
        F(box, "Ribbon H", w=282, h=26, x=0, y=86, fill=ribbon)
        card = F(box, "Card", layout="vertical", gap=6, w=242, x=20, y=132, padding=16, fill="#FFFFFF", cornerRadius=6)
        T(card, name, 22, SERIF, PINE)
        T(card, label, 11, PLEX_B, RED, upper=True, ls="4%")
        T(card, body, 12, PLEX, "#36423A", fill=True, lh=17)
        ellipse(box, 123, 81, 36, GOLD if i != 1 else RED, name="Bow")
        T(box, "★", 20, SERIF, PINE if i != 1 else CREAM, x=133, y=86)

    # contact + footer
    sec = F(pg, "Contact", layout="horizontal", w=W, padding=[72, PAD, 72, PAD], gap=64, fill=PINE2, crossAlign="center")
    l = F(sec, "Copy", layout="vertical", gap=12)
    grow(l)
    T(l, "Buon Natale, Merry Christmas.", 48, SERIF_I, GOLD)
    T(l, "Engineering judgment, code credibility and management experience, all wrapped up in one place.", 17, PLEX, SAGE, fill=True, lh=27)
    r = F(sec, "Links", layout="vertical", gap=12)
    for ic, label in CONTACT:
        a = F(r, label, layout="horizontal", gap=12, crossAlign="center")
        c = F(a, "Icon", layout="horizontal", w=30, h=30, cornerRadius=15, fill=RED, mainAlign="center", crossAlign="center")
        T(c, ic, 11, PLEX_B, CREAM)
        T(a, label, 15, PLEX_B, CREAM)
    ft = F(pg, "Footer", layout="horizontal", w=W, padding=[26, PAD, 34, PAD], mainAlign="spaceBetween")
    T(ft, "Arduino Di Giosia · Engineering leader and senior engineer · TypeScript, React, PHP", 13, PLEX, SAGE)
    T(ft, "Panettone tested in Nottingham. Back to normal on 7 January.", 13, PLEX, GOLD)

    # a few static snowflakes over the hero (the live version drifts, off with reduced motion)
    for i, (x, y, d) in enumerate([(70, 140, 4), (310, 260, 3), (640, 120, 5), (980, 220, 3), (1300, 160, 4), (1180, 520, 3),
                                    (860, 600, 4), (420, 640, 3), (60, 560, 5), (1380, 420, 3), (720, 380, 3)]):
        S("node.create", {"type": "ellipse", "parent": pg, "x": x, "y": y, "width": d, "height": d,
                          "props": {"fill": "#FFFFFF", "opacity": 0.7, "absolute": True}, "select": False, "name": f"snow {i}"}, ref=False)


# ================================================================ TERMINAL: "tty"
def terminal():
    BG, WIN, GREEN, DIM, AMBER, LINE = "#050805", "#0A110B", "#7CFF9B", "#4E9C61", "#FFB000", "#1C3A22"
    PIX = ("VT323", "Regular")
    pg = page("Terminal · tty", BG)
    wrap = F(pg, "Desk", layout="vertical", w=W, gap=20, padding=[40, 80, 40, 80])
    win = F(wrap, "Terminal window", layout="vertical", fill=WIN, cornerRadius=12, clip=True, stroke=LINE, strokeWeight=1)
    grow(win)
    bar = F(win, "Title bar", layout="horizontal", h=38, padding=[0, 16, 0, 16], gap=8, crossAlign="center", fill="#111A12", sV="fixed")
    grow(bar)
    for c in ("#FF5F56", "#FFBD2E", "#27C93F"):
        d = F(bar, "light", w=12, h=12, cornerRadius=6, fill=c)
    T(bar, "   arduino@erme2: ~ — zsh — 140×48", 13, PLEX, DIM)
    body = F(win, "Session", layout="vertical", gap=26, padding=[30, 40, 40, 40])
    grow(body)

    def prompt(parent, cmd):
        r = F(parent, "Prompt", layout="horizontal", gap=10)
        T(r, "arduino@erme2", 15, PLEX_B, GREEN)
        T(r, "~", 15, PLEX_B, "#6FB7FF")
        T(r, "$", 15, PLEX_B, DIM)
        T(r, cmd, 15, PLEX, "#D7FFE0")
        return r

    prompt(body, "whoami")
    hero = F(body, "Hero", layout="horizontal", gap=48)
    grow(hero)
    left = F(hero, "Copy", layout="vertical", gap=18)
    grow(left)
    T(left, NAME.lower().replace(" ", "_"), 18, PLEX, DIM)
    T(left, "Hands-on\nengineering\nleadership._", 96, PIX, GREEN, lh=84, fill=True)
    T(left, "# " + LEAD, 15, PLEX, "#A9E8B6", lh=25, fill=True)
    cta = F(left, "Commands", layout="horizontal", gap=10, wrap=True, crossGap=10)
    grow(cta)
    for i, (_, label) in enumerate(CTAS):
        b = F(cta, label, layout="horizontal", padding=[8, 14, 8, 14], fill=GREEN if i == 0 else None,
              **({} if i == 0 else {"stroke": GREEN, "strokeWeight": 1}))
        T(b, f"[ {label.lower()} ]", 14, PLEX_B, BG if i == 0 else GREEN)
    top = F(hero, "htop", layout="vertical", w=520, gap=12, padding=18, stroke=LINE, strokeWeight=1)
    hd = F(top, "Header", layout="horizontal", mainAlign="spaceBetween")
    grow(hd)
    T(hd, "signal  —  uptime 20y 3m", 13, PLEX_B, AMBER)
    T(hd, "load: 0.42 0.38 0.31", 13, PLEX, DIM)
    for i, (v, label) in enumerate(METRICS):
        row = F(top, f"Metric {i}", layout="vertical", gap=4)
        grow(row)
        r1 = F(row, "Bar", layout="horizontal", gap=10, crossAlign="center")
        grow(r1)
        T(r1, f"{i + 1}", 13, PLEX, DIM)
        fillw = [96, 70, 84, 58][i]
        bar = F(r1, "Track", layout="horizontal", h=14, fill="#0F1F12", sV="fixed")
        grow(bar)
        F(bar, "Used", w=int(3.6 * fillw), h=14, fill=[GREEN, "#5FD7FF", AMBER, GREEN][i])
        T(r1, v, 16, PLEX_B, GREEN)
        T(row, "   " + label, 12, PLEX, DIM, fill=True)
    T(top, "Positioning: tech lead, senior TypeScript and PHP engineer and engineering leader, fluent in AI-assisted delivery.",
      12, PLEX, "#A9E8B6", fill=True, lh=18)

    prompt(body, "git log --oneline --graph career")
    log = F(body, "git log", layout="vertical", gap=16, padding=[0, 0, 0, 6])
    grow(log)
    for i, (title, co, place, dates, bullets) in enumerate(ROLES):
        e = F(log, f"Commit {co}", layout="horizontal", gap=16)
        grow(e)
        g = F(e, "Graph", layout="vertical", w=16)
        T(g, "*", 18, PLEX_B, AMBER)
        c = F(e, "Commit", layout="vertical", gap=4)
        grow(c)
        h = F(c, "Head", layout="horizontal", gap=10)
        T(h, ["a91f3e2", "6c0d47b", "e52b18f"][i], 15, PLEX_B, AMBER)
        if i == 0:
            T(h, "(HEAD -> main)", 15, PLEX_B, "#6FB7FF")
        T(h, f"{title} @ {co}", 15, PLEX_B, "#D7FFE0")
        T(c, f"Date:   {dates} · {place}", 13, PLEX, DIM)
        for b in bullets:
            T(c, f"    + {b}", 13, PLEX, "#A9E8B6", fill=True)

    prompt(body, "ls -la ~/projects")
    tbl = F(body, "ls", layout="vertical", gap=6)
    grow(tbl)
    T(tbl, "total 4", 13, PLEX, DIM)
    for i, (name, label, desc) in enumerate(PROJECTS):
        r = F(tbl, name, layout="horizontal", gap=18)
        grow(r)
        T(r, "drwxr-xr-x", 13, PLEX, DIM)
        T(r, "arduino", 13, PLEX, DIM)
        T(r, "2026", 13, PLEX, DIM)
        T(r, f"{name}/", 14, PLEX_B, "#6FB7FF")
        T(r, f"# {label}: {desc}", 13, PLEX, "#A9E8B6", fill=True)

    prompt(body, "contact --help")
    ct = F(body, "Contact", layout="horizontal", gap=28, wrap=True, crossGap=10)
    grow(ct)
    for ic, label in CONTACT:
        T(ct, f"--{ic.lower() if ic != '@' else 'mail'}  {label}", 15, PLEX_B, GREEN)
    last = prompt(body, "")
    F(last, "Cursor", w=10, h=18, fill=GREEN)
    T(wrap, "Arduino Di Giosia · Engineering leader and senior engineer · exit 0", 13, PLEX, DIM, name="Footer note")


# ================================================================ BLUEPRINT: "Sheet A1"
def blueprint():
    BLUE, LINE, WHITE, PALE, YELLOW = "#0F4C81", "#FFFFFF", "#F2F8FF", "#BCD6F2", "#FFD166"
    HAND = ("Architects Daughter", "Regular")
    pg = page("Blueprint · Sheet A1", BLUE)
    # grid paper: a minor 24 px and a major 120 px grid behind everything
    H = 1800
    for name, step, op in (("Grid minor", 24, 0.07), ("Grid major", 120, 0.16)):
        g = F(pg, name, w=W, h=H, x=0, y=0, opacity=op)
        setp(g, absolute=True)
        path = " ".join([f"M{x} 0 L{x} {H}" for x in range(0, W + 1, step)] + [f"M0 {y} L{W} {y}" for y in range(0, H + 1, step)])
        vec(g, path, stroke=WHITE, sw=1, name=name)
    sheet = F(pg, "Sheet", layout="vertical", w=W, padding=[36, 60, 36, 60])
    frame = F(sheet, "Drawing frame", layout="vertical", gap=0, stroke=WHITE, strokeWeight=2)
    grow(frame)
    # zone markers along the top
    zones = F(frame, "Zones", layout="horizontal", h=22, sV="fixed", stroke=WHITE, strokeWeight=1, strokeSides=[0, 0, 1, 0])
    grow(zones)
    for z in "ABCDEFGH":
        c = F(zones, f"Zone {z}", layout="horizontal", h=22, mainAlign="center", crossAlign="center", sV="fixed",
              stroke=WHITE, strokeWeight=1, strokeSides=[0, 1, 0, 0])
        grow(c)
        T(c, z, 11, PLEX_B, PALE)
    inner = F(frame, "Drawing", layout="vertical", gap=56, padding=[44, 56, 44, 56])
    grow(inner)

    nav = F(inner, "Nav", layout="horizontal", mainAlign="spaceBetween", crossAlign="center")
    grow(nav)
    T(nav, f"{NAME.upper()}  /  {ROLE.upper()}", 13, PLEX_B, WHITE, ls="6%")
    links = F(nav, "Links", layout="horizontal", gap=26)
    for i, l in enumerate(("Profile", "Experience", "Projects", "Workflow", "Contact")):
        T(links, f"{'ABCDE'[i]}. {l.upper()}", 12, PLEX_M, PALE, ls="6%")

    hero = F(inner, "Hero", layout="horizontal", gap=64, crossAlign="center")
    grow(hero)
    left = F(hero, "Copy", layout="vertical", gap=20)
    grow(left)
    T(left, "DETAIL 1 — THE ENGINEER", 12, PLEX_B, YELLOW, ls="10%")
    T(left, "HANDS-ON\nENGINEERING\nLEADERSHIP.", 64, PLEX_B, WHITE, lh=68, ls="2%", fill=True)
    T(left, "built close to the code ↘", 20, HAND, YELLOW)
    T(left, LEAD, 15, PLEX, PALE, lh=25, fill=True)
    cta = F(left, "CTAs", layout="horizontal", gap=10, wrap=True, crossGap=10)
    grow(cta)
    for i, (ic, label) in enumerate(CTAS):
        b = F(cta, label, layout="horizontal", gap=8, padding=[9, 14, 9, 14], fill=WHITE if i == 0 else None,
              stroke=WHITE, strokeWeight=1, **({} if i == 0 else {"dashes": [5, 4]}))
        T(b, label.upper(), 12, PLEX_B, BLUE if i == 0 else WHITE, ls="4%")
    # signal board as an annotated part drawing
    part = F(hero, "Part drawing", w=560, h=430)
    T(part, "W = 420", 11, PLEX, PALE, x=150, y=0)
    vec(part, "M40 18 L460 18 M40 12 L40 24 M460 12 L460 24", stroke=PALE, sw=1)
    box = F(part, "Signal board", layout="vertical", w=420, x=40, y=34, stroke=WHITE, strokeWeight=1.5)
    for i, (v, label) in enumerate(METRICS):
        r = F(box, f"Metric {i}", layout="horizontal", gap=16, padding=[16, 18, 16, 18], crossAlign="center",
              stroke=WHITE, strokeWeight=1, strokeSides=[0 if i == 0 else 1, 0, 0, 0], dashes=[4, 4])
        grow(r)
        T(r, f"0{i + 1}", 11, PLEX_B, YELLOW)
        T(r, v, 26, PLEX_B, WHITE)
        T(r, label, 11, PLEX, PALE, fill=True)
    # callouts in handwriting
    T(part, "20 yrs, still writes the code", 17, HAND, YELLOW, x=150, y=392)
    vec(part, "M140 404 Q 110 400 100 372", stroke=YELLOW, sw=1.5)
    T(part, "H = 4", 11, PLEX, PALE, x=480, y=190)
    vec(part, "M470 34 L470 370 M464 34 L476 34 M464 370 L476 370", stroke=PALE, sw=1)

    # experience as revision table
    sec = F(inner, "Experience", layout="vertical", gap=18)
    grow(sec)
    T(sec, "B — REVISION HISTORY", 14, PLEX_B, YELLOW, ls="10%")
    tbl = F(sec, "Revisions", layout="vertical", stroke=WHITE, strokeWeight=1)
    grow(tbl)
    hdr = F(tbl, "Header", layout="horizontal", padding=[10, 16, 10, 16], gap=24, fill="#0B3E6B")
    grow(hdr)
    for txt, w in (("REV", 60), ("DATE", 200), ("ROLE", 320), ("CHANGE", None)):
        t = T(hdr, txt, 11, PLEX_B, PALE, ls="8%", w=w)
        if not w:
            grow(t)
    for i, (title, co, place, dates, bullets) in enumerate(ROLES):
        r = F(tbl, co, layout="horizontal", padding=[14, 16, 14, 16], gap=24, stroke=WHITE, strokeWeight=1,
              strokeSides=[1, 0, 0, 0])
        grow(r)
        T(r, ["C", "B", "A"][i], 18, PLEX_B, YELLOW, w=60)
        T(r, dates.upper(), 12, PLEX, WHITE, w=200)
        rl = F(r, "Role", layout="vertical", w=320)
        T(rl, title.upper(), 13, PLEX_B, WHITE, fill=True)
        T(rl, f"{co} · {place}", 12, PLEX, PALE, fill=True)
        ch = F(r, "Change", layout="vertical", gap=4)
        grow(ch)
        for b in bullets[:2]:
            T(ch, f"— {b}", 12, PLEX, PALE, fill=True, lh=17)

    # projects as an architecture diagram
    sec = F(inner, "Projects", layout="vertical", gap=22)
    grow(sec)
    T(sec, "C — SYSTEM DIAGRAM: PERSONAL PROJECTS", 14, PLEX_B, YELLOW, ls="10%")
    dia = F(sec, "Diagram", w=1200, h=250)
    xs = [0, 320, 640, 960]
    for i, (name, label, body) in enumerate(PROJECTS):
        b = F(dia, name, layout="vertical", gap=6, w=240, x=xs[i], y=20, padding=16, stroke=WHITE, strokeWeight=1.5,
              fill="#0B3E6B")
        T(b, name.upper(), 18, PLEX_B, WHITE)
        T(b, label.upper(), 10, PLEX_B, YELLOW, ls="6%")
        T(b, body, 11, PLEX, PALE, fill=True, lh=16)
        if i < 3:
            vec(dia, f"M{xs[i] + 244} 100 L{xs[i + 1] - 4} 100 M{xs[i + 1] - 12} 94 L{xs[i + 1] - 4} 100 L{xs[i + 1] - 12} 106",
                stroke=WHITE, sw=1.5)
    for i, word in enumerate(("governs", "serves", "ships")):
        T(dia, word, 15, HAND, YELLOW, x=xs[i] + 244 + (72 - len(word) * 7) // 2, y=72)

    # contact + title block
    bottom = F(inner, "Bottom", layout="horizontal", gap=40, crossAlign="max")
    grow(bottom)
    ct = F(bottom, "Contact", layout="vertical", gap=10)
    grow(ct)
    T(ct, "D — CONTACT", 14, PLEX_B, YELLOW, ls="10%")
    for ic, label in CONTACT:
        T(ct, f"[{ic}]  {label}", 14, PLEX_B, WHITE)
    tb = F(bottom, "Title block", layout="vertical", w=460, stroke=WHITE, strokeWeight=1.5)
    for k, v in (("PROJECT", "erme2.com"), ("DRAWN BY", "A. DI GIOSIA"), ("CHECKED", "YAUP REVIEW GATE"),
                 ("SCALE", "1:1"), ("SHEET", "A1 · 1 OF 1"), ("REV", "v1.4 · NOV 2026")):
        r = F(tb, k, layout="horizontal", padding=[8, 12, 8, 12], gap=16, stroke=WHITE, strokeWeight=1,
              strokeSides=[0 if k == "PROJECT" else 1, 0, 0, 0])
        grow(r)
        T(r, k, 10, PLEX_B, PALE, w=110, ls="8%")
        T(r, v, 13 if k != "PROJECT" else 18, PLEX_B, WHITE)


# ================================================================ SWISS: "International"
def swiss():
    INK, RED, GREY, PAPER = "#111111", "#E30613", "#6B6B6B", "#FFFFFF"
    I4, I5, I7, I9 = ("Inter", "Regular"), ("Inter", "Medium"), ("Inter", "Bold"), ("Inter", "Black")
    pg = page("Swiss · International", PAPER)
    nav = F(pg, "Nav", layout="horizontal", w=W, h=64, padding=[0, PAD, 0, PAD], mainAlign="spaceBetween", crossAlign="center",
            stroke=INK, strokeWeight=2, strokeSides=[0, 0, 1, 0])
    T(nav, "Arduino Di Giosia", 15, I7, INK)
    links = F(nav, "Links", layout="horizontal", gap=32)
    for i, l in enumerate(("Profile", "Experience", "Projects", "Workflow", "Contact")):
        T(links, f"{i + 1:02d}  {l}", 13, I5, RED if i == 0 else INK)

    hero = F(pg, "Hero", w=W, h=700)
    F(hero, "Red block", w=360, h=360, x=PAD, y=90, fill=RED)
    T(hero, "Engineering\nleadership\n\nSenior\nTypeScript/PHP\n\nNottingham, UK", 12, I7, INK, x=PAD, y=474, lh=16)
    T(hero, "Hands-\non\nengineering\nleader-\nship.", 108, I9, INK, x=PAD + 160, y=80, lh=98, ls="-4%")
    T(hero, LEAD, 16, I4, INK, x=1040, y=120, lh=25, name="Lead")
    setp({"$ref": steps[-1]["as"]}, width=280, textAutoResize="height")
    col = F(hero, "Links", layout="vertical", gap=0, w=280, x=1040, y=360)
    for i, (_, label) in enumerate(CTAS):
        r = F(col, label, layout="horizontal", padding=[14, 0, 14, 0], mainAlign="spaceBetween", stroke=INK, strokeWeight=1,
              strokeSides=[1, 0, 0, 0])
        grow(r)
        T(r, label, 15, I7, RED if i == 0 else INK)
        T(r, "→", 15, I7, RED if i == 0 else INK)

    # metrics as a row of big numerals
    met = F(pg, "Signal", layout="horizontal", w=W, padding=[0, PAD, 0, PAD], gap=0)
    for i, (v, label) in enumerate(METRICS):
        c = F(met, f"Metric {i}", layout="vertical", gap=10, padding=[24, 20, 40, 0 if i == 0 else 20], stroke=INK,
              strokeWeight=2, strokeSides=[1, 0, 0, 0 if i == 0 else 1])
        grow(c)
        T(c, v, 56 if len(v) < 7 else 34, I9, RED if i == 0 else INK, ls="-3%")
        T(c, label, 13, I4, GREY, fill=True, lh=19)
        setp(c, sizingV="fill")

    def section(num, title):
        s = F(pg, title, layout="horizontal", w=W, padding=[96, PAD, 40, PAD], gap=40)
        T(s, num, 160, I9, RED, lh=130, ls="-6%", w=300)
        right = F(s, "Content", layout="vertical", gap=24)
        grow(right)
        T(right, title, 44, I9, INK, ls="-3%")
        return right

    r = section("02", "Recent work")
    for title, co, place, dates, bullets in ROLES:
        row = F(r, co, layout="horizontal", gap=32, padding=[18, 0, 18, 0], stroke=INK, strokeWeight=1, strokeSides=[1, 0, 0, 0])
        grow(row)
        T(row, dates, 13, I5, GREY, w=190)
        t = F(row, "Role", layout="vertical", gap=2, w=260)
        T(t, title, 18, I7, INK, fill=True)
        T(t, f"{co}, {place}", 14, I4, GREY, fill=True)
        b = F(row, "Points", layout="vertical", gap=6)
        grow(b)
        for x in bullets:
            T(b, x, 14, I4, INK, fill=True, lh=20)

    r = section("03", "Personal projects")
    g = F(r, "Grid", layout="horizontal", gap=0)
    grow(g)
    for i, (name, label, body) in enumerate(PROJECTS):
        c = F(g, name, layout="vertical", gap=10, padding=[20, 20, 32, 20], fill=RED if i == 0 else None,
              stroke=INK, strokeWeight=1, strokeSides=[2, 0 if i < 3 else 0, 0, 0 if i == 0 else 1])
        grow(c)
        ink = PAPER if i == 0 else INK
        T(c, f"0{i + 1}", 13, I7, ink)
        T(c, name, 30, I9, ink, ls="-3%")
        T(c, label, 13, I7, ink)
        T(c, body, 13, I4, ink if i == 0 else GREY, fill=True, lh=19)

    ct = F(pg, "Contact", layout="horizontal", w=W, padding=[96, PAD, 96, PAD], gap=40, fill=INK)
    T(ct, "05", 160, I9, RED, lh=130, ls="-6%", w=300)
    right = F(ct, "Content", layout="vertical", gap=20)
    grow(right)
    T(right, "Engineering judgment, code credibility and management experience in one place.", 40, I9, PAPER, fill=True, lh=44, ls="-3%")
    lk = F(right, "Links", layout="horizontal", gap=36, wrap=True, crossGap=12)
    grow(lk)
    for _, label in CONTACT:
        T(lk, label, 16, I7, PAPER)
    ft = F(pg, "Footer", layout="horizontal", w=W, padding=[20, PAD, 28, PAD], mainAlign="spaceBetween")
    T(ft, "Arduino Di Giosia · Engineering leader and senior engineer", 12, I5, INK)
    T(ft, "Set in Inter. Grid: 12 columns, 120 px margins.", 12, I5, GREY)


# ================================================================ ARCADE: "Insert coin" (original; inspired by 80s bubble arcade games)
def arcade():
    BLACK, WHITE, RED, YELLOW, CYAN, MAGENTA, GREEN, BLUE = "#000000", "#FFFFFF", "#FF3B3B", "#FFE135", "#3CE7FF", "#FF4FD8", "#5CFF6B", "#3B6BFF"
    PIX = ("Press Start 2P", "Regular")
    pg = page("Arcade · Insert coin", BLACK)

    def bricks(parent, width, color, rows=2, name="Bricks"):
        b = F(parent, name, w=width, h=rows * 20)
        for r in range(rows):
            off = 0 if r % 2 == 0 else -20
            for i in range(off, width, 40):
                x0 = max(i, 0)
                w = min(38, i + 38 - x0, width - x0)
                if w > 2:
                    F(b, "brick", w=w, h=18, x=x0, y=r * 20, fill=color)
        return b

    def bubble(parent, x, y, d, color, value=None, label=None, fs=22):
        bb = F(parent, f"Bubble {value or ''}", w=d, h=d, x=x, y=y)
        S("node.create", {"type": "ellipse", "parent": bb, "x": 0, "y": 0, "width": d, "height": d, "select": False, "name": "skin",
                          "props": {"fill": color, "opacity": 0.16}}, ref=False)
        S("node.create", {"type": "ellipse", "parent": bb, "x": 0, "y": 0, "width": d, "height": d, "select": False, "name": "rim",
                          "props": {"fill": None, "stroke": color, "strokeWeight": 3}}, ref=False)
        S("node.create", {"type": "ellipse", "parent": bb, "x": d * 0.2, "y": d * 0.14, "width": d * 0.16, "height": d * 0.1,
                          "select": False, "name": "shine", "props": {"fill": WHITE, "opacity": 0.85, "rotation": -30}}, ref=False)
        if value:
            T(bb, value, fs, PIX, WHITE, x=0, y=d * 0.36, w=d, align="center")
            T(bb, label, 11, PLEX_B, color, x=d * 0.14, y=d * 0.36 + fs + 16, w=d * 0.72, align="center")
        return bb

    # HUD
    hud = F(pg, "HUD", layout="horizontal", w=W, h=84, padding=[0, PAD, 0, PAD], mainAlign="spaceBetween", crossAlign="center")
    for top, val, c in (("1UP", "000020", RED), ("HI-SCORE", "2026", RED), ("2UP", "INSERT COIN", CYAN)):
        col = F(hud, top, layout="vertical", gap=8, crossAlign="center")
        T(col, top, 14, PIX, c)
        T(col, val, 16, PIX, WHITE if top != "2UP" else YELLOW)
    menu = F(pg, "Menu", layout="horizontal", w=W, padding=[0, PAD, 0, PAD], gap=34)
    for i, l in enumerate(("PROFILE", "EXPERIENCE", "PROJECTS", "WORKFLOW", "CONTACT")):
        T(menu, ("▶ " if i == 0 else "  ") + l, 12, PIX, YELLOW if i == 0 else WHITE)

    # hero
    hero = F(pg, "Hero", layout="horizontal", w=W, padding=[56, PAD, 24, PAD], gap=40, crossAlign="center")
    left = F(hero, "Copy", layout="vertical", gap=24)
    grow(left)
    T(left, "ROUND 1  ·  ARDUINO DI GIOSIA", 13, PIX, GREEN)
    h = F(left, "Headline", layout="vertical", gap=14)
    for word, c in (("HANDS-ON", YELLOW), ("ENGINEERING", CYAN), ("LEADERSHIP!", MAGENTA)):
        T(h, word, 44, PIX, c)
    T(left, LEAD, 16, PLEX, "#D6D6E6", lh=27, fill=True)
    cta = F(left, "Buttons", layout="horizontal", gap=16, wrap=True, crossGap=16)
    grow(cta)
    for i, (_, label) in enumerate(CTAS):
        c = [RED, BLUE, BLUE, BLUE][i]
        b = F(cta, label, layout="horizontal", padding=[14, 18, 14, 18], fill=c, stroke=WHITE if i == 0 else BLACK, strokeWeight=3)
        T(b, ("PRESS START: " if i == 0 else "") + label.upper(), 11, PIX, WHITE)
    art = F(hero, "Bubbles", w=520, h=520)
    bubble(art, 20, 10, 230, CYAN, METRICS[0][0], METRICS[0][1], fs=34)
    bubble(art, 270, 60, 210, MAGENTA, METRICS[1][0], METRICS[1][1], fs=26)
    bubble(art, 60, 260, 200, GREEN, METRICS[2][0], METRICS[2][1], fs=24)
    bubble(art, 290, 290, 200, YELLOW, "v1", "in minutes: first version AI-generated, then iterated", fs=30)
    for x, y, d in ((470, 20, 28), (0, 220, 22), (250, 470, 18), (500, 240, 16)):
        bubble(art, x, y, d, WHITE)
    plat = F(pg, "Platform", layout="horizontal", w=W, padding=[0, PAD, 0, PAD])
    bricks(plat, CW, MAGENTA, rows=2)

    # high scores (experience)
    sec = F(pg, "High scores", layout="vertical", w=W, padding=[72, PAD, 56, PAD], gap=28, crossAlign="center")
    T(sec, "BEST PLAYERS · EXPERIENCE", 22, PIX, RED)
    tbl = F(sec, "Table", layout="vertical", gap=26, w=1000)
    head = F(tbl, "Head", layout="horizontal", gap=24)
    grow(head)
    for t, w in (("RANK", 120), ("YEARS", 260), ("ROLE", None)):
        x = T(head, t, 12, PIX, WHITE, w=w)
        if not w:
            grow(x)
    for i, (title, co, place, dates, bullets) in enumerate(ROLES):
        c = [YELLOW, CYAN, MAGENTA][i]
        row = F(tbl, co, layout="horizontal", gap=24)
        grow(row)
        T(row, ["1ST", "2ND", "3RD"][i], 16, PIX, c, w=120)
        T(row, dates.replace(" – ", "-").upper(), 11, PIX, c, w=260)
        r = F(row, "Role", layout="vertical", gap=8)
        grow(r)
        T(r, f"{title.upper()} · {co.upper()}", 13, PIX, c, fill=True, lh=20)
        T(r, " · ".join(bullets), 13, PLEX, "#BFC3D9", fill=True, lh=20)

    # stage select (projects)
    sec = F(pg, "Stage select", layout="vertical", w=W, padding=[40, PAD, 64, PAD], gap=28)
    T(sec, "SELECT STAGE · PROJECTS", 22, PIX, CYAN)
    grid = F(sec, "Stages", layout="horizontal", gap=24)
    grow(grid)
    gems = [RED, YELLOW, GREEN, MAGENTA]
    for i, (name, label, body) in enumerate(PROJECTS):
        card = F(grid, name, layout="vertical", gap=12, padding=20, stroke=gems[i], strokeWeight=4)
        grow(card)
        top = F(card, "Top", layout="horizontal", mainAlign="spaceBetween", crossAlign="center")
        grow(top)
        T(top, f"ROUND {i + 2}", 11, PIX, gems[i])
        gem = F(top, "Item", w=24, h=24)
        for (gx, gy) in ((8, 0), (0, 8), (8, 8), (16, 8), (8, 16)):
            F(gem, "px", w=8, h=8, x=gx, y=gy, fill=gems[i])
        T(card, name.upper(), 18, PIX, WHITE)
        T(card, label, 12, PLEX_B, gems[i])
        T(card, body, 13, PLEX, "#BFC3D9", fill=True, lh=19)
    plat = F(pg, "Platform 2", layout="horizontal", w=W, padding=[0, PAD, 0, PAD])
    bricks(plat, CW, CYAN, rows=1)

    # continue (contact)
    ct = F(pg, "Continue", layout="vertical", w=W, padding=[72, PAD, 56, PAD], gap=26, crossAlign="center")
    T(ct, "CONTINUE?", 40, PIX, YELLOW)
    T(ct, "9", 72, PIX, RED)
    T(ct, "INSERT COIN TO TALK ENGINEERING", 13, PIX, WHITE)
    lk = F(ct, "Links", layout="horizontal", gap=20, wrap=True, crossGap=16, mainAlign="center")
    for i, (_, label) in enumerate(CONTACT):
        b = F(lk, label, layout="horizontal", padding=[12, 16, 12, 16], stroke=[RED, CYAN, MAGENTA, GREEN][i], strokeWeight=3)
        T(b, label, 14, PLEX_B, WHITE)
    ft = F(pg, "Footer", layout="horizontal", w=W, padding=[24, PAD, 32, PAD], mainAlign="spaceBetween")
    T(ft, "© 2026 ARDUINO DI GIOSIA", 11, PIX, "#8A8FA8")
    T(ft, "CREDIT 01", 11, PIX, YELLOW)


THEMES = {"christmas": (christmas, ["plex", "dmserif"]), "terminal": (terminal, ["plex", "vt323"]),
          "blueprint": (blueprint, ["plex", "architects"]), "swiss": (swiss, ["inter"]),
          "arcade": (arcade, ["plex", "pixel"])}

if __name__ == "__main__":
    theme, fdir = sys.argv[1], sys.argv[2]
    fn, fl = THEMES[theme]
    fonts(fdir, fl)
    fn()
    for s in steps:
        print(json.dumps(s, ensure_ascii=False))
