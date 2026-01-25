# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New authentication method with OAuth2

## [1.2.0] - 2024-01-20

### Added

- User profile page with avatar support
- Export data to CSV functionality
- Dark mode toggle in settings

### Changed

- Improved API response time by 40%
- Updated dashboard layout for better UX

### Deprecated

- Legacy API endpoint `/api/v1/users` (use `/api/v2/users` instead)

### Fixed

- Login timeout issue on slow connections (#142)
- Memory leak in WebSocket handler (#138)

## [1.1.0] - 2024-01-10

### Added

- Real-time notifications
- Two-factor authentication

### Security

- Fixed XSS vulnerability in comment field (CVE-2024-XXXX)
- Updated dependencies to patch known vulnerabilities

## [1.0.0] - 2024-01-01

### Added

- Initial release
- User registration and login
- Dashboard with analytics
- REST API with rate limiting
- Documentation and API reference

[unreleased]: https://github.com/user/project/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/project/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/user/project/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/user/project/releases/tag/v1.0.0
