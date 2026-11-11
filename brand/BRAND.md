# orku brand kit

Everything needed to reproduce the orku look, as used on https://orku.ai. The files in this folder are self-contained; copy the folder as a whole.

## Files

| File | What it is |
|---|---|
| `orku-logo.svg` | The wordmark "orku". Primary logo. |
| `orku-mark.svg` | The "o" on its own. Favicon, app icon, avatar, small spaces. |
| `background.svg` | Sand background with faint contour lines, 1600 × 1000, scales to cover any size. |
| `background.png` | The same as a bitmap, 3200 × 2000. |
| `contours.svg` | Only the faint contour lines, transparent, to lay over any sand surface. |
| `contours-glow.svg` | The same lines in warm orange with a soft halo: the "lit" state shown around the pointer on the site. |
| `tokens.css` | The colours as CSS custom properties. |

## Colours

| Name | Hex | Use |
|---|---|---|
| Sand | `#F6F1E6` | Background. The brand is light: sand is the default surface. |
| Ink | `#18191A` | Logo, text. Near-black, never pure `#000`. |
| Amber | `#F6B04F` | Outer wedge in the "o". Accent only. |
| Ember | `#D63F1C` | Inner wedge in the "o", the "core". Accent only, smallest amount. |
| Glow | `#E8843A` | Contour lines lit up on interaction. |

Contour lines: Ink at 7 % opacity (1 px), every fifth line at 11 %.

Proportion: mostly sand, ink for the logo and type, and amber/ember only as small accents, as in the logo itself.

## Logo

- The wordmark is drawn geometry, not a typeface. Always use the SVG; never retype "orku" in a font.
- Lowercase only: "orku", also in running text.
- Ink on sand. Keep clear space around it of at least the height of the "o".
- Keep it small and calm: on the site it is 140 px wide on desktop, 104 px on phones, centred, with nothing else on the page.
- Don't recolour, stretch, outline or add effects. The wedge in the "o" may rotate (see Motion); nothing else moves.
- The "o" mark alone is the favicon and works as a square avatar on sand or on ink.

## Background

A topographic map: smooth, organic contour lines, very faint, so the surface reads as sand with a texture rather than a pattern. Lines are generated (seeded terrain, marching squares), not drawn; `tools/make-topo.py` in the repo regenerates them with a different `SEED` for a new landscape in the same style.

## Motion

- The wedge in the "o" turns to point at the cursor, easing gently (about 12 % of the remaining angle per frame), and returns to its rest position (pointing up-right) when the cursor leaves.
- The contour lines around the cursor light up in Glow orange through a soft circular spotlight (about 300 px radius, 55 % strength), fading in and out over 0.8 s.
- Always subtle. With `prefers-reduced-motion`, nothing moves.

## Tone of the visual style

Quiet, warm, earthy and precise: a lot of empty sand, one strong mark, a hint of terrain, and a small glowing core.
