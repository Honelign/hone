# Rule: Flutter Clean Architecture & BLoC Best Coding Practices

This rule enforces industry-standard, senior-level coding guidelines for Clean Architecture and BLoC state management in Flutter. Follow these rules to ensure the codebase remains clean, maintainable, testable, and highly optimized.

---

## 📂 1. Feature-First Folder Structure
Each feature must separate concerns into three clean layers: `data`, `domain`, and `presentation`.

```text
lib/features/<feature_name>/
├── data/
│   ├── datasources/        # Remote (API Client) & Local (DB Client) sources
│   ├── models/             # API response Models, API request DTOs, local DB models
│   └── repositories/       # Implementation of domain repository contracts
├── domain/
│   ├── entities/           # Pure Dart business objects (No serialization/DB annotations)
│   ├── repositories/       # Abstract repository interfaces
│   └── usecases/           # Single-purpose business actions (e.g. GetItemUseCase)
└── presentation/
    ├── bloc/               # Bloc, Event, and State files
    ├── pages/              # Main screen widgets (Scaffolds, Page wrappers)
    └── widgets/            # Reusable UI components
```

---

## 🏷️ 2. Explicit Filename Suffixes
To prevent namespace collisions and maintain absolute readability, all files must use descriptive naming suffixes:

* **Domain Entity:** `<name>_entity.dart` (e.g., `booking_entity.dart` declaring `class BookingEntity`)
* **API Response Model:** `<name>_model.dart` (e.g., `booking_model.dart` declaring `class BookingModel` representing the incoming API response payload)
* **API Request DTO:** `<name>_dto.dart` (e.g., `create_booking_dto.dart` declaring `class CreateBookingDto` representing the outgoing API request payload)
* **Local Database Model:** `<name>_db_model.dart` (e.g., `booking_db_model.dart` declaring `class BookingDbModel` with ORM annotations representing the database table)
* **Repository Interface:** `<name>_repository.dart` (e.g., `booking_repository.dart`)
* **Repository Implementation:** `<name>_repository_impl.dart` (e.g., `booking_repository_impl.dart`)

---

## 🔄 3. Strict Data Boundary Separation and Mapping
Data layer artifacts (Models, DTOs, DB Models) must never leak into the presentation or domain layers.

1. **Entities (`*_entity.dart`):** Must be pure Dart classes extending `Equatable`. No dependency on ORMs (like ObjectBox) or JSON serializers (no `fromJson`/`toJson`).
2. **API Response Models (`*_model.dart`):** Parse network JSON response payloads (`fromJson`).
3. **API Request DTOs (`*_dto.dart`):** Serialize request payloads to JSON (`toJson`) before sending to the API.
4. **Database Models (`*_db_model.dart`):** Contain local database annotations (e.g., `@Entity()`, `@Id()`, `@Unique()`).
5. **Data Mapping:** Models and DB Models must implement mapping methods (`toEntity()` and `fromEntity()`) to translate data to and from domain entities.
6. **Mapping Location:** Mapping must happen inside the **Data Layer** (specifically inside the repository implementations). The Domain and Presentation layers must only consume and operate on `Entity` objects.

---

## 📦 4. Local Database (ObjectBox) Mapping Standards
To prevent duplicate records and maintain database integrity when mapping Domain Entities to ObjectBox Database Models, follow these rules:

1. **Auto-Increment Key:** The local DB Model must declare `int obId = 0;` annotated with `@Id()` for ObjectBox's internal identification.
2. **UUID Mapping & Conflict Strategy:** The remote UUID String from the Domain Entity must be saved into a dedicated index field (e.g., `String remoteId`) and annotated with `@Unique(onConflict: ConflictStrategy.replace)`.
3. **Upsert Safety:** When mapping an entity to a DB Model, you must either:
   - **Method A (Upsert by index):** Set `obId = 0` and rely on the `@Unique(onConflict: ConflictStrategy.replace)` annotation on the remote UUID field to replace the row.
   - **Method B (Query lookup):** Query the local Box to retrieve the existing `obId` matching the remote UUID before calling `fromEntity(entity, obId: existingId)`, and pass it to perform an inline update.

```dart
// Example of compliant database model with conflict strategy
@Entity()
class BookingDbModel {
  @Id()
  int obId = 0;

  @Unique(onConflict: ConflictStrategy.replace)
  final String id; // Matches remote UUID

  final double amount;

  BookingDbModel({this.obId = 0, required this.id, required this.amount});

  static BookingDbModel fromEntity(BookingEntity entity, {int obId = 0}) =>
      BookingDbModel(
        obId: obId,
        id: entity.id,
        amount: entity.amount,
      );
}
```

---

## 🧠 5. BLoC Architecture: Events, States, and Pattern Matching

