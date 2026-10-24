# Installation

This skill assumes Zvec is already installed. Use this page only when you need to set up Zvec in a new environment.

Official prebuilt packages now cover the main desktop/server targets, including Windows support added in `0.3.0` and official Flutter/mobile support in `0.4.0`.

## Python

- `0.8.0` ships native wheels for Python 3.11–3.14. Earlier interpreters (e.g. 3.10) are not in the `0.8.0` wheel matrix — check the upstream release notes before assuming support, and fall back to a source build if needed.

```bash
pip install zvec
```

## Node.js

```bash
npm install @zvec/zvec
```

## Dart / Flutter

`0.4.0` adds an official Flutter package:

```bash
flutter pub add zvec
```

- The package ships Dart/Flutter FFI bindings.
- Upstream release notes say Android (`arm64-v8a`) and iOS (`arm64`) prebuilt native libraries are downloaded automatically during the build.
- For mobile usage, prefer the official package over maintaining ad-hoc FFI glue.

## Supported platforms (official packages)

- Linux (`x86_64`, `ARM64`)
- macOS (`ARM64`)
- macOS (`x86_64`, Intel Mac) — added in `0.8.0`
- Windows (`x86_64`)
- Windows (`ARM64`, MSVC) with dedicated ARM64 SDK packages — added in `0.8.0`
- Android (`arm64-v8a`) via Flutter package
- iOS (`arm64`) via Flutter package

DiskANN indexes run on Windows and on the mobile platforms (Android, iOS) as of `0.8.0`; see `indexing.md` for the per-platform I/O behaviour.

## Build from source

If you need an unsupported platform/architecture or want unreleased behavior, use the upstream build guide instead of assuming package availability.

## Links

- GitHub README (installation snippets): https://github.com/alibaba/zvec
- Quickstart: https://zvec.org/en/docs/quickstart/
- Build guide: https://zvec.org/en/docs/db/build/
