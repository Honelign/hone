# Hone Icons Workflow & Context Rule

This document records the full architecture, context, data pipeline, and implementation instructions for the **`hone_icons`** Flutter icon font package in this monorepo.

---

## 1. Project Context & Objectives

- **Monorepo Layout**:
  - `hone_icons/`: Central shared Flutter icon package containing all design system icons.
  - `lersha_base_mobile/`: Shared foundational mobile library.
  - `offtaker_app/`, `lersha_service_provider_app/`: Consumer Flutter mobile apps.
- **Design Source**: Figma library **NeatIcons (Copy)** (File Key: `yIkcB8h7zlUXJcZQUK2PeJ`).
- **Icon Scope**: ~2,897 unique icons across ~40 categories, each available in 7 distinct styles:
  1. `Outline`
  2. `Linear`
  3. `Bold`
  4. `Bulk`
  5. `Duotone`
  6. `TwoColor`
  7. `Gestalt`
- **Output Target**: TrueType font files (`.ttf`) + Flutter `IconData` classes with type-safe autocompletion and zero external runtime dependencies.

---

## 2. The Figma Export Naming Challenge & Solution

### The Challenge
In Figma, each icon is a `COMPONENT_SET` (e.g., `prompt`, `AI-brain-1`). Inside it, the 7 style variants are named `style=outline`, `style=bold`, etc.
When batch-exporting all layers from Figma, Figma names files by their own layer name. Because hundreds of layers share the same name (`style=outline`), Figma outputs:
`style=outline.svg`, `style=outline-1.svg`, `style=outline-2.svg`, ..., `style=outline-N.svg`.
This strips the parent icon name from the filename.

### The Solution
1. In Figma, layers are exported in the **exact sequential order** of the layer tree.
2. We extracted the complete metadata catalog of all 39+ pages and 2,897 icons directly via the Figma API:
   **`hone_icons/scripts/icons_catalog.json`**.
3. Therefore, within any category folder:
   - Index 0 (`style=outline.svg`) $\rightarrow$ Icon 0 in that category catalog
   - Index 1 (`style=outline-1.svg`) $\rightarrow$ Icon 1 in that category catalog
   - Index $K$ (`style=outline-K.svg`) $\rightarrow$ Icon $K$ in that category catalog
4. **Golden Export Rule**: As long as each Figma page/category is exported into its own folder (e.g., `icons_svg/arrows/`, `icons_svg/AI/`, etc.), mapping is 100% deterministic and automatic.

---

## 3. Directory Structure

```
hone/
├── .agents/
│   └── rules/
│       ├── hone_icons_workflow.md            <-- This rule file
│       └── flutter_clean_bloc_architecture.md
├── hone_icons/
│   ├── pubspec.yaml                          <-- Flutter package manifest & font declarations
│   ├── README.md                             <-- Developer usage guide
│   ├── icons_svg/                            <-- Raw SVGs exported from Figma (categorized)
│   │   ├── AI/
│   │   ├── arrows/
│   │   ├── essentials/
│   │   └── ... (42 category folders)
│   ├── icons_clean/                          <-- Mapped, clean SVGs organized by style
│   │   ├── Bold/
│   │   ├── Bulk/
│   │   ├── Duotone/
│   │   ├── Gestalt/
│   │   ├── Linear/
│   │   ├── Outline/
│   │   └── TwoColor/
│   ├── fonts/                                <-- Compiled TrueType font files (.ttf)
│   │   ├── HoneIconsBold.ttf
│   │   ├── HoneIconsBulk.ttf
│   │   ├── HoneIconsDuotone.ttf
│   │   ├── HoneIconsGestalt.ttf
│   │   ├── HoneIconsLinear.ttf
│   │   ├── HoneIconsOutline.ttf
│   │   └── HoneIconsTwoColor.ttf
│   ├── lib/
│   │   ├── hone_icons.dart                   <-- Main export barrel file + default typedef
│   │   └── src/
│   │       ├── hone_icons_bold.dart
│   │       ├── hone_icons_bulk.dart
│   │       ├── hone_icons_duotone.dart
│   │       ├── hone_icons_gestalt.dart
│   │       ├── hone_icons_linear.dart
│   │       ├── hone_icons_outline.dart
│   │       └── hone_icons_twocolor.dart
│   └── scripts/
│       ├── icons_catalog.json                <-- Complete Figma node & sequence metadata
│       ├── map_all_categories.py             <-- Maps raw SVGs into icons_clean/ by style
│       └── build_package.py                  <-- Compiles TTFs with svgtofont & generates Dart
```

---

## 4. Automation Scripts & Pipeline

