# Changelog

All notable changes to the Contract Tracker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-09-30

### Added
- **Custom Holidays Management**: Complete system for managing user-defined holiday periods
- **EBRD Christmas Closure Support**: Specific support for EBRD office closures and shutdowns
- **Holiday Types**: Bank Holiday, Office Closure, and Personal Holiday categories
- **Settings UI**: Full CRUD interface for custom holidays in Settings page
- **Calendar Integration**: Custom holidays display in calendar with appropriate icons (🏛️, 🚫, 🏖️)
- **API Endpoints**: Complete REST API for custom holidays management
- **Data Source Toggle**: Custom holidays can be enabled/disabled in data sources

### Technical Details
- **New Models**: `CustomHoliday` and `CustomHolidayCollection` data models
- **New Repository**: `CustomHolidayRepository` for data persistence
- **New API Routes**: `/api/custom-holidays` with full CRUD operations
- **Calendar Integration**: Custom holidays appear in contract calendar view
- **Validation**: Date range validation and overlap prevention

## [1.2.0] - 2025-09-30

### Fixed
- **Calendar Day-of-Week Display**: Fixed JavaScript calendar to correctly show Monday as first day of week
- **Timezone Issues**: Resolved date shifting problems caused by UTC conversion in `toISOString()`
- **Back to Contracts Navigation**: Fixed 404 error when clicking "Back to Contracts" button (trailing slash issue)
- **Contract Key Management**: Improved contract identification system with stable `contract_id` instead of composite keys

### Added
- **Out-of-Scope Day Cleanup**: Added "Fix" button to automatically remove day allocations outside contract period
- **Enhanced Data Integrity**: Improved contract data migration and key management
- **Better Error Handling**: More robust contract editing and validation

### Changed
- **Contract Editing**: Now uses stable `contract_id` for updates instead of changing composite keys
- **Date Handling**: Switched to timezone-safe date formatting to prevent UTC conversion issues
- **API Endpoints**: Added new endpoint `/api/contracts/{key}/fix-out-of-scope` for cleanup operations

## [1.0.0] - 2025-09-30

### Added
- **Initial Release** of Contract Tracker
- **Multi-Contract Management**: Track multiple contracts simultaneously with unique keys
- **Calendar-Based Planning**: Visual calendar interface for day allocation similar to spreadsheet
- **Smart Day Suggestions**: Automatically suggest optimal working days (110 weekdays)
- **Constraint Validation**: Ensure contract rules are followed (exactly 110 working days)
- **Day Status System**: 6 different day types (Working, Bank Holiday, Holiday/Sick, In Lieu, On Call, Not Applicable)
- **Financial Tracking**: Monitor earnings and contract values with VAT calculations
- **Flexible Planning**: Drag-and-drop style day allocation with real-time updates
- **RESTful API**: Complete API for programmatic access and external integrations
- **Docker Support**: Full containerization with Docker and Docker Compose
- **Production Ready**: Nginx reverse proxy, security headers, rate limiting
- **Data Persistence**: JSON-based storage with automatic backups
- **Responsive Design**: Modern web interface that works on desktop and mobile
- **Health Monitoring**: Container health checks and logging
- **Management Scripts**: Easy-to-use Docker management tools

### Technical Features
- **Modular Architecture**: Clean separation of concerns with models, services, and data layers
- **Type Safety**: Python type hints throughout the codebase
- **Error Handling**: Comprehensive error handling and user feedback
- **Security**: Non-root Docker user, security headers, input validation
- **Performance**: Gzip compression, static file caching, optimized Docker layers
- **Testing Ready**: Structure prepared for unit and integration tests
- **Documentation**: Comprehensive README with setup and usage instructions

### API Endpoints
- `GET /api/contracts/` - List all contracts
- `POST /api/contracts/` - Create new contract
- `GET /api/contracts/{key}` - Get specific contract
- `PUT /api/contracts/{key}` - Update contract
- `DELETE /api/contracts/{key}` - Delete contract
- `POST /api/contracts/{key}/days` - Update day status
- `GET /api/contracts/{key}/suggestions` - Get working day suggestions
- `POST /api/contracts/{key}/suggestions` - Apply suggestions
- `GET /api/contracts/{key}/validate` - Validate contract constraints
- `GET /api/dashboard/` - Get dashboard data
- `GET /api/dashboard/settings` - Get application settings
- `PUT /api/dashboard/settings` - Update settings

### Docker Features
- **Multi-stage Build**: Optimized Docker images for development and production
- **Docker Compose**: Easy orchestration with data persistence
- **Nginx Integration**: Reverse proxy with rate limiting and security
- **Health Checks**: Container health monitoring
- **Volume Mounting**: Persistent data storage
- **Environment Configuration**: Flexible environment variable support

## [Unreleased]

### Planned Features
- **Invoice Generation**: Create PDF invoices automatically
- **UK Bank Holiday Integration**: Real-time holiday data from gov.uk API
- **School Calendar Integration**: PraeWood School holidays
- **Calendar Export**: ICS file generation for external calendars
- **Multi-User Support**: Support for multiple staff members
- **Reporting Dashboard**: Advanced analytics and reporting
- **Mobile App**: Native mobile application
- **Database Migration**: PostgreSQL support for larger deployments
- **Caching Layer**: Redis for improved performance
- **Background Tasks**: Celery for async operations
- **API Rate Limiting**: Enhanced protection against abuse
- **Automated Testing**: Comprehensive test coverage
- **CI/CD Pipeline**: Automated testing and deployment

### Technical Improvements
- **Performance Optimization**: Database indexing and query optimization
- **Security Enhancements**: JWT authentication, RBAC permissions
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Logging**: Structured logging with ELK stack integration
- **Backup Strategy**: Automated backup and disaster recovery
- **Scaling**: Kubernetes deployment manifests
- **API Versioning**: Semantic API versioning strategy
