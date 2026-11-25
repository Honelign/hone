# Hone Icons (`hone_icons`)

Dedicated Flutter package for the **Hone Design System** icons, converted directly from the Figma **NeatIcons** library into high-performance, single-color TrueType (`.ttf`) icon fonts and type-safe Dart `IconData` classes.

---

## 📌 Project Overview & Full Context

* **Monorepo Layout**:
  * `hone_icons/`: Central Flutter icon package.
  * `lersha_base_mobile/`: Shared foundational library (can re-export `hone_icons`).
  * `offtaker_app/`, `lersha_service_provider_app/`: Consumer Flutter mobile apps.
* **Figma File**: `NeatIcons (Copy)` (File Key: `yIkcB8h7zlUXJcZQUK2PeJ`).
* **Design Structure**:
  * ~2,897 unique icons across ~40 categories.
  * Each icon is a Figma `COMPONENT_SET` with up to 7 distinct style variants:
    1. **Outline** (Default)
    2. **Linear**
    3. **Bold**
    4. **Bulk**
    5. **Duotone**
    6. **TwoColor**
    7. **Gestalt**
* **Output Assets**:
  * 7 compiled TrueType fonts in `fonts/` (`HoneIconsOutline.ttf`, `HoneIconsBold.ttf`, etc.).
  * 7 Dart classes in `lib/src/` (`HoneIconsOutline`, `HoneIconsBold`, etc.) + main barrel file `lib/hone_icons.dart`.

---

## 📂 Folder Structure

```
hone_icons/
├── pubspec.yaml                 # Flutter package manifest & font declarations
├── README.md                    # This complete documentation & context file
├── fonts/                       # Compiled TrueType (.ttf) font files
│   ├── HoneIconsOutline.ttf
│   ├── HoneIconsLinear.ttf
│   ├── HoneIconsBold.ttf
│   ├── HoneIconsBulk.ttf
│   ├── HoneIconsDuotone.ttf
│   ├── HoneIconsTwoColor.ttf
│   └── HoneIconsGestalt.ttf
├── lib/
│   ├── hone_icons.dart          # Barrel file & default `HoneIcons` typedef
│   └── src/
│       ├── hone_icons_outline.dart
│       ├── hone_icons_linear.dart
│       ├── hone_icons_bold.dart
│       ├── hone_icons_bulk.dart
│       ├── hone_icons_duotone.dart
│       ├── hone_icons_twocolor.dart
│       └── hone_icons_gestalt.dart
├── icons_svg/                   # Raw Figma exports organized by category
│   ├── AI/
│   ├── arrows/
│   ├── essentials/
│   └── ... (42 category folders)
├── icons_clean/                 # Mapped SVGs organized by style
│   ├── Outline/
│   ├── Linear/
│   ├── Bold/
│   ├── Bulk/
│   ├── Duotone/
│   ├── TwoColor/
│   └── Gestalt/
└── scripts/
    ├── icons_catalog.json       # Exact node order & names from Figma API
    ├── map_all_categories.py    # Matches Figma exports to catalog names
    ├── build_package.py         # Runs svgtofont, builds TTF fonts & Dart classes
    └── generate_icon_registry.py # Builds ../icon_finder/lib/icon_registry.dart
```

---

## 🧠 The Figma Naming Quirk & How It Is Solved

### The Problem
When you select sub-layer components in Figma and export them in bulk, Figma names each file after the variant property (e.g. `style=outline.svg`, `style=outline-1.svg`, `style=outline-2.svg`...). Because hundreds of layers share the same name, Figma appends sequential numbers (`-1`, `-2`, etc.), stripping the parent icon name.

### The Solution
Figma exports layers in the **exact sequential order** of the layer tree. We extracted the complete Figma metadata tree (`scripts/icons_catalog.json`).
Therefore, inside each category folder:
* `style=outline.svg` (Index 0) $\rightarrow$ Icon 0 in that category (`aiBrainTop`, etc.)
* `style=outline-1.svg` (Index 1) $\rightarrow$ Icon 1 in that category (`aiBrainTop2`, etc.)

**Exact layer names, not positions**: Figma numbers each *exact* layer name separately (`style=bold`, `style=bold-1`, ...). The Figma file contains misspelled variant layers (`style=filled`, `style=oultine`, `style=two ton`, `style=llinear`, ...), `style=Default` standing in for a missing style, and icons whose variants use another property name (`Property 1=bold`). Each of these shifts the numbering of the following icons for that style only. `map_all_categories.py` therefore walks the catalog in layer order and counts every exact layer name, so the k-th `style=bold` layer maps to `style=bold-k.svg`.

**Pages missing from the catalog are skipped**: `E-Commerce` is not in `icons_catalog.json`, so its exports are not mapped (guessing names from the inner layer files mislabelled them). Re-extract that page into the catalog, then re-run the mapping.

**Font-ready SVGs**: icon fonts fill every glyph with the nonzero rule and cannot draw strokes. `build_package.py` converts each SVG with [picosvg](https://github.com/googlefonts/picosvg) first (`fill-rule="evenodd"` holes and strokes become plain filled paths); without it, ~14% of Outline icons rendered as solid shapes and stroked icons disappeared. Figma `NaN` path segments are rewritten as lines to their end points (or dropped) during mapping.

**Unique ids across pages**: the same Figma name can appear on two pages (`logout` in Essential and Users) or twice on one page. Ids are unique across the whole package: a repeat gets `_2`, `_3`, ... in folder order, so no SVG overwrites another. `icons_clean/manifest.json` records each id's page and Figma name; the Icon Finder registry takes its categories from it.

**Ambiguous Figma names**: the Figma file reuses one name for different drawings (52 cases, e.g. `square-euro` for the yen, pound and euro squares), and a few variants are identical drawings under two names (e.g. Bold `squareEuro` and `circleEuro`), which share one glyph. Both come from the design file; rename the layers in Figma to fix them.

**Known limitation**: fonts are single-color, so the translucent layer of `Duotone` and `Bulk` icons renders fully opaque.

Requirements: Node (`npx svgtofont`) and `pip install picosvg`.

---

## 🛠️ Step-by-Step Implementation Guide

### 1. Map Raw Figma SVGs to Clean Names
Takes all categorized exports from `icons_svg/`, resolves the numbered filenames against `icons_catalog.json`, normalizes to `lowerCamelCase`, and outputs to `icons_clean/<Style>/`:
```bash
python scripts/map_all_categories.py
```

### 2. Compile Fonts & Generate Dart Code
Reads `icons_clean/`, executes `npx svgtofont` for each style, generates `.ttf` files in `fonts/`, parses Unicode hex codepoints, generates type-safe Dart classes in `lib/src/`, generates `lib/hone_icons.dart`, and updates `pubspec.yaml`:
```bash
python scripts/build_package.py
```

### 3. Update the Icon Finder
Regenerates `../icon_finder/lib/icon_registry.dart` from `lib/src/` and `icons_clean/manifest.json`:
```bash
python scripts/generate_icon_registry.py
```

### 4. Verify Package
```bash
flutter pub get
dart analyze
```

---

## 🚀 Usage in Flutter Apps

### 1. Dependency Setup
In your app's `pubspec.yaml` (e.g., in `lersha_base_mobile/pubspec.yaml` or `offtaker_app/pubspec.yaml`):

```yaml
dependencies:
  hone_icons:
    path: ../hone_icons
```

*(Tip: If you add `export 'package:hone_icons/hone_icons.dart';` inside `lersha_base_mobile`, all apps already depending on `lersha_base_mobile` will automatically have access without modifying their individual `pubspec.yaml`)*.

### 2. Dart Code Examples

```dart
import 'package:flutter/material.dart';
import 'package:hone_icons/hone_icons.dart';

// 1. Default Style (Outline):
Icon(
  HoneIcons.aiBrainTop,
  size: 24,
  color: Colors.blue,
);

Icon(
  HoneIcons.arrowUpRight,
  size: 20,
  color: Colors.black87,
);

// 2. Specific Style Variants:
Icon(HoneIconsBold.aiBrainTop, size: 24, color: Colors.indigo);
Icon(HoneIconsLinear.aiBrainTop, size: 24);
Icon(HoneIconsBulk.aiBrainTop, size: 24);
Icon(HoneIconsDuotone.aiBrainTop, size: 24);
Icon(HoneIconsTwoColor.aiBrainTop, size: 24);
Icon(HoneIconsGestalt.aiBrainTop, size: 24);
```

---

## ⚠️ Notes on the 5 Special Folders

During initial export, 5 folders contained inner vector slices or full component set previews rather than individual variant component layers:
1. `Banknote, Credit Card` (Exported full 400x64 component set frames)
2. `Earphone,headphone` (Exported full 400x64 component set frames)
3. `brand, company` (Exported inner vector slices: `line`, `filled`, `merged`)
4. `call,phone` (Exported inner vector slices: `line`, `shaped`, `merged`)
5. `document,content` (Exported inner vector slices: `line`, `shaped`, `merged`)

### To update these 5 categories:
1. In Figma, navigate to that page.
2. Select the master component sets (on `call,phone` & `document,content`, use the second frame).
3. Press **`Enter`** to select the child variant components (`style=outline`, `style=bold`, etc.).
4. Click **`+`** under **Export**, choose **SVG**, and export into their respective folder in `icons_svg/`.
5. Re-run:
   ```bash
   python scripts/map_all_categories.py
   python scripts/build_package.py
   ```
