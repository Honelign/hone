import os
import re
import shutil
import subprocess
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "icons_clean"
FONTS_DIR = BASE_DIR / "fonts"
LIB_DIR = BASE_DIR / "lib"
SRC_DIR = LIB_DIR / "src"

def build():
    print(f"Compiling icons from: {INPUT_DIR}")
    style_dirs = [d for d in INPUT_DIR.iterdir() if d.is_dir()]
    if not style_dirs:
        print("No style directories found in icons_clean!")
        return

    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    SRC_DIR.mkdir(parents=True, exist_ok=True)

    active_styles = []

    for sdir in sorted(style_dirs, key=lambda x: x.name):
        style = sdir.name
        svgs = list(sdir.glob("*.svg"))
        if not svgs:
            continue
        print(f"\nProcessing Style: {style} ({len(svgs)} icons)...")
        font_name = f"HoneIcons{style}"
        out_dir = BASE_DIR / ".staging" / f"out_{style}"
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = f"npx svgtofont --sources \"{sdir}\" --output \"{out_dir}\" --fontName {font_name}"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        ttf_file = out_dir / f"{font_name}.ttf"
        css_file = out_dir / f"{font_name}.css"

        if not ttf_file.exists():
            print(f"Warning: Failed to generate {font_name}.ttf")
            print(res.stderr)
            continue

        dest_ttf = FONTS_DIR / f"{font_name}.ttf"
        shutil.copy2(ttf_file, dest_ttf)
        print(f"  Generated TTF: {dest_ttf.relative_to(BASE_DIR)}")

        # Parse unicode mappings from CSS
        code_points = {}
        if css_file.exists():
            with open(css_file, 'r', encoding='utf-8') as cf:
                content = cf.read()
                matches = re.findall(rf'\.{font_name}-([a-zA-Z0-9_\-]+)::before\s*{{\s*content:\s*"\\([a-fA-F0-9]+)"', content)
                for id_name, hex_code in matches:
                    code_points[id_name] = hex_code

        # Generate Dart file for this style
        dart_file = SRC_DIR / f"hone_icons_{style.lower()}.dart"
        with open(dart_file, 'w', encoding='utf-8') as df:
            df.write("// GENERATED CODE - DO NOT MODIFY BY HAND\n")
            df.write("import 'package:flutter/widgets.dart';\n\n")
            df.write(f"/// Icons for Hone design system ({style} style).\n")
            df.write(f"class HoneIcons{style} {{\n")
            df.write(f"  HoneIcons{style}._();\n\n")
            df.write(f"  static const String _fontFamily = '{font_name}';\n")
            df.write("  static const String _fontPackage = 'hone_icons';\n\n")
            
            for sf in sorted(svgs, key=lambda x: x.stem):
                icon_id = sf.stem
                hex_code = code_points.get(icon_id)
                if hex_code:
                    df.write(f"  static const IconData {icon_id} = IconData(0x{hex_code}, fontFamily: _fontFamily, fontPackage: _fontPackage);\n\n")
            df.write("}\n")
        print(f"  Generated Dart: {dart_file.relative_to(BASE_DIR)}")
        active_styles.append(style)

    # Clean staging
    staging = BASE_DIR / ".staging"
    if staging.exists():
        shutil.rmtree(staging)

    # Generate main barrel file lib/hone_icons.dart
    barrel_file = LIB_DIR / "hone_icons.dart"
    default_style = 'Outline' if 'Outline' in active_styles else active_styles[0]
    with open(barrel_file, 'w', encoding='utf-8') as bf:
        bf.write("// Hone Icons Package for Flutter\n")
        bf.write("library hone_icons;\n\n")
        bf.write("export 'package:flutter/widgets.dart' show IconData;\n")
        for style in active_styles:
            bf.write(f"export 'src/hone_icons_{style.lower()}.dart';\n")
        
        bf.write(f"\nimport 'src/hone_icons_{default_style.lower()}.dart';\n")
        bf.write(f"\n/// Default alias for HoneIcons (points to HoneIcons{default_style})\n")
        bf.write(f"typedef HoneIcons = HoneIcons{default_style};\n")
    print(f"\nGenerated main barrel file: {barrel_file.relative_to(BASE_DIR)}")

    # Update pubspec.yaml fonts section
    pubspec_file = BASE_DIR / "pubspec.yaml"
    font_entries = []
    for s in active_styles:
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
    with open(pubspec_file, 'w', encoding='utf-8') as pf:
        pf.write(pubspec_content)
    print(f"Updated pubspec.yaml with {len(active_styles)} fonts.")
    print("\nDONE! All Hone Icons compiled successfully.")

if __name__ == '__main__':
    build()
