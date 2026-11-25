import 'package:flutter_test/flutter_test.dart';
import 'package:icon_finder/main.dart';

void main() {
  testWidgets('Icon Finder App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const HoneIconFinderApp());
    expect(find.text('Hone Icons'), findsOneWidget);
  });
}
