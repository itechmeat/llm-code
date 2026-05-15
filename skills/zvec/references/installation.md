# Installation

This skill assumes Zvec is already installed. Use this page only when you need to set up Zvec in a new environment.

Official prebuilt packages now cover the main desktop/server targets, including Windows support added in `0.3.0` and official Flutter/mobile support in `0.4.0`.

## Python

- Requirement (as documented in the GitHub README): Python 3.10–3.14

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
- Windows (`x86_64`)
- Android (`arm64-v8a`) via Flutter package
- iOS (`arm64`) via Flutter package

## Build from source

If you need an unsupported platform/architecture or want unreleased behavior, use the upstream build guide instead of assuming package availability.

## Links

- GitHub README (installation snippets): https://github.com/alibaba/zvec
- Quickstart: https://zvec.org/en/docs/quickstart/
- Build guide: https://zvec.org/en/docs/db/build/
