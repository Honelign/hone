"""Maps the raw Figma exports in icons_svg/ to named SVGs in icons_clean/.

Figma names each exported variant after its layer ("style=outline"), and
numbers repeats of the *exact same layer name* in layer order:
"style=outline.svg", "style=outline-1.svg", ... The catalog
(scripts/icons_catalog.json) lists each page's icons in that same layer
order, with every variant's exact layer name. So the k-th occurrence of a
layer name in the catalog is the export numbered k.

Matching on the exact layer name (not the icon's position on the page)
matters: the Figma file has misspelled layers ("filled", "oultine",
"two ton", ...) and icons without some styles, which shift the numbering
of the following icons for that style only.

Pages missing from the catalog are skipped rather than guessed.

Icon ids are unique across all pages (a repeated name gets "_2", "_3"...
in folder order), and icons_clean/manifest.json records each id's page
and Figma name for generate_icon_registry.py.
"""

import json
import re
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR / "scripts" / "icons_catalog.json"
ICONS_SVG_DIR = BASE_DIR / "icons_svg"
CLEAN_DIR = BASE_DIR / "icons_clean"

with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
    catalog_icons = json.load(f)

# Group catalog icons by page, keeping layer order.
catalog_by_page = {}
for item in catalog_icons:
    catalog_by_page.setdefault(item['page'], []).append(item)

FOLDER_TO_PAGE = {
    'ai': 'AI (Artificial intelligence)',
    'arrows': 'Arrows',
    'bookmark': 'Bookmark',
    'camera,image': 'Camera, Image',
    'cloud,hosting': 'Cloud, Hosting',
    'connectivity,signal': 'Connectivity, Signal',
    'database': 'Database',
    'date': 'Date',
    'devices': 'Devices',
    'e-commerce': 'E-Commerce',
    'electronics': 'Electronics ',
    'emogi,stickers': 'Emoji, Sticker',
    'essentials': 'Essential',
    'files': 'File',
    'financial,business': 'Financial, Business',
    'folder': 'Folder',
    'general': 'General',
    'gift,celebration': 'Gift, Celebration',
    'home': 'Home',
    'layout': 'Layout, Grid',
    'link': 'Link',
    'mail': 'Mail',
    'map': 'Map, Location',
    'message': 'Meseage, Notification',
    'multimedia': 'Multimedia',
    'reward': 'Reward',
    'security': 'Security',
    'server': 'Server',
    'space,astronomy': 'Space, Astronomy',
    'store': 'Store',
    'technology': 'Technology',
    'time': 'Time',
    'trip': 'Trip, Travel',
    'user': 'Users',
    'video': 'Video',
    'watch': 'Watch',
    'weather': 'Weather',
}

# Variant layer names (after "style=") -> output style folder, including
# the misspellings used in the Figma file.
STYLE_MAP = {
    'outline': 'Outline',
    'oultine': 'Outline',
    'linear': 'Linear',
    'llinear': 'Linear',
    'bold': 'Bold',
    'filled': 'Bold',
    'bulk': 'Bulk',
    'bul': 'Bulk',
    'duotone': 'Duotone',
    'two ton': 'Duotone',
    'two tone': 'Duotone',
    'tow tone': 'Duotone',
    'two color': 'TwoColor',
    'two  color': 'TwoColor',
    'gestalt': 'Gestalt',
}
ALL_STYLES = sorted(set(STYLE_MAP.values()))


def clean_id(name: str) -> str:
    name = re.sub(r'[^a-zA-Z0-9_\-\s]', '', name)
    words = [w for w in re.split(r'[-_\s]+', name) if w]
    if not words:
        return "icon"
    first = words[0].lower()
    if first[0].isdigit():
        first = "icon" + first
    return first + "".join(w.capitalize() for w in words[1:])


_NUMBER = re.compile(r'[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?')
# Commands whose last two numbers are the end point, so a NaN segment can
# become a straight line to it.
_LINEABLE = set('LlCcSsQqTt')


def _sanitize_path_data(d_val: str) -> str:
    """Rewrites path data with Figma's NaN segments (degenerate curves such
    as "C-nan -nan -nan -nan 13.07 22.21" or "Lnan nan").

    A NaN segment with a finite end point becomes a line to it; one
    without is dropped. "nan" is replaced by a marker first: its letters
    are SVG commands ("n" is not, but "a" is the arc command).
    """
    marked = re.sub(r'[-+]?nan', ' X ', d_val, flags=re.IGNORECASE)
    out = []
    for cmd, args in re.findall(r'([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)', marked):
        if 'X' not in args:
            out.append(cmd + args)
            continue
        tokens = re.findall(r'X|' + _NUMBER.pattern, args)
        end = tokens[-2:]
        if cmd in _LINEABLE and len(end) == 2 and 'X' not in end:
            line = 'L' if cmd.isupper() else 'l'
            out.append(f"{line}{end[0]} {end[1]}")
        # else: no usable end point, drop the segment
    # A path must start with a move-to; if the first one was dropped, the
    # next segment's end point becomes it.
    if out and out[0][0] not in 'Mm':
        first = re.findall(_NUMBER, out[0])
        out[0] = f"M{first[-2]} {first[-1]}" if len(first) >= 2 else ''
    return ''.join(out)


