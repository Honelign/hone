import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:hone_icons/hone_icons.dart';
import 'icon_registry.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const HoneIconFinderApp());
}

class HoneIconFinderApp extends StatefulWidget {
  const HoneIconFinderApp({super.key});

  @override
  State<HoneIconFinderApp> createState() => _HoneIconFinderAppState();
}

class _HoneIconFinderAppState extends State<HoneIconFinderApp> {
  ThemeMode _themeMode = ThemeMode.dark;

  void _toggleTheme() {
    setState(() {
      _themeMode = _themeMode == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
    });
  }

  @override
  Widget build(BuildContext context) {
    const primaryColor = Color(0xFF10B981); // Emerald green (Lersha theme)

    final darkTheme = ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryColor,
        brightness: Brightness.dark,
        surface: const Color(0xFF0F172A),
      ),
      scaffoldBackgroundColor: const Color(0xFF090D16),
      fontFamily: 'Inter',
    );

    final lightTheme = ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryColor,
        brightness: Brightness.light,
        surface: Colors.white,
      ),
      scaffoldBackgroundColor: const Color(0xFFF8FAFC),
      fontFamily: 'Inter',
    );

    return MaterialApp(
      title: 'Hone Icons - Icon Finder',
      debugShowCheckedModeBanner: false,
      theme: lightTheme,
      darkTheme: darkTheme,
      themeMode: _themeMode,
      home: IconFinderScreen(
        onToggleTheme: _toggleTheme,
        isDark: _themeMode == ThemeMode.dark,
      ),
    );
  }
}

class IconFinderScreen extends StatefulWidget {
  final VoidCallback onToggleTheme;
  final bool isDark;

  const IconFinderScreen({
    super.key,
    required this.onToggleTheme,
    required this.isDark,
  });

  @override
  State<IconFinderScreen> createState() => _IconFinderScreenState();
}

class _IconFinderScreenState extends State<IconFinderScreen> {
  final TextEditingController _searchController = TextEditingController();
  final FocusNode _searchFocusNode = FocusNode();

  HoneIconStyle _selectedStyle = HoneIconStyle.outline;
  String _selectedCategory = 'All';
  double _iconSize = 32.0;
  Color _iconColor = const Color(0xFF10B981);

  final List<Color> _presetColors = const [
    Color(0xFF10B981), // Emerald
    Color(0xFF3B82F6), // Blue
    Color(0xFF8B5CF6), // Purple
    Color(0xFFEC4899), // Pink
    Color(0xFFF59E0B), // Amber
    Color(0xFFEF4444), // Red
    Colors.white,
    Colors.black87,
  ];

  List<IconItem> _filteredIcons = [];

  @override
  void initState() {
    super.initState();
    _filteredIcons = kAllIcons;
    _searchController.addListener(_onFilterChanged);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _searchFocusNode.dispose();
    super.dispose();
  }

  void _onFilterChanged() {
    final query = _searchController.text.trim().toLowerCase();
    setState(() {
      _filteredIcons = kAllIcons.where((item) {
        final matchesCategory =
            _selectedCategory == 'All' || item.category == _selectedCategory;
        if (!matchesCategory) return false;

        if (query.isEmpty) return true;
        return item.id.toLowerCase().contains(query) ||
            item.name.toLowerCase().contains(query) ||
            item.category.toLowerCase().contains(query);
      }).toList();
    });
  }

