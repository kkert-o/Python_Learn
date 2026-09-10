# Release signing

The debug build is automatically signed by Android and is only for development.
A public release must use a private keystore that is not committed to Git.

## Prepare the keystore

Create the keystore outside source control, for example:

```powershell
keytool -genkeypair `
  -v `
  -keystore release\python-learning.jks `
  -alias python-learning `
  -keyalg RSA `
  -keysize 4096 `
  -validity 10000
```

Create `keystore.properties` in the `PythonApp` directory based on
`keystore.properties.example`. The file is ignored by Git.

## Build a signed release

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:assembleRelease
```

If all four signing properties are present, Gradle signs the release APK with
the configured key. If they are absent, the release build remains unsigned and
the in-app release check reports that signing is not configured.

## Before publishing

1. Run unit tests and install the debug APK on at least one phone-sized and one
   tablet-sized emulator.
2. Verify light mode, dark mode, wallpaper text contrast, and system back
   navigation across every nested screen.
3. Run the Python runtime smoke test from `我的 > 发布与设备检查`.
4. Back up the keystore and passwords in a secure password manager. Losing the
   release key prevents future updates under the same application identity.
5. Build the Android App Bundle for distribution:

```powershell
.\gradlew.bat :app:bundleRelease
```