def sanitize_svg_content(content: str) -> str:
    if 'nan' not in content.lower():
        return content
    return re.sub(
        r'd="([^"]+)"',
        lambda m: f'd="{_sanitize_path_data(m.group(1))}"',
        content)


def style_of(label: str, icon_styles: set) -> str | None:
    """The output style for a variant layer name like "style=bold"."""
    if not label.startswith('style='):
        return None  # e.g. "Property 1=bold": never exported as style=*
    raw = label.split('=', 1)[1].strip()
    if raw == 'Default':
        # "Default" stands in for the one style the icon lacks.
        lacking = [s for s in ALL_STYLES if s not in icon_styles]
        return lacking[0] if len(lacking) == 1 else None
    return STYLE_MAP.get(raw)


if CLEAN_DIR.exists():
    shutil.rmtree(CLEAN_DIR)
for norm_style in ALL_STYLES:
    (CLEAN_DIR / norm_style).mkdir(parents=True, exist_ok=True)

total_mapped = 0
sanitized_count = 0
# Global, so the same name on two pages cannot overwrite one SVG.
name_tracker = {}
manifest = {}
skipped_folders = []

disk_folders = [f for f in ICONS_SVG_DIR.iterdir() if f.is_dir()]

for folder in sorted(disk_folders, key=lambda x: x.name.lower()):
    page_name = FOLDER_TO_PAGE.get(folder.name.lower())
    page_icons = catalog_by_page.get(page_name, [])
    files = {f.stem: f for f in folder.glob("style=*.svg")}
    if not files:
        skipped_folders.append(f"{folder.name} (no style=* exports)")
        continue
    if not page_icons:
        skipped_folders.append(
            f"{folder.name} (page '{page_name}' not in catalog, "
            f"{len(files)} files)")
        continue

    seen_labels = {}
    folder_mapped = 0
    missing = 0
    used = set()
    for entry in page_icons:
        cid = clean_id(entry['name'])
        if cid in name_tracker:
            name_tracker[cid] += 1
            cid = f"{cid}_{name_tracker[cid]}"
        else:
            name_tracker[cid] = 1

        manifest[cid] = {'page': page_name.strip(), 'name': entry['name']}
        labels = [label for _, label in entry['variants']]
        icon_styles = {
            STYLE_MAP.get(l.split('=', 1)[-1].strip()) for l in labels
        } - {None}
        for label in labels:
            # Number every exact layer name, mapped or not, so later
            # icons keep their numbers.
            k = seen_labels.get(label, 0)
            seen_labels[label] = k + 1
            norm_style = style_of(label, icon_styles)
            if norm_style is None:
                continue
            f = files.get(label if k == 0 else f"{label}-{k}")
            if f is None:
                missing += 1
                continue
            used.add(f.stem)

            content = f.read_text(encoding='utf-8')
            if 'nan' in content.lower():
                content = sanitize_svg_content(content)
                sanitized_count += 1
            (CLEAN_DIR / norm_style / f"{cid}.svg").write_text(
                content, encoding='utf-8')
            folder_mapped += 1

    unused = sorted(set(files) - used)
    print(f"Folder '{folder.name}': mapped {folder_mapped} "
          f"(page '{page_name}', missing {missing}, unused {len(unused)})")
    total_mapped += folder_mapped

# Only ids that got at least one SVG.
written = {f.stem for f in CLEAN_DIR.glob("*/*.svg")}
(CLEAN_DIR / "manifest.json").write_text(json.dumps(
    {k: v for k, v in sorted(manifest.items()) if k in written},
    indent=1, ensure_ascii=False), encoding='utf-8')

print("\n==========================================")
print(f"TOTAL MAPPED FILES ACROSS ALL CATEGORIES: {total_mapped}")
print(f"Sanitized Figma NaN paths: {sanitized_count}")
print("==========================================")
for norm_style in ALL_STYLES:
    count = len(list((CLEAN_DIR / norm_style).glob("*.svg")))
    print(f"  - {norm_style}: {count} unique SVGs")
if skipped_folders:
    print("\nSkipped (not mapped):")
    for name in skipped_folders:
        print(f"  - {name}")