### State & Event Structure
1. Use **Dart 3 `sealed class`** patterns for all states and events to enforce compile-time type safety.
2. Events must be named using **past tense** reflecting user interaction or lifecycle events (e.g., `BookingFetchRequested`, `BookingCancelPressed`).
3. States must represent mutually exclusive layout conditions (`Initial`, `LoadInProgress`, `LoadSuccess`, `LoadFailure`).

### Presentation Pattern Matching
1. **Rule:** Use Dart 3 `switch` expression pattern matching inside your `BlocBuilder` to handle states. This guarantees exhaustiveness and prevents unhandled runtime layouts.

---

## 🧱 6. Widget Cleanliness and Performance Optimization

### Class-Based Widgets Only
> [IMPORTANT]
> **NEVER use helper functions that return widgets (e.g. `Widget _buildHeader()`).**
> 
> You must extract code into separate `const StatelessWidget` classes. This permits Flutter to optimize and cache layout subtrees, prevents parent rebuild leaks, and ensures correct `BuildContext` scopes.

### Strict File Constraints
* **Line length:** Maximum of **80 characters** per line.
* **File size:** Maximum of **150–200 lines** per file. Beyond this, widgets must be extracted into their own files under `widgets/`.

### Rebuild and Side-Effect Isolation
1. **`BlocBuilder`:** Strictly for rendering widgets. Use `buildWhen` to optimize and prevent unnecessary rebuilds from transient states.
2. **`BlocListener`:** Strictly for side-effects (e.g., navigation, dialogs, SnackBars). Never place routing or alert actions inside the builder function.
3. **Data Passing:** Parent widgets must only pass primitive parameters or Domain Entities to child widgets. Do **not** pass BLoC or State objects to children. Child widgets must remain pure UI templates.

---

## 🗺️ 7. Centralized Navigation (No Hardcoded Routes)
* **Rule:** Never use hardcoded route strings (e.g., `context.push('/payment')`) directly inside widgets or BLoC listeners.
* **Implementation:** Always use a centralized route class (e.g., `AppRoutes.bookingDetails`) or type-safe routes. This provides refactor safety and a single source of truth for routing.
* **Navigation Trigger:** All route pushes/pops must reside inside a `BlocListener`'s or `BlocConsumer`'s `listener` callback.

---

## 🛡️ 8. Isolated Input Validation
* **Rule:** Do not write regex patterns or validation logic directly inside widgets.
* **Implementation:** Encapsulate validation logic inside pure helper classes (e.g. `Validators.validateEmail`) in the core utilities directory (`core/utils/`). 
* **Tear-offs:** Pass validator methods directly as tear-offs to inputs (e.g. `validator: Validators.validateEmail`). This ensures that the validation rules are isolated and easily unit-tested.

---

## 🔢 9. Enhanced Enums for String Mapping
* **Rule:** Do not write custom `switch` blocks or `if-else` chains in repository or data source layers to translate backend status/type strings into enums.
* **Implementation:** Use Dart **Enhanced Enums** with a constructor field (e.g., `final String apiKey`) and a static `parse(String?)` helper.
* **Safe Fallback:** Always define a fallback option (e.g., `unknown`) inside the enum to handle unrecognized strings gracefully.
* **JSON Serialization:** Use custom `JsonConverter` classes to automatically serialize/deserialize the enum inside your model or DTO files.

---

## ❓ 10. Ask, Don't Assume (Clarification Rule)
* **Rule:** If a model request body, API payload structure, or enum value mapping is unclear or lacks documentation, developers/AI agents **must not assume** or write temporary bypass code. You must ask the user for clarification and proceed only with verified details.

---

## 🏗️ 11. SOLID & DRY Principles Enforcement (Zero Code Smells)
To eliminate spaghetti structures and duplication code smells, follow these rules:

