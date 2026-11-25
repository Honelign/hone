# Hone Monorepo

Welcome to the **Hone** repository — home to the **Hone Icons** Flutter design system package and the interactive **Icon Finder** web application.

---

## Projects in this Monorepo

| Project | Description | Link |
|---|---|---|
| **`hone_icons/`** | Core Flutter icon package containing 2,750+ icons across 7 styles as compiled TrueType fonts. | [hone_icons/README.md](hone_icons/README.md) |
| **`icon_finder/`** | Interactive Flutter Web application for browsing, filtering, and copying icon code snippets. | [Live Web App](https://flutter-ai-playground-30390.web.app) |

---

## Live Icon Finder Web App
Explore and search all 2,750+ icons interactively:  
🌐 **[https://flutter-ai-playground-30390.web.app](https://flutter-ai-playground-30390.web.app)**

---

## Using `hone_icons` in Any Flutter Project

### 1. Add Git Dependency to `pubspec.yaml`

```yaml
dependencies:
  flutter:
    sdk: flutter
  hone_icons:
    git:
      url: https://github.com/Honelign/hone.git
      path: hone_icons
      ref: main
```

Run:
```bash
flutter pub get
```

---

### 2. Usage in Dart Code

```dart
import 'package:flutter/material.dart';
import 'package:hone_icons/hone_icons.dart';

// Default style (Outline):
Icon(HoneIcons.aiBrainTop, size: 28, color: Colors.green);
Icon(HoneIcons.arrowUpRight, size: 24);

// Specific style classes:
Icon(HoneIconsOutline.aiSparkle, size: 24);
Icon(HoneIconsLinear.aiBrainTop, size: 24);
Icon(HoneIconsBold.home2, size: 24, color: Colors.blue);
Icon(HoneIconsBulk.setting2, size: 24);
Icon(HoneIconsDuotone.user, size: 24);
Icon(HoneIconsTwoColor.heart, size: 24);
Icon(HoneIconsGestalt.wallet3, size: 24);
```

---

### Available Styles
- **`HoneIcons` / `HoneIconsOutline`**: 2,748 icons
- **`HoneIconsLinear`**: 2,749 icons
- **`HoneIconsBold`**: 2,742 icons
- **`HoneIconsBulk`**: 2,735 icons
- **`HoneIconsDuotone`**: 2,745 icons
- **`HoneIconsTwoColor`**: 2,746 icons
- **`HoneIconsGestalt`**: 2,750 icons

Total unique icon designs: **2,750+** across **36 categories**.

---

## License
MIT License.
