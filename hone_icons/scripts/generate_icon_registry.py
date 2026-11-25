import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# Written by map_all_categories.py: icon id -> its Figma page and name.
MANIFEST_PATH = BASE_DIR / "icons_clean" / "manifest.json"
LIB_SRC = BASE_DIR / "lib" / "src"
OUT_FILE = BASE_DIR.parent / "icon_finder" / "lib" / "icon_registry.dart"

DART_KEYWORDS = {
    'abstract', 'as', 'assert', 'async', 'await', 'base', 'break', 'case', 'catch',
    'class', 'const', 'continue', 'covariant', 'default', 'deferred', 'do', 'dynamic',
    'else', 'enum', 'export', 'extends', 'extension', 'external', 'factory', 'false',
    'final', 'finally', 'for', 'Function', 'get', 'hide', 'if', 'implements', 'import',
    'in', 'interface', 'is', 'late', 'library', 'mixin', 'new', 'null', 'of', 'on',
    'operator', 'part', 'required', 'rethrow', 'return', 'sealed', 'set', 'show',
    'static', 'super', 'switch', 'sync', 'this', 'throw', 'true', 'try', 'type',
    'typedef', 'var', 'void', 'when', 'while', 'with', 'yield'
}

def safe_id(name: str) -> str:
    if name in DART_KEYWORDS:
        return f"icon{name.capitalize()}"
    return name

# Parse all available icon identifiers per style from hone_icons/lib/src/*.dart
styles = ['outline', 'linear', 'bold', 'bulk', 'duotone', 'twocolor', 'gestalt']
style_classes = {
    'outline': 'HoneIconsOutline',
    'linear': 'HoneIconsLinear',
    'bold': 'HoneIconsBold',
    'bulk': 'HoneIconsBulk',
    'duotone': 'HoneIconsDuotone',
    'twocolor': 'HoneIconsTwoColor',
    'gestalt': 'HoneIconsGestalt',
}

icons_by_style = {}
for s in styles:
    fpath = LIB_SRC / f"hone_icons_{s}.dart"
    content = fpath.read_text(encoding='utf-8')
    matches = set(re.findall(r'static const IconData ([a-zA-Z0-9_]+) =', content))
    icons_by_style[s] = matches
    print(f"Style '{s}': {len(matches)} icons")

# Category of each icon, from the same mapping that named its SVGs.
with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
    manifest = json.load(f)
cat_map = {safe_id(cid): (info['page'], info['name'])
           for cid, info in manifest.items()}

# All unique icon names (union across all styles)
all_names = sorted(list(set.union(*[icons_by_style[s] for s in styles])))
print(f"Total unique icon names across all styles: {len(all_names)}")

# Generate human readable label from camelCase (e.g. "aiBrainTop" -> "AI Brain Top")
def to_label(s: str) -> str:
    # A repeated Figma name gets "_2", "_3": label it "Name (2)".
    repeat = re.fullmatch(r'(.+)_(\d+)', s)
    if repeat:
        return f"{to_label(repeat.group(1))} ({repeat.group(2)})"
    # Handle ai prefix
    if s.startswith("ai") and len(s) > 2 and s[2].isupper():
        rest = re.sub(r'([A-Z])', r' \1', s[2:]).strip()
        return f"AI {rest}"
    # Replace numbers with space + number
    s = re.sub(r'(\d+)', r' \1', s)
    s = re.sub(r'([A-Z])', r' \1', s).strip()
    return s.title()

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    f.write("// GENERATED REGISTRY FOR ICON FINDER WEB APP\n")
    f.write("import 'package:hone_icons/hone_icons.dart';\n\n")
    
    f.write("""enum HoneIconStyle {
  outline('Outline'),
  linear('Linear'),
  bold('Bold'),
  bulk('Bulk'),
  duotone('Duotone'),
  twoColor('Two Color'),
  gestalt('Gestalt');

  final String label;
  const HoneIconStyle(this.label);
}

class IconItem {
  final String id;
  final String name;
  final String category;
  final Map<HoneIconStyle, IconData> styles;

  const IconItem({
    required this.id,
    required this.name,
    required this.category,
    required this.styles,
  });

  IconData get defaultIcon => styles[HoneIconStyle.outline] ?? styles.values.first;

  IconData getIcon(HoneIconStyle style) => styles[style] ?? defaultIcon;

  bool hasStyle(HoneIconStyle style) => styles.containsKey(style);
}

""")
    
    f.write("final List<IconItem> kAllIcons = [\n")
    
    for name in all_names:
        page_info = cat_map.get(name)
        if page_info:
            raw_category, original_name = page_info
            category = re.sub(r'\(.*?\)', '', raw_category).strip()
        else:
            raise SystemExit(f"{name} is not in {MANIFEST_PATH.name}; "
                             "re-run map_all_categories.py")
            
        label = to_label(name)
        
        style_entries = []
        if name in icons_by_style['outline']:
            style_entries.append(f"HoneIconStyle.outline: HoneIconsOutline.{name}")
        if name in icons_by_style['linear']:
            style_entries.append(f"HoneIconStyle.linear: HoneIconsLinear.{name}")
        if name in icons_by_style['bold']:
            style_entries.append(f"HoneIconStyle.bold: HoneIconsBold.{name}")
        if name in icons_by_style['bulk']:
            style_entries.append(f"HoneIconStyle.bulk: HoneIconsBulk.{name}")
        if name in icons_by_style['duotone']:
            style_entries.append(f"HoneIconStyle.duotone: HoneIconsDuotone.{name}")
        if name in icons_by_style['twocolor']:
            style_entries.append(f"HoneIconStyle.twoColor: HoneIconsTwoColor.{name}")
        if name in icons_by_style['gestalt']:
            style_entries.append(f"HoneIconStyle.gestalt: HoneIconsGestalt.{name}")
            
        styles_map_code = "{" + ", ".join(style_entries) + "}"
        f.write(f"  IconItem(id: '{name}', name: '{label}', category: '{category}', styles: {styles_map_code}),\n")
        
    f.write("];\n\n")
    
    # Also export all categories list
    categories = sorted(list(set(re.sub(r'\(.*?\)', '', cat_map.get(n, ("General", ""))[0]).strip() for n in all_names)))
    f.write(f"final List<String> kAllCategories = {json.dumps(categories)};\n")

print(f"Generated {OUT_FILE} with {len(all_names)} icons across {len(categories)} categories!")
