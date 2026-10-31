# Changelog

All notable changes to the Drop&Go project will be documented in this file.

The format follows a simplified version of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses semantic versioning where applicable.

## [1.0.0] - 2026-10-31

### Added
- Initial commercial release of Drop&Go.
- FastAPI backend.
- SQLAlchemy ORM integration.
- SQLite database support.
- JWT-based authentication system.
- Bcrypt password hashing.
- Role-based access control for administrators and store owners.
- English and Turkish language support.
- Dynamic template rendering for internationalization.
- White-label settings for application name, currency, and default language.
- Store dashboard for monitoring business activity.
- Chart.js integration for dashboard analytics.
- QR code scanning API for booking identification and luggage status updates.
- Luggage status workflow: Pending, Stored, and Retrieved.
- PDF receipt generation through HTML2PDF integration.
- Jinja2 template rendering.
- Bootstrap 5 frontend integration.
- Docker configuration.
- Docker Compose deployment configuration.
- Default administrator account initialization.
- Default store owner account initialization.
- Installation and deployment documentation.
- README documentation.

### Security
- JWT-based authentication.
- Bcrypt password hashing.
- Role-based access control.
- Documentation recommending the replacement of default credentials before production deployment.

### Documentation
- Added installation instructions.
- Added Docker deployment commands.
- Added default account information.
- Added technology stack documentation.
- Added security recommendations.
- Added version history documentation.

---

## Versioning Policy

Drop&Go uses a versioning approach intended to communicate the scope of each release.

- **Major version:** Introduces significant changes that may affect compatibility.
- **Minor version:** Introduces new features while aiming to preserve compatibility.
- **Patch version:** Includes bug fixes and minor improvements.

## Upcoming Releases

Future releases may include additional features, improvements, and bug fixes as they are implemented and verified.

Planned or potential enhancements should not be considered available features until they have been released.