#!/usr/bin/env python3
"""Generate README.md from keymap.c for the Lily58 `nilquera` keymap.

Parses each `[_LAYER] = LAYOUT(...)` block, maps the keycodes to compact
labels, and renders each layer as a fixed-width ASCII schematic (inside a
code block) that mirrors the Lily58's physical layout: two 6-column halves,
the inner keys bridging the bottom row, and the 4-key thumb clusters below.
Run directly or via the git pre-commit hook.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
KEYMAP = os.path.join(HERE, "keymap.c")
README = os.path.join(HERE, "README.md")

# --- keycode -> label ------------------------------------------------------
SIMPLE = {
    "XXXXXXX": "", "KC_NO": "", "_______": "▽", "KC_TRNS": "▽",
    "QK_GESC": "Esc", "KC_ESC": "Esc", "KC_TAB": "Tab", "KC_SPC": "Spc",
    "KC_ENT": "Ent", "KC_BSPC": "Bsp", "KC_DEL": "Del", "KC_CAPS": "Caps",
    "KC_LSFT": "Shft", "KC_RSFT": "Shft", "KC_LCTL": "Ctrl", "KC_RCTL": "Ctrl",
    "KC_LALT": "Alt", "KC_RALT": "AltGr", "KC_LGUI": "GUI", "KC_RGUI": "GUI",
    "KC_LEFT": "←", "KC_DOWN": "↓", "KC_UP": "↑", "KC_RGHT": "→",
    "KC_PLUS": "+", "KC_MINS": "-", "KC_EQL": "=",
    "KC_LBRC": "[", "KC_RBRC": "]", "KC_BSLS": "\\",
    "ES_QUOT": "'", "ES_GRV": "`", "ES_NTIL": "Ñ", "ES_ACUT": "´",
    "ES_COMM": ",", "ES_DOT": ".", "ES_MINS": "-", "ES_LCBR": "{", "ES_RCBR": "}",
    "ES_LBRC": "[", "ES_RBRC": "]", "ES_PLUS": "+", "ES_CCED": "Ç",
    "ES_BSLS": "\\", "ES_LABK": "<", "ES_RABK": ">",
}
# compact modifier prefixes so combos stay narrow in the schematic
MODS = {
    "LCTL": "C+", "RCTL": "C+", "LSFT": "S+", "RSFT": "S+",
    "LALT": "A+", "RALT": "AGr+", "LGUI": "G+", "RGUI": "G+",
    "LCAG": "CAG+", "HYPR": "Hy+", "MEH": "Meh+",
}
LAYER_KEYS = {"MO", "TG", "TO", "TT", "DF", "OSL"}


def label(tok):
    tok = tok.strip()
    if tok in SIMPLE:
        return SIMPLE[tok]
    m = re.match(r"^(\w+)\((.*)\)$", tok)
    if m:
        fn, arg = m.group(1), m.group(2)
        if fn in LAYER_KEYS:
            name = arg.strip().lstrip("_")
            return name if fn == "MO" else f"{fn} {name}"
        if fn == "LT":
            lyr, kc = [a.strip() for a in arg.split(",", 1)]
            return f"{lyr.lstrip('_')}/{label(kc)}"
        if fn in MODS:
            return MODS[fn] + label(arg)
        return f"{fn}({label(arg)})"
    if re.match(r"^KC_[A-Z]$", tok) or re.match(r"^KC_[0-9]$", tok):
        return tok[3]
    m = re.match(r"^KC_F([0-9]{1,2})$", tok)
    if m:
        return "F" + m.group(1)
    if tok.startswith("KC_"):
        return tok[3:].title()
    if tok.startswith("ES_"):
        return tok[3:].title()
    return tok


# --- parsing ---------------------------------------------------------------
def split_top_level(text):
    """Split a comma-separated arg list, ignoring commas inside parens."""
    out, depth, cur = [], 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return [t.strip() for t in out]


def extract_layers(src):
    """Return list of (layer_name, [tokens]) in source order."""
    layers = []
    for m in re.finditer(r"\[(_\w+)\]\s*=\s*LAYOUT\(", src):
        name = m.group(1)
        i = m.end()
        depth, start = 1, i
        while i < len(src) and depth:
            if src[i] == "(":
                depth += 1
            elif src[i] == ")":
                depth -= 1
            i += 1
        layers.append((name, split_top_level(src[start:i - 1])))
    return layers


# --- rendering -------------------------------------------------------------
# Lily58: 58 keys. Index layout per LAYOUT() call:
#   r0: 0-5 L, 6-11 R          r1: 12-17 L, 18-23 R
#   r2: 24-29 L, 30-35 R       r3: 36-41 L, 42 innerL, 43 innerR, 44-49 R
#   thumbs: 50-53 L, 54-57 R
def _row(cells, w):
    return "|" + "|".join(c.center(w) for c in cells) + "|"


def _bar(n, w, left, mid, right):
    return left + mid.join(["-" * w] * n) + right


def render_layer(name, toks):
    title = f"### {name.lstrip('_')}\n\n"
    if len(toks) != 58:
        return title + f"_Could not render: expected 58 keys, found {len(toks)}._\n"

    lab = [label(t) for t in toks]
    w = max(3, max(len(x) for x in lab))

    def L(r):  # left 6 of a main row (rows store 6 left then 6 right)
        return lab[r * 12: r * 12 + 6] if r < 3 else lab[36:42]

    def R(r):  # right 6 of a main row
        return lab[r * 12 + 6: r * 12 + 12] if r < 3 else lab[44:50]

    gap = " " * (2 * w + 1)          # between halves on rows 0-2
    top = _bar(6, w, ",", "+", ".")
    sep = _bar(6, w, "+", "+", "+")

    lines = [top + gap + top]
    for r in (0, 1, 2):
        lines.append(_row(L(r), w) + gap + _row(R(r), w))
        lines.append(sep + gap + sep if r < 2 else _bar(14, w, "+", "+", "+"))
    # bottom row is one continuous 14-cell row: L0-5 | innerL | innerR | R0-5
    row3 = L(3) + [lab[42], lab[43]] + R(3)
    lines.append(_row(row3, w))
    lines.append(_bar(14, w, "`", "+", "'"))

    # thumb clusters: 4 keys each, tucked toward the centre
    indent = " " * (2 * w + 2)
    tgap = " " * (2 * w + 1)
    thumbL, thumbR = lab[50:54], lab[54:58]
    ttop = _bar(4, w, ",", "+", ".")
    tbot = _bar(4, w, "`", "+", "'")
    lines.append(indent + ttop + tgap + ttop)
    lines.append(indent + _row(thumbL, w) + tgap + _row(thumbR, w))
    lines.append(indent + tbot + tgap + tbot)

    return title + "```\n" + "\n".join(lines) + "\n```\n"


def main():
    with open(KEYMAP, encoding="utf-8") as f:
        src = f.read()
    layers = extract_layers(src)

    parts = [
        "# Lily58 — `nilquera` keymap",
        "",
        "Spanish (ES) layout. **Auto-generated from "
        "[`keymap.c`](keymap.c) by [`generate_readme.py`](generate_readme.py) "
        "via the git pre-commit hook — do not edit by hand.**",
        "",
        "**Legend** — empty cell = no key · `▽` = transparent (falls through to "
        "the layer below). Modifier combos use compact prefixes: "
        "`C+` Ctrl · `S+` Shift · `A+` Alt · `G+` GUI · `CAG+` Ctrl+Alt+GUI. "
        "`LOWER`/`RAISE` are held-to-switch layer keys.",
        "",
    ]
    for name, toks in layers:
        parts.append(render_layer(name, toks))
        parts.append("")

    with open(README, "w", encoding="utf-8") as f:
        f.write("\n".join(parts).rstrip() + "\n")
    print(f"Wrote {README} ({len(layers)} layers)")


if __name__ == "__main__":
    main()
