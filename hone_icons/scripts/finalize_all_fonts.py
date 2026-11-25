import re
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = BASE_DIR / ".staging"
FONTS_DIR = BASE_DIR / "fonts"
LIB_DIR = BASE_DIR / "lib"
SRC_DIR = LIB_DIR / "src"

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

# 1. Copy Bold and Bulk TTF from staging
bold_ttf = STAGING_DIR / "test_bold" / "HoneIconsBold.ttf"
bulk_ttf = STAGING_DIR / "test_bulk" / "HoneIconsBulk.ttf"

if bold_ttf.exists():
    shutil.copy2(bold_ttf, FONTS_DIR / "HoneIconsBold.ttf")
    print("Copied HoneIconsBold.ttf to fonts/")

if bulk_ttf.exists():
    shutil.copy2(bulk_ttf, FONTS_DIR / "HoneIconsBulk.ttf")
    print("Copied HoneIconsBulk.ttf to fonts/")

# 2. Map of CSS files for generating Dart classes
css_sources = {
    'Bold': STAGING_DIR / "test_bold" / "HoneIconsBold.css",
    'Bulk': STAGING_DIR / "test_bulk" / "HoneIconsBulk.css",
    'Duotone': STAGING_DIR / "out_Duotone" / "HoneIconsDuotone.css",
    'Gestalt': STAGING_DIR / "out_Gestalt" / "HoneIconsGestalt.css",
    'Linear': STAGING_DIR / "out_Linear" / "HoneIconsLinear.css",
    'Outline': STAGING_DIR / "out_Outline" / "HoneIconsOutline.css",
    'TwoColor': STAGING_DIR / "out_TwoColor" / "HoneIconsTwoColor.css",
}

for style, css_path in css_sources.items():
    if not css_path.exists():
        print(f"CSS not found for {style}: {css_path}")
        continue
        
    font_name = f"HoneIcons{style}"
    content = css_path.read_text(encoding='utf-8')
    matches = re.findall(rf'\.{font_name}-([a-zA-Z0-9_\-]+)::before\s*{{\s*content:\s*"\\([a-fA-F0-9]+)"', content)
    
    dart_file = SRC_DIR / f"hone_icons_{style.lower()}.dart"
    with open(dart_file, 'w', encoding='utf-8') as df:
        df.write("// GENERATED CODE - DO NOT MODIFY BY HAND\n")
        df.write("import 'package:flutter/widgets.dart';\n\n")
        df.write(f"/// Icons for Hone design system ({style} style).\n")
        df.write(f"class HoneIcons{style} {{\n")
        df.write(f"  HoneIcons{style}._();\n\n")
        df.write(f"  static const String _fontFamily = '{font_name}';\n")
        df.write("  static const String _fontPackage = 'hone_icons';\n\n")
        
        for id_name, hex_code in sorted(matches, key=lambda x: x[0]):
            safe_name = safe_id(id_name)
            df.write(f"  static const IconData {safe_name} = IconData(0x{hex_code}, fontFamily: _fontFamily, fontPackage: _fontPackage);\n\n")
        df.write("}\n")
    print(f"Generated Dart for {style}: {dart_file.name} ({len(matches)} icons)")

# 3. Regenerate barrel file hone_icons.dart
all_styles = ['Bold', 'Bulk', 'Duotone', 'Gestalt', 'Linear', 'Outline', 'TwoColor']
barrel_file = LIB_DIR / "hone_icons.dart"
with open(barrel_file, 'w', encoding='utf-8') as bf:
    bf.write("// Hone Icons Package for Flutter\n")
    bf.write("library hone_icons;\n\n")
    bf.write("export 'package:flutter/widgets.dart' show IconData;\n")
    for style in all_styles:
        bf.write(f"export 'src/hone_icons_{style.lower()}.dart';\n")
    
    bf.write("\nimport 'src/hone_icons_outline.dart';\n")
    bf.write("\n/// Default alias for HoneIcons (points to HoneIconsOutline)\n")
    bf.write("typedef HoneIcons = HoneIconsOutline;\n")

print("Regenerated lib/hone_icons.dart")

# 4. Update pubspec.yaml with all 7 fonts
font_entries = []
for s in all_styles:
    font_name = f"HoneIcons{s}"
    font_entries.append(f"    - family: {font_name}\n      fonts:\n        - asset: fonts/{font_name}.ttf")

fonts_yaml = "\n".join(font_entries)
pubspec_content = f"""name: hone_icons
description: "Hone design system icons package for Flutter applications."
version: 0.0.1
homepage: https://lersha.com

environment:
  sdk: ^3.12.1
  flutter: ">=1.17.0"

dependencies:
  flutter:
    sdk: flutter

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^6.0.0

flutter:
  fonts:
{fonts_yaml}
"""
(BASE_DIR / "pubspec.yaml").write_text(pubspec_content, encoding='utf-8')
print("Updated pubspec.yaml with all 7 fonts!")
