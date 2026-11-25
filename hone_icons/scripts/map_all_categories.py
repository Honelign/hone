import json
import re
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR / "scripts" / "icons_catalog.json"
ICONS_SVG_DIR = BASE_DIR / "icons_svg"
CLEAN_DIR = BASE_DIR / "icons_clean"

with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
    catalog_icons = json.load(f)

# Group catalog icons by page
catalog_by_page = {}
for item in catalog_icons:
    page = item['page']
    if page not in catalog_by_page:
        catalog_by_page[page] = []
    catalog_by_page[page].append(item)

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

def sanitize_svg_content(content: str) -> str:
    if 'nan' not in content.lower():
        return content
    # Remove path segments with nan or replace nan coordinates
    def replace_d(match):
        d_val = match.group(1)
        # Remove any command segment containing nan
        cleaned = re.sub(r'[a-df-zA-DF-Z][^a-df-zA-DF-Z]*nan[^a-df-zA-DF-Z]*', '', d_val, flags=re.IGNORECASE)
        cleaned = re.sub(r'[-+]?nan', '0', cleaned, flags=re.IGNORECASE)
        return f'd="{cleaned}"'
    return re.sub(r'd="([^"]+)"', replace_d, content)

if CLEAN_DIR.exists():
    shutil.rmtree(CLEAN_DIR)
CLEAN_DIR.mkdir(parents=True)

for norm_style in set(STYLE_MAP.values()):
    (CLEAN_DIR / norm_style).mkdir(parents=True, exist_ok=True)

total_mapped = 0
sanitized_count = 0
unmapped_folders = []

disk_folders = [f for f in ICONS_SVG_DIR.iterdir() if f.is_dir()]

for folder in sorted(disk_folders, key=lambda x: x.name.lower()):
    fn_lower = folder.name.lower()
    page_name = FOLDER_TO_PAGE.get(fn_lower)
    
    style_files = list(folder.glob("style=*.svg"))
    if not style_files:
        unmapped_folders.append(folder.name)
        continue
        
    page_icons = catalog_by_page.get(page_name, [])
    named_files = [f.stem for f in folder.glob("*.svg") if not f.name.startswith("style=")]
    
    unique_names = {}
    name_tracker = {}
    
    if page_icons:
        for idx, entry in enumerate(page_icons):
            raw_name = entry['name']
            cid = clean_id(raw_name)
            if cid in name_tracker:
                name_tracker[cid] += 1
                cid = f"{cid}_{name_tracker[cid]}"
            else:
                name_tracker[cid] = 1
            unique_names[idx] = cid
    elif named_files:
        sorted_named = sorted(named_files)
        for idx, raw_name in enumerate(sorted_named):
            cid = clean_id(raw_name)
            if cid in name_tracker:
                name_tracker[cid] += 1
                cid = f"{cid}_{name_tracker[cid]}"
            else:
                name_tracker[cid] = 1
            unique_names[idx] = cid

    folder_mapped = 0
    for f in style_files:
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
        
        raw_content = f.read_text(encoding='utf-8')
        if 'nan' in raw_content.lower():
            sanitized = sanitize_svg_content(raw_content)
            dest_file.write_text(sanitized, encoding='utf-8')
            sanitized_count += 1
        else:
            dest_file.write_text(raw_content, encoding='utf-8')
            
        folder_mapped += 1
        
    print(f"Folder '{folder.name}': Mapped {folder_mapped} style files (Category: {page_name})")
    total_mapped += folder_mapped

print(f"\n==========================================")
print(f"TOTAL MAPPED FILES ACROSS ALL CATEGORIES: {total_mapped}")
print(f"Sanitized Figma NaN paths: {sanitized_count}")
print(f"==========================================")
for norm_style in sorted(set(STYLE_MAP.values())):
    count = len(list((CLEAN_DIR / norm_style).glob("*.svg")))
    print(f"  - {norm_style}: {count} unique SVGs")