  void _copyToClipboard(String text, String label) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 20),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'Copied: $label',
                style: const TextStyle(fontWeight: FontWeight.w600),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 2),
        width: 400,
        backgroundColor: const Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }

  String _getClassName(HoneIconStyle style) {
    switch (style) {
      case HoneIconStyle.outline:
        return 'HoneIconsOutline';
      case HoneIconStyle.linear:
        return 'HoneIconsLinear';
      case HoneIconStyle.bold:
        return 'HoneIconsBold';
      case HoneIconStyle.bulk:
        return 'HoneIconsBulk';
      case HoneIconStyle.duotone:
        return 'HoneIconsDuotone';
      case HoneIconStyle.twoColor:
        return 'HoneIconsTwoColor';
      case HoneIconStyle.gestalt:
        return 'HoneIconsGestalt';
    }
  }

  void _showIconDetailModal(IconItem item) {
    showDialog(
      context: context,
      builder: (ctx) {
        final isDark = Theme.of(ctx).brightness == Brightness.dark;
        return Dialog(
          backgroundColor: isDark ? const Color(0xFF111827) : Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 680),
            child: Padding(
              padding: const EdgeInsets.all(28.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title Row
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: _iconColor.withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Icon(
                          item.getIcon(_selectedStyle),
                          size: 40,
                          color: _iconColor,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item.name,
                              style: const TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Category: ${item.category} • ID: ${item.id}',
                              style: TextStyle(
                                fontSize: 13,
                                color: isDark ? Colors.white54 : Colors.black54,
                              ),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        onPressed: () => Navigator.of(ctx).pop(),
                        icon: const Icon(Icons.close),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  const Divider(),
                  const SizedBox(height: 16),

                  // Styles Row
                  const Text(
                    'All Available Styles',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: HoneIconStyle.values.map((s) {
                      final hasThisStyle = item.hasStyle(s);
                      final iconData = item.styles[s];
                      final isCurrent = _selectedStyle == s;

                      return Tooltip(
                        message: hasThisStyle ? s.label : '${s.label} (Not available)',
                        child: InkWell(
                          borderRadius: BorderRadius.circular(12),
                          onTap: hasThisStyle
                              ? () {
                                  setState(() => _selectedStyle = s);
                                  Navigator.of(ctx).pop();
                                }
                              : null,
                          child: Container(
                            width: 80,
                            padding: const EdgeInsets.symmetric(
                                vertical: 12, horizontal: 8),
                            decoration: BoxDecoration(
                              color: isCurrent
                                  ? const Color(0xFF10B981).withValues(alpha: 0.15)
                                  : (isDark
                                      ? const Color(0xFF1F2937)
                                      : const Color(0xFFF1F5F9)),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: isCurrent
                                    ? const Color(0xFF10B981)
                                    : Colors.transparent,
                                width: 1.5,
                              ),
                            ),
                            child: Column(
                              children: [
                                if (hasThisStyle && iconData != null)
                                  Icon(iconData, size: 28, color: _iconColor)
                                else
                                  const Icon(Icons.remove,
                                      size: 28, color: Colors.grey),
                                const SizedBox(height: 6),
                                Text(
                                  s.label,
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: isCurrent
                                        ? FontWeight.bold
                                        : FontWeight.normal,
                                    color: hasThisStyle
                                        ? (isDark ? Colors.white : Colors.black87)
                                        : Colors.grey,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ),

                  const SizedBox(height: 24),
                  const Text(
                    'Copy Snippet',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                  const SizedBox(height: 10),

                  // Snippet 1: Icon widget
                  _buildSnippetRow(
                    isDark: isDark,
                    title: 'Flutter Widget',
                    code: 'Icon(${_getClassName(_selectedStyle)}.${item.id}, size: ${_iconSize.toInt()}, color: Colors.green)',
                    onCopy: () => _copyToClipboard(
                      'Icon(${_getClassName(_selectedStyle)}.${item.id})',
                      'Icon widget',
                    ),
                  ),
                  const SizedBox(height: 8),

                  // Snippet 2: IconData identifier
                  _buildSnippetRow(
                    isDark: isDark,
                    title: 'Identifier',
                    code: '${_getClassName(_selectedStyle)}.${item.id}',
                    onCopy: () => _copyToClipboard(
                      '${_getClassName(_selectedStyle)}.${item.id}',
                      '${_getClassName(_selectedStyle)}.${item.id}',
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildSnippetRow({
    required bool isDark,
    required String title,
    required String code,
    required VoidCallback onCopy,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : const Color(0xFFF1F5F9),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              code,
              style: TextStyle(
                fontFamily: 'monospace',
                fontSize: 12.5,
                color: isDark ? const Color(0xFF38BDF8) : const Color(0xFF0369A1),
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            tooltip: 'Copy $title',
            icon: const Icon(Icons.copy, size: 18),
            onPressed: onCopy,
          ),
        ],
      ),
    );
  }

  void _showDocsModal() {
    showDialog(
      context: context,
      builder: (ctx) {
        final isDark = Theme.of(ctx).brightness == Brightness.dark;
        return Dialog(
          backgroundColor: isDark ? const Color(0xFF111827) : Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 600),
            child: Padding(
              padding: const EdgeInsets.all(28.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Using Hone Icons in Flutter',
                        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      IconButton(
                        onPressed: () => Navigator.of(ctx).pop(),
                        icon: const Icon(Icons.close),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    '1. Add to pubspec.yaml',
                    style: TextStyle(fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: isDark ? const Color(0xFF1E293B) : const Color(0xFFF1F5F9),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const SelectableText(
                      'dependencies:\n  hone_icons:\n    git:\n      url: https://github.com/Honelign/hone.git\n      path: hone_icons\n      ref: main',
                      style: TextStyle(fontFamily: 'monospace', fontSize: 12),
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    '2. Import and Use',
                    style: TextStyle(fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: isDark ? const Color(0xFF1E293B) : const Color(0xFFF1F5F9),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const SelectableText(
                      "import 'package:hone_icons/hone_icons.dart';\n\n// Use any style class:\nIcon(HoneIconsOutline.aiSparkle)\nIcon(HoneIconsBold.home2)\nIcon(HoneIconsDuotone.user)",
                      style: TextStyle(fontFamily: 'monospace', fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final surfaceColor = isDark ? const Color(0xFF111827) : Colors.white;
    final borderColor = isDark ? const Color(0xFF1F2937) : const Color(0xFFE2E8F0);

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // TOP NAV / HEADER BAR
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              decoration: BoxDecoration(
                color: surfaceColor,
                border: Border(bottom: BorderSide(color: borderColor)),
              ),
              child: Row(
                children: [
                  // App Branding
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: const Color(0xFF10B981).withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      HoneIconsOutline.category,
                      color: Color(0xFF10B981),
                      size: 26,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Text(
                            'Hone Icons',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              letterSpacing: -0.5,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: const Color(0xFF10B981).withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: const Text(
                              'v0.0.1',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF10B981),
                              ),
                            ),
                          ),
                        ],
                      ),
                      Text(
                        '2,750+ icons across 7 styles & 36 categories',
                        style: TextStyle(
                          fontSize: 12,
                          color: isDark ? Colors.white60 : Colors.black54,
                        ),
                      ),
                    ],
                  ),
                  const Spacer(),

                  // Quick Action Buttons
                  OutlinedButton.icon(
                    onPressed: _showDocsModal,
                    icon: const Icon(Icons.code, size: 16),
                    label: const Text('Integration Guide'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  IconButton(
                    tooltip: widget.isDark ? 'Switch to Light' : 'Switch to Dark',
                    onPressed: widget.onToggleTheme,
                    icon: Icon(
                      widget.isDark ? Icons.light_mode : Icons.dark_mode,
                    ),
                  ),
                ],
              ),
            ),

            // SEARCH & FILTER TOOLBAR
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF0F172A) : const Color(0xFFF8FAFC),
                border: Border(bottom: BorderSide(color: borderColor)),
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      // Search input
                      Expanded(
                        flex: 3,
                        child: TextField(
                          controller: _searchController,
                          focusNode: _searchFocusNode,
                          decoration: InputDecoration(
                            hintText: 'Search 2,750 icons by name, ID or category...',
                            hintStyle: TextStyle(
                              color: isDark ? Colors.white38 : Colors.black38,
                              fontSize: 14,
                            ),
                            prefixIcon: const Icon(Icons.search, size: 20),
                            suffixIcon: _searchController.text.isNotEmpty
                                ? IconButton(
                                    icon: const Icon(Icons.clear, size: 18),
                                    onPressed: () => _searchController.clear(),
                                  )
                                : null,
                            filled: true,
                            fillColor: surfaceColor,
                            contentPadding: const EdgeInsets.symmetric(
                                horizontal: 16, vertical: 12),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide(color: borderColor),
                            ),
                            enabledBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide(color: borderColor),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: const BorderSide(
                                color: Color(0xFF10B981),
                                width: 2,
                              ),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),

                      // Category Dropdown
                      Expanded(
                        flex: 2,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12),
                          decoration: BoxDecoration(
                            color: surfaceColor,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: borderColor),
                          ),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<String>(
                              isExpanded: true,
                              value: _selectedCategory,
                              icon: const Icon(Icons.keyboard_arrow_down),
                              items: ['All', ...kAllCategories].map((cat) {
                                return DropdownMenuItem(
                                  value: cat,
                                  child: Text(
                                    cat == 'All' ? 'All Categories (36)' : cat,
                                    style: const TextStyle(fontSize: 13.5),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                );
                              }).toList(),
                              onChanged: (val) {
                                if (val != null) {
                                  setState(() => _selectedCategory = val);
                                  _onFilterChanged();
                                }
                              },
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Style Selector Chips & Controls Bar
                  Row(
                    children: [
                      // Style tabs
                      Expanded(
                        child: SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          child: Row(
                            children: HoneIconStyle.values.map((style) {
                              final isSelected = _selectedStyle == style;
                              return Padding(
                                padding: const EdgeInsets.only(right: 8),
                                child: ChoiceChip(
                                  label: Text(style.label),
                                  selected: isSelected,
                                  selectedColor:
                                      const Color(0xFF10B981).withValues(alpha: 0.2),
                                  side: BorderSide(
                                    color: isSelected
                                        ? const Color(0xFF10B981)
                                        : borderColor,
                                  ),
                                  labelStyle: TextStyle(
                                    fontSize: 12.5,
                                    fontWeight: isSelected
                                        ? FontWeight.bold
                                        : FontWeight.normal,
                                    color: isSelected
                                        ? const Color(0xFF10B981)
                                        : (isDark ? Colors.white70 : Colors.black87),
                                  ),
                                  onSelected: (selected) {
                                    if (selected) {
                                      setState(() => _selectedStyle = style);
                                    }
                                  },
                                ),
                              );
                            }).toList(),
                          ),
                        ),
                      ),

                      // Size Slider
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.photo_size_select_small,
                              size: 16,
                              color: isDark ? Colors.white54 : Colors.black54),
                          SizedBox(
                            width: 100,
                            child: Slider(
                              value: _iconSize,
                              min: 20,
                              max: 56,
                              divisions: 9,
                              activeColor: const Color(0xFF10B981),
                              onChanged: (v) => setState(() => _iconSize = v),
                            ),
                          ),
                          Text(
                            '${_iconSize.toInt()}px',
                            style: TextStyle(
                              fontSize: 11,
                              color: isDark ? Colors.white54 : Colors.black54,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(width: 14),

                      // Color Presets
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: _presetColors.map((c) {
                          final isCurrent = _iconColor == c;
                          return GestureDetector(
                            onTap: () => setState(() => _iconColor = c),
                            child: Container(
                              margin: const EdgeInsets.symmetric(horizontal: 3),
                              width: 18,
                              height: 18,
                              decoration: BoxDecoration(
                                color: c,
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: isCurrent
                                      ? Colors.white
                                      : Colors.transparent,
                                  width: 2,
                                ),
                                boxShadow: isCurrent
                                    ? [
                                        const BoxShadow(
                                          color: Color(0xFF10B981),
                                          blurRadius: 4,
                                          spreadRadius: 1,
                                        )
                                      ]
                                    : null,
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // RESULTS COUNT BAR
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
              color: isDark ? const Color(0xFF090D16) : const Color(0xFFF1F5F9),
              child: Row(
                children: [
                  Text(
                    'Showing ${_filteredIcons.length} icons',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: isDark ? Colors.white60 : Colors.black54,
                    ),
                  ),
                  const Spacer(),
                  Text(
                    'Tip: Click any icon to view details & snippets, or hover to copy identifier',
                    style: TextStyle(
                      fontSize: 11.5,
                      fontStyle: FontStyle.italic,
                      color: isDark ? Colors.white38 : Colors.black38,
                    ),
                  ),
                ],
              ),
            ),

            // MAIN ICON GRID
            Expanded(
              child: _filteredIcons.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.search_off,
                            size: 64,
                            color: isDark ? Colors.white24 : Colors.black26,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'No icons match your search',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: isDark ? Colors.white60 : Colors.black54,
                            ),
                          ),
                          const SizedBox(height: 8),
                          TextButton(
                            onPressed: () {
                              _searchController.clear();
                              setState(() => _selectedCategory = 'All');
                              _onFilterChanged();
                            },
                            child: const Text('Reset Filters'),
                          ),
                        ],
                      ),
                    )
                  : LayoutBuilder(
                      builder: (context, constraints) {
                        // Responsive cross axis count
                        final width = constraints.maxWidth;
                        int crossAxisCount = 8;
                        if (width < 600) {
                          crossAxisCount = 3;
                        } else if (width < 900) {
                          crossAxisCount = 4;
                        } else if (width < 1200) {
                          crossAxisCount = 6;
                        }

                        return GridView.builder(
                          padding: const EdgeInsets.all(20),
                          gridDelegate:
                              SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: crossAxisCount,
                            crossAxisSpacing: 14,
                            mainAxisSpacing: 14,
                            childAspectRatio: 0.9,
                          ),
                          itemCount: _filteredIcons.length,
                          itemBuilder: (context, index) {
                            final item = _filteredIcons[index];
                            return _IconCard(
                              item: item,
                              style: _selectedStyle,
                              className: _getClassName(_selectedStyle),
                              size: _iconSize,
                              color: _iconColor,
                              onTap: () => _showIconDetailModal(item),
                              onCopy: (code, label) =>
                                  _copyToClipboard(code, label),
                            );
                          },
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

class _IconCard extends StatefulWidget {
  final IconItem item;
  final HoneIconStyle style;
  final String className;
  final double size;
  final Color color;
  final VoidCallback onTap;
  final void Function(String code, String label) onCopy;

  const _IconCard({
    required this.item,
    required this.style,
    required this.className,
    required this.size,
    required this.color,
    required this.onTap,
    required this.onCopy,
  });

  @override
  State<_IconCard> createState() => _IconCardState();
}

class _IconCardState extends State<_IconCard> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final hasStyle = widget.item.hasStyle(widget.style);
    final iconData = widget.item.getIcon(widget.style);

    final cardBg = isDark
        ? (_isHovered ? const Color(0xFF1E293B) : const Color(0xFF111827))
        : (_isHovered ? const Color(0xFFF1F5F9) : Colors.white);

    final cardBorder = _isHovered
        ? const Color(0xFF10B981)
        : (isDark ? const Color(0xFF1F2937) : const Color(0xFFE2E8F0));

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: InkWell(
        onTap: widget.onTap,
        borderRadius: BorderRadius.circular(14),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
          decoration: BoxDecoration(
            color: cardBg,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: cardBorder, width: _isHovered ? 1.5 : 1),
            boxShadow: _isHovered
                ? [
                    BoxShadow(
                      color: const Color(0xFF10B981).withValues(alpha: 0.15),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    )
                  ]
                : null,
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Icon
              Expanded(
                child: Center(
                  child: hasStyle
                      ? Icon(iconData, size: widget.size, color: widget.color)
                      : Opacity(
                          opacity: 0.35,
                          child: Icon(iconData,
                              size: widget.size, color: widget.color),
                        ),
                ),
              ),
              const SizedBox(height: 6),

              // Name
              Text(
                widget.item.name,
                style: const TextStyle(
                  fontSize: 11.5,
                  fontWeight: FontWeight.w600,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.center,
              ),

              const SizedBox(height: 4),

              // Hover quick copy or category
              if (_isHovered)
                InkWell(
                  onTap: () => widget.onCopy(
                    '${widget.className}.${widget.item.id}',
                    '${widget.className}.${widget.item.id}',
                  ),
                  child: Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: const Color(0xFF10B981).withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.copy, size: 10, color: Color(0xFF10B981)),
                        SizedBox(width: 4),
                        Text(
                          'Copy',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF10B981),
                          ),
                        ),
                      ],
                    ),
                  ),
                )
              else
                Text(
                  widget.item.id,
                  style: TextStyle(
                    fontSize: 10,
                    fontFamily: 'monospace',
                    color: isDark ? Colors.white38 : Colors.black38,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
            ],
          ),
        ),
      ),
    );
  }
}