1. **SRP (Single Responsibility):** Separate classes strictly by action. UseCases must contain only one public `call()` method executing a single transaction.
2. **DIP (Dependency Inversion):** High-level modules (UseCases) must depend on abstraction repository interfaces. Concrete repository implementations must reside in the data layer. Resolve them strictly via constructor-injected Dependency Injection (`get_it` & `injectable`).
3. **DRY (Don't Repeat Yourself):** 
   - Extract common UI blocks (buttons, standard dialogs, loading panels) into `features/shared/` or `core/presentation/widgets/`.
   - Keep formatting converters, string utils, and device feature helpers in `core/utils/`.

---

## 🔑 12. Mandatory Named Parameters Everywhere (CamelCase)
* **Rule:** All functions, methods, and constructors (including domain use cases, data source queries, repository operations, BLoC event factory constructors, UI widget constructors, utility methods, and enum parser methods) must strictly use **named parameters** for all parameters.
* **Prohibition:** Positional parameters are strictly prohibited. Never pass values positionally (e.g. `myFunc(value)`), as this is prone to type/order confusion errors. Every argument must be named (e.g. `myFunc(value: value)`).
* **Naming Standard:** Use `camelCase` for all named parameters (e.g., `{required String userId, String? categoryId}`) to maintain absolute consistency with Flutter framework standards.
* **Exceptions:** Standard framework override methods (e.g. standard widget `build(BuildContext context)`) and constructors of simple wrapper data types (like standard Equatable list props overrides) are allowed to preserve framework signatures.

---

## 📁 13. Dedicated BLoC Subdirectories
To prevent flat folder pollution and maintain structural clarity:
1. **Rule:** Presentation layer BLoCs (`/presentation/bloc/`) must be organized into dedicated subdirectories per BLoC (e.g., `/bloc/products/`, `/bloc/product_detail/`).
2. **Contents:** Each subdirectory must group the specific BLoC class, event, state, and generated files (`.freezed.dart`, etc.) together.
3. **Flat Directory Restriction:** A flat `bloc/` directory containing files for multiple distinct BLoCs is prohibited.

### Example Folder Structure:
```text
lib/features/inputs/products/presentation/bloc/
├── products/
│   ├── products_bloc.dart
│   ├── products_event.dart
│   ├── products_state.dart
│   ├── products_event.freezed.dart
│   └── products_state.freezed.dart
├── product_detail/
│   ├── product_detail_bloc.dart
│   └── ...
└── add_product/
    ├── add_product_bloc.dart
    └── ...
```

---

## 📄 14. One Class Per Presentation File
To ensure navigability, discoverability, and single-responsibility at the file level:

1. **Rule:** Every presentation file (`pages/`, `widgets/`) must declare **exactly one public or private class**. Multiple classes in a single file are strictly prohibited.
2. **Threshold:** Any private widget class (`_MyWidget`) that spans more than ~30 lines of build logic must be extracted into its own dedicated file in the feature's `widgets/` folder.
3. **Naming:** The extracted file's name must match the class name in snake_case (e.g., `class AddProductWizardScaffold` → `add_product_wizard_scaffold.dart`). Extracted widgets should be made **public** (no underscore prefix) since they now live in their own file.
4. **Location:**
   - Sub-widgets that are page-specific go in the same feature's `widgets/` folder.
   - Generic reusable widgets (used by 2+ features) go in `core/presentation/widgets/` or `features/shared/widgets/`.
5. **No barrel files:** Do not create `index.dart` barrel files — import each file with its full package path.

### ❌ Prohibited — multiple classes in one file:
```dart
// add_product_view.dart  ← BAD: 5 classes in one file
class AddProductView extends StatefulWidget { ... }
class _WizardScaffold extends StatelessWidget { ... }   // 120 lines
class _Step1Form extends StatelessWidget { ... }         // 180 lines
class _Step2Form extends StatelessWidget { ... }         // 90 lines
class _SuccessScaffold extends StatelessWidget { ... }   // 75 lines
```

### ✅ Correct — one class per file:
```text
lib/features/inputs/products/presentation/
├── pages/
│   └── add_product_view.dart        ← only AddProductView
└── widgets/
    ├── add_product_wizard_scaffold.dart
    ├── add_product_step1_form.dart
    ├── add_product_step2_form.dart
    └── add_product_success_scaffold.dart
```

---

## 🔒 15. No Dynamic Types — Always Be Explicit
To prevent runtime type errors and maintain full static analysis coverage:

1. **Rule:** `dynamic` is strictly prohibited as a type annotation for any parameter, return type, field, variable, or generic type argument.
2. **Always use the concrete type:** Use the actual model, entity, DTO, enum, or built-in Dart type that represents the data (e.g., `StoreProductEntity`, `List<CategoryModel>`, `String`, `int`).
3. **No implicit dynamics:** Never omit a type annotation where Dart would infer `dynamic` (e.g., untyped `List`, `Map`, raw `Future`).
4. **Router `extra`:** When passing data through GoRouter's `extra` field, cast to the concrete type immediately on the receiving page — do not leave it as `dynamic` or `Object?` beyond the cast site.
5. **JSON maps:** `Map<String, dynamic>` is the **only** accepted use of `dynamic` — it is required by Dart's JSON decoding API (`json.decode` returns `Map<String, dynamic>`). This exception applies nowhere else.

### ❌ Prohibited:
```dart
// Parameters
void process(dynamic data) { ... }
Future<dynamic> fetchProduct() { ... }

// Variables
dynamic result = await repository.get();
List items = [];                          // infers List<dynamic>
Map map = {};                             // infers Map<dynamic, dynamic>

// GoRouter extra left uncast
final product = extra;                    // extra is Object? / dynamic
```

### ✅ Correct:
```dart
// Parameters — use the entity/model
void process(StoreProductEntity product) { ... }
Future<ProductEntity> fetchProduct() { ... }

// Variables — explicitly typed
StoreProductEntity result = await repository.get();
List<CategoryModel> items = [];
Map<String, String> map = {};

// GoRouter extra — cast immediately
final product = extra! as StoreProductEntity;

// JSON decoding — the only valid dynamic use
Map<String, dynamic> json = jsonDecode(response.body) as Map<String, dynamic>;
```

