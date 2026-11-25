import json
import re
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR / "scripts" / "icons_catalog.json"
AI_STYLES_DIR = BASE_DIR / "icons_svg" / "AI styles"
CLEAN_DIR = BASE_DIR / "icons_clean"

with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
    icons = json.load(f)

ai_icons = [i for i in icons if i['page'] == 'AI (Artificial intelligence)']

def clean_id(name: str) -> str:
    name = re.sub(r'[^a-zA-Z0-9_\-\s]', '', name)
    words = re.split(r'[-_\s]+', name)
    words = [w for w in words if w]
    if not words:
        return "icon"
    first = words[0].lower()
    if first[0].isdigit():
        first = "icon" + first
    rest = [w.capitalize() for w in words[1:]]
    return first + "".join(rest)

# Handle duplicate names in catalog by assigning unique IDs
unique_names = {}
name_tracker = {}
for idx, entry in enumerate(ai_icons):
    cid = clean_id(entry['name'])
    if cid in name_tracker:
        name_tracker[cid] += 1
        cid = f"{cid}_{name_tracker[cid]}"
    else:
        name_tracker[cid] = 1
    unique_names[idx] = cid

STYLE_MAP = {
    'outline': 'Outline',
    'linear': 'Linear',
    'bold': 'Bold',
    'filled': 'Bold',
    'bulk': 'Bulk',
    'duotone': 'Duotone',
    'two color': 'TwoColor',
    'gestalt': 'Gestalt',
}

if CLEAN_DIR.exists():
    shutil.rmtree(CLEAN_DIR)
CLEAN_DIR.mkdir(parents=True)

for norm_style in set(STYLE_MAP.values()):
    (CLEAN_DIR / norm_style).mkdir(parents=True, exist_ok=True)

all_files = list(AI_STYLES_DIR.glob("*.svg"))

mapped_count = 0
for f in all_files:
    stem = f.stem
    m = re.match(r'style=([a-zA-Z0-9\s]+?)(?:-(\d+))?$', stem)
    if not m:
        continue
    raw_style = m.group(1).strip()
    idx_str = m.group(2)
    index = int(idx_str) if idx_str else 0
    
    norm_style = STYLE_MAP.get(raw_style)
    if not norm_style or index not in unique_names:
        continue
        
    cid = unique_names[index]
    dest_file = CLEAN_DIR / norm_style / f"{cid}.svg"
    shutil.copy2(f, dest_file)
    mapped_count += 1

print(f"\nSuccessfully mapped & renamed: {mapped_count} files!")
for norm_style in sorted(set(STYLE_MAP.values())):
    count = len(list((CLEAN_DIR / norm_style).glob("*.svg")))
    print(f"  - {norm_style}: {count} SVGs")
