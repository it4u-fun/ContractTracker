# Contract Tracker

A modern web application for tracking contractor days and managing contracts. Built with Python Flask and containerized with Docker, this application helps contractors plan their working days, track earnings, and ensure they meet their contract obligations.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

### Core Functionality
- **Multi-Contract Management**: Track multiple contracts simultaneously
- **Calendar-Based Planning**: Visual calendar interface for day allocation
- **Smart Suggestions**: Automatically suggest optimal working days
- **Constraint Validation**: Ensure contract rules are followed
- **Financial Tracking**: Monitor earnings and contract values
- **Export Capabilities**: Export calendar data for external use

### Day Status Types
- **Working**: Days allocated for work
- **Bank Holiday**: Official bank holidays
- **Holiday/Sick**: Personal time off
- **In Lieu**: Compensatory time off
- **On Call**: Standby or carry-over time
- **Not Applicable**: Days outside contract scope

### Key Benefits
- **Contract Balance Validation**: Ensure exactly 110 working days (or custom amount)
- **Holiday Constraint Checking**: Prevent violations of holiday rules
- **Financial Year Optimization**: Balance income across financial periods
- **Visual Progress Tracking**: See contract completion at a glance
- **Flexible Planning**: Adjust allocations as circumstances change

## Installation

### Option 1: Docker (Recommended)

The easiest way to run Contract Tracker is using Docker:

#### Prerequisites
- Docker and Docker Compose installed

#### Quick Start
```bash
# Clone or download the project
cd ContractTracker

# Build and run with Docker
./docker-scripts.sh build
./docker-scripts.sh run
```

#### Using Docker Compose
```bash
# Run with docker-compose (includes data persistence)
docker-compose up -d

# Run with nginx reverse proxy
docker-compose --profile with-nginx up -d
```

#### Docker Management
```bash
# View status
./docker-scripts.sh status

# View logs
./docker-scripts.sh logs

# Stop the application
./docker-scripts.sh stop

# Clean up everything
./docker-scripts.sh cleanup
```

**Access the application at:** `http://localhost:5000`

### Option 2: Local Python Installation

#### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

#### Setup Instructions

1. **Clone or Download** the project to your local machine

2. **Navigate to the project directory**:
   ```bash
   cd ContractTracker
   ```

3. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   python run.py
   ```

6. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Creating Your First Contract

1. **Click "New Contract"** from the dashboard
2. **Fill in contract details**:
   - Staff Name: Your name
   - Client Company: Company you're contracting for (e.g., EBRD)
   - Contract Name: Description of the contract
   - Start/End Dates: Contract period
   - Total Working Days: Number of days to work (e.g., 110)
   - Daily Rate: Your daily rate in pounds
3. **Click "Create Contract"**

### Planning Working Days

1. **Navigate to the contract calendar**
2. **Use "Suggest Working Days"** to auto-allocate weekdays
3. **Click on any day** to change its status
4. **Adjust allocations** as needed
5. **Check the status panel** to ensure you're on track

### Understanding the Interface

- **Green Days**: Working days
- **Yellow Days**: Bank holidays
- **Red Days**: Personal holidays/sick days
- **Blue Days**: In lieu days
- **Gray Days**: On call or not applicable
- **Progress Bar**: Shows completion percentage
- **Health Score**: Overall contract health (0-100)

## Configuration

### Application Settings

The application can be configured through the Settings page:

- **Financial Year**: Default start date (15-Jul)
- **VAT Rate**: Tax rate percentage (20%)
- **Daily Rate**: Default daily rate (£575)
- **Holiday Constraints**: Maximum holiday periods and gaps
- **Data Sources**: Enable/disable external calendar integrations

### Data Storage

- **Contracts**: Stored in `data/contracts.json`
- **Settings**: Stored in `data/settings.json`
- **Backups**: Automatic backups created on updates

## API Endpoints

The application provides a RESTful API for programmatic access:

### Contracts
- `GET /api/contracts/` - List all contracts
- `POST /api/contracts/` - Create new contract
- `GET /api/contracts/{key}` - Get specific contract
- `PUT /api/contracts/{key}` - Update contract
- `DELETE /api/contracts/{key}` - Delete contract

### Day Management
- `POST /api/contracts/{key}/days` - Update day status
- `GET /api/contracts/{key}/suggestions` - Get working day suggestions
- `POST /api/contracts/{key}/suggestions` - Apply suggestions

### Validation
- `GET /api/contracts/{key}/validate` - Validate contract constraints

### Dashboard
- `GET /api/dashboard/` - Get dashboard data
- `GET /api/dashboard/settings` - Get application settings
- `PUT /api/dashboard/settings` - Update settings

## Docker Deployment

### Production Deployment

For production deployment, use the production Dockerfile:

```bash
# Build production image
docker build -f Dockerfile.prod -t contract-tracker:prod .

# Run production container
docker run -d \
  --name contract-tracker-prod \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e FLASK_ENV=production \
  -e SECRET_KEY="your-secure-secret-key" \
  contract-tracker:prod
```

### Docker Compose for Production

```bash
# Start with nginx reverse proxy
docker-compose --profile with-nginx up -d
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `production` |
| `FLASK_DEBUG` | Enable debug mode | `False` |
| `SECRET_KEY` | Flask secret key | Required |

### Data Persistence

The application stores data in the `./data` directory which is mounted as a volume in Docker. This ensures your contracts and settings persist across container restarts.

## Development

### Project Structure
```
ContractTracker/
├── app/                    # Main application package
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── data/              # Data access layer
│   └── api/               # API endpoints
├── templates/             # HTML templates
├── static/                # CSS, JavaScript, images
├── data/                  # Data storage
├── tests/                 # Unit tests
├── config.py              # Configuration
├── run.py                 # Application entry point
└── requirements.txt       # Dependencies
```

### Running Tests
```bash
pytest tests/
```

### Ways of Working
- Prefer Docker via `./docker-scripts.sh` to build/run; keep the app running and healthy.
- After changes: rebuild, run, then verify UI/API; fix regressions immediately.
- Use the Chrome agent to validate pages at `http://localhost:5000` (UI states, console/network, performance).
- Keep docs up to date (`CHAT_LEARN.md`, `README.md`, `API.md`) and use conventional commits.

### Code Quality
```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/
```

## Future Enhancements

### Planned Features
- **Invoice Generation**: Create PDF invoices automatically
- **UK Bank Holiday Integration**: Real-time holiday data
- **School Calendar Integration**: PraeWood School holidays
- **Calendar Export**: ICS file generation for external calendars
- **Multi-User Support**: Support for multiple staff members
- **Reporting Dashboard**: Advanced analytics and reporting
- **Mobile App**: Native mobile application

### Technical Improvements
- **Database Migration**: Move from JSON to PostgreSQL
- **Caching Layer**: Redis for improved performance
- **Background Tasks**: Celery for async operations
- **API Rate Limiting**: Protect against abuse
- **Automated Testing**: Comprehensive test coverage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints

## Changelog

### Version 1.0.0 (Initial Release)
- Multi-contract management
- Calendar-based day planning
- Smart working day suggestions
- Contract validation and constraints
- Financial tracking and reporting
- Modern responsive web interface
- RESTful API for external integration

---

**Built with ❤️ for contractors by contractors**
