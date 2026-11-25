import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:icon_finder/icon_registry.dart';
import 'package:icon_finder/main.dart';

void main() {
  testWidgets('Icon Finder App smoke test', (WidgetTester tester) async {
    // The finder is a desktop web layout.
    tester.view.physicalSize = const Size(1440, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(const HoneIconFinderApp());
    expect(find.text('Hone Icons'), findsOneWidget);
    expect(
      find.text(
        '${kAllIcons.length} icons across 7 styles & '
        '${kAllCategories.length} categories',
      ),
      findsOneWidget,
    );
  });
}
