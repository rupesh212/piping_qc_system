# Piping QA/QC Mobile App

Flutter mobile client for the Piping QA/QC system. Provides field inspection
capabilities including ISO document scanning, validation, and dashboard access.

## Prerequisites

| Tool | Minimum Version |
|------|----------------|
| Flutter SDK | 3.10.0 |
| Dart SDK | 3.0.0 |
| Android Studio / Xcode | Latest stable |
| Android emulator or physical device | API 21+ |
| iOS Simulator (macOS only) | iOS 14+ |

Install Flutter: https://docs.flutter.dev/get-started/install

Verify your setup:

```bash
flutter doctor
```

## Project Structure

```
mobile/
├── lib/
│   ├── main.dart                  # App entry point, router, providers
│   ├── providers/
│   │   ├── auth_provider.dart     # Authentication state (ChangeNotifier)
│   │   └── theme_provider.dart    # Theme mode persistence
│   ├── screens/
│   │   ├── login_screen.dart      # Login with API URL configuration
│   │   ├── dashboard_screen.dart  # Stats overview and recent issues
│   │   ├── iso_list_screen.dart   # Searchable, paginated ISO list
│   │   ├── scan_screen.dart       # Camera/gallery upload and validation
│   │   └── settings_screen.dart   # API URL, connection test, logout
│   ├── services/
│   │   └── api_service.dart       # HTTP client wrapping the backend API
│   └── widgets/
│       ├── stat_card.dart         # Reusable statistics card
│       └── status_badge.dart      # Colour-coded status chip
├── android/
│   └── app/src/main/
│       └── AndroidManifest.xml    # Permissions + cleartext traffic (dev)
└── pubspec.yaml
```

## Configuring the API URL

The app needs to reach the backend service. The default URL is
`http://10.0.2.2:8000` which routes to `localhost` on the host machine from
an Android emulator.

You can change the URL in two ways:

1. **Login screen** — the URL field is editable before signing in.
2. **Settings screen** — change and save a new URL after login. Tap
   "Test Connection" to verify before saving.

### Common URL values

| Environment | URL |
|-------------|-----|
| Android emulator → host localhost | `http://10.0.2.2:8000` |
| iOS Simulator → host localhost | `http://127.0.0.1:8000` |
| Physical device on same Wi-Fi | `http://<host-ip>:8000` |
| Production | `https://your-domain.com` |

## Running on an Emulator

### Android

```bash
# Start an Android emulator from Android Studio (Device Manager),
# then from the mobile/ directory:
cd mobile
flutter pub get
flutter run
```

### iOS (macOS only)

```bash
open -a Simulator
cd mobile
flutter pub get
flutter run
```

## Running on a Physical Device

1. Enable **Developer Options** and **USB Debugging** (Android) or trust the
   Mac (iOS).
2. Connect the device via USB.
3. Run:

```bash
cd mobile
flutter pub get
flutter run
```

## Running Tests

```bash
cd mobile
flutter test
```

## Building for Release

### Android APK

```bash
cd mobile
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk
```

### Android App Bundle (for Play Store)

```bash
cd mobile
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

### iOS (macOS only)

```bash
cd mobile
flutter build ios --release
# Then open ios/Runner.xcworkspace in Xcode to archive and distribute.
```

## Environment Notes

- `android:usesCleartextTraffic="true"` is set in `AndroidManifest.xml` to
  allow plain HTTP during development. For production, use HTTPS and remove
  this flag (or set it to `false`).
- Tokens are stored in **flutter_secure_storage** (Android Keystore /
  iOS Keychain). API URL is stored in **shared_preferences**.

## Dependencies

| Package | Purpose |
|---------|---------|
| `http` | HTTP client |
| `shared_preferences` | Persistent key-value storage (API URL, theme) |
| `flutter_secure_storage` | Encrypted token storage |
| `provider` | State management |
| `go_router` | Declarative routing |
| `intl` | Date/number formatting |
| `image_picker` | Camera and gallery access |
| `fl_chart` | Charts (available for future use) |
| `cached_network_image` | Cached remote images |
