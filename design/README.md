# Theme designs

Design alternatives for erme2.com, made in [FigCraft](https://github.com/storytold/figcraft) before any code (decided 9 Nov 2026). Each theme has its own folder with the `.figcraft` file and a PNG preview. We decide which ones to develop, then implement them one at a time with the theme loader (#14).

| Theme | Folder | Ticket | Idea |
|-------|--------|--------|------|
| Christmas, "At home" | `christmas/` | #15 | An original 90s family-Christmas feel (inspired by the decade's Christmas comedies, nothing taken from any film). Pine, berry red and gold, DM Serif Display headings. The four numbers sit in the lit windows of a house at night, with a wreath on the door. Tartan dividers, roles as gift tags, projects as wrapped presents, fairy lights, candy-cane stripe, snow. "Buon Natale" and a panettone line in the footer. |
| Terminal, "tty" | `terminal/` | #16 | The page is a terminal session. VT323 pixel headline. Metrics as an `htop` panel, experience as `git log`, projects as `ls -la`, contact as command flags, blinking cursor. |
| Blueprint, "Sheet A1" | `blueprint/` | #17 | A technical drawing: grid paper, drawing frame with zones, handwritten annotations (Architects Daughter), the signal board as a dimensioned part, experience as a revision table, projects as a system diagram, a title block (drawn by, checked by Yaup, revision). |
| Arcade, "Insert coin" | `arcade/` | #20 | An original 80s arcade feel (inspired by bubble-shooting arcade games, no characters, logos or levels from any game). Black screen, Press Start 2P pixel type, neon brick platforms, the numbers inside floating bubbles, a 1UP / HI-SCORE bar, experience as a high-score table, projects as "select stage", contact as "Continue?". |
| Swiss, "International" | `swiss/` | #18 | International Typographic Style: Inter Black, one red, asymmetric grid, huge section numbers, rules instead of boxes, the headline broken across five lines. |

Inspired by, never copied: no characters, logos, artwork, scenes or quotes from films or games.

Why these go beyond colours: feedback on the current site is that it reads as AI-generated. Each design changes typography, layout details and adds personal touches. The copy is the live site's, shortened in places to fit a mockup; the implementation keeps the full copy.

## Regenerating

`build/build_themes.py` builds each file from scratch with FigCraft's command API:

```sh
npm i --prefix /tmp/fonts @expo-google-fonts/ibm-plex-mono @expo-google-fonts/dm-serif-display \
  @expo-google-fonts/vt323 @expo-google-fonts/architects-daughter @expo-google-fonts/inter \
  @expo-google-fonts/press-start-2p
for t in christmas terminal blueprint swiss arcade; do
  python3 design/build/build_themes.py $t /tmp/fonts/node_modules > /tmp/$t.jsonl
  figcraft-cli run /tmp/$t.jsonl --out design/$t/$t.figcraft
done
```

This overwrites the files. Once a design is being edited by hand in FigCraft, treat its `.figcraft` file as the source.