### Step 1: Mapping Raw Exports to Clean SVGs
Script: **`hone_icons/scripts/map_all_categories.py`**
- Reads each category folder inside `hone_icons/icons_svg/`.
- Extracts `style=<style>-<index>.svg` files.
- Matches `index` to the icon name in `icons_catalog.json` for that category.
- Normalizes names to `lowerCamelCase` (e.g. `aiBrainTop`, `arrowUpRight`).
- Differentiates duplicate names (e.g. `humanoidRobot4_2`).
- Copies clean SVGs into `hone_icons/icons_clean/<Style>/<cleanIconId>.svg`.

Run:
```bash
python hone_icons/scripts/map_all_categories.py
```

### Step 2: Compiling Fonts & Generating Flutter Code
Script: **`hone_icons/scripts/build_package.py`**
- Uses `npx svgtofont` to compile `.svg` files in `icons_clean/<Style>` into `fonts/HoneIcons<Style>.ttf`.
- Extracts Unicode hex code points from generated CSS (`\ea01`, `\ea02`, etc.).
- Generates type-safe Dart classes:
  - `class HoneIconsOutline { static const IconData name = IconData(0x..., fontFamily: 'HoneIconsOutline', fontPackage: 'hone_icons'); }`
  - Similarly for `HoneIconsBold`, `HoneIconsLinear`, `HoneIconsBulk`, `HoneIconsDuotone`, `HoneIconsTwoColor`, `HoneIconsGestalt`.
- Generates `lib/hone_icons.dart` with `typedef HoneIcons = HoneIconsOutline;`.
- Updates `hone_icons/pubspec.yaml` with all font asset declarations.

Run:
```bash
python hone_icons/scripts/build_package.py
```

---

## 5. Status of the 5 Special Folders

During initial export, 5 folders contained inner vector slices or full component set previews rather than individual variant component layers:
1. `Banknote, Credit Card` (Exported full 400x64 component set frames)
2. `Earphone,headphone` (Exported full 400x64 component set frames)
3. `brand, company` (Exported inner `line`, `filled`, `merged` sub-vectors)
4. `call,phone` (Exported inner `line`, `shaped`, `merged` sub-vectors)
5. `document,content` (Exported inner `line`, `shaped`, `merged` sub-vectors)

### How to re-export these 5 pages in Figma (if needed):
1. In Figma, navigate to that page.
2. Select the master component sets (the second frame on `call,phone` / `document,content`).
3. Press **`Enter`** to select the child variant components (`style=outline`, `style=bold`, etc.).
4. Under **Export**, click **+**, select **SVG**, and export into their respective folder in `hone_icons/icons_svg/`.
5. Re-run `python hone_icons/scripts/map_all_categories.py` and `python hone_icons/scripts/build_package.py`.

---

## 6. How to Consume `hone_icons` in Apps

### 1. In App's `pubspec.yaml`
Add local path dependency:
```yaml
dependencies:
  hone_icons:
    path: ../hone_icons
```
*(Or export it through `lersha_base_mobile` so all apps automatically inherit it).*

### 2. In Dart Code
```dart
import 'package:flutter/material.dart';
import 'package:hone_icons/hone_icons.dart';

// Default style (Outline):
Icon(HoneIcons.aiBrainTop, size: 24, color: Colors.blue);
Icon(HoneIcons.arrowUpRight, size: 24);

// Explicit styles:
Icon(HoneIconsBold.aiBrainTop, size: 24, color: Colors.indigo);
Icon(HoneIconsLinear.aiBrainTop, size: 24);
Icon(HoneIconsBulk.aiBrainTop, size: 24);
Icon(HoneIconsDuotone.aiBrainTop, size: 24);
Icon(HoneIconsTwoColor.aiBrainTop, size: 24);
Icon(HoneIconsGestalt.aiBrainTop, size: 24);
```

---

## 7. Fast Cheat Sheet

```bash
# 1. Map raw SVG exports to clean names
python hone_icons/scripts/map_all_categories.py

# 2. Compile TrueType fonts and generate Flutter Dart code
python hone_icons/scripts/build_package.py

# 3. Verify Flutter package
cd hone_icons
flutter pub get
dart analyze
```

---

## 8. Icon Finder Web App & Deployment

The monorepo includes an interactive Flutter Web application (`icon_finder/`) to explore, search, and copy code snippets for all 2,750+ icons.

- **Live URL**: https://flutter-ai-playground-30390.web.app
- **Firebase Project**: `flutter-ai-playground-30390`
- **Rebuilding & Redeploying**:
  ```bash
  # Regenerate registry if new icons are added
  python hone_icons/scripts/generate_icon_registry.py

  # Build web app
  cd icon_finder
  flutter build web --release

  # Deploy to Firebase Hosting
  firebase deploy --only hosting
  ```

