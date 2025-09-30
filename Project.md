
Introduction

I am a contractor, which means I work for multiple companies.
Currently I work for one company, EBRD.

I track each day I work, and when I dont.

My contract is limited by Time and Money, although Money is also Time, and therefore really only limited by Days. For example, my current contract has a start date, end date, and a number of days that I can work ( 110 days ).

My contract renews every 6 months, but this can very in length.

EBRD Pays me £575 per day, and I charge VAT on top of that. VAT gets paid on to the Inland Revenue, so I dont get the money, but its on the Invoice.

I also have to factor in the various imposed Holidays throughout the year, so that I always get the maximum money from the contract. Things like Christmas where the company is closed for 2 weeks.

This is VERY IMPORTANT. Always get the full amount of money from a Contract.

I am limited to taking a maximum of 2 weeks holiday at any one time, with a weeks gap.

For EBRD, each month I fill in my timesheet on an Application called Keyed-In.
Based on this, I submit invoices via email, to get paid for the previous month.

-----

I work for my own company ElectioSolutions Limited, which is contracted to the various companies. So currently I'm a one-person company, although my wife, Corrine, might was also on the books previously.

My Company has a Financial Year, from 15-jul -> 14-jul.. this date will need confirming.

I need a way to track the days that I have worked; the days I can't work, and therefore plan the days I have to take as leave to fulfil the 110 days correctly.

I'm free to move the planned days around as I please, but have to give notice to the Company. Things like school Half-Term  weeks and things like that are usual times for breaks.

-----

What do I need ?

I need to plan the days so that I can raise accurate invoices, and get the most from the Contract.
I need to have a view on "Money Earnt" for the financial year, as sometimes its better to move holiday past the end of the financial year, in order to balance an income. Also predicted income based on the planned calender.

Additional ToDos
----------------

* Raise the Invoices & Email in.
* Create Credit Notes, Invoices and Remittance Advice PDFs

Funcional Specs

We're going to create a Python Web App.
All Data MUST be sanatised before being allowed into the Application.
This includes all API data and URLs.

I will need to be able to Load & Save Contract Files, which contain all the planned data.
I will need UK England Holidays pulled in, and also school holidays. Note I may not take the official holidays as holidays, so this needs to be optional.

Cursor Additions:

## Functional Requirements

### Core Contract Management
- **Multi-Contract Support**: System must handle multiple contracts simultaneously, keyed by:
  - Staff Name
  - Client Company Name  
  - Contract Name
- **Contract Structure**: Each contract contains:
  - Start/End dates
  - Total working days allowance (e.g., 110 days)
  - Daily rate (£575 + configurable VAT)
  - Contract renewal period (typically 6 months, configurable)

### Day Tracking System
- **Day States**:
  - "Actually Worked" - Confirmed completed days
  - "Plan to Work" - Manually agreed future working days
  - "Predicted" - System-suggested days (subject to change)
  - "Holiday/Not Working" - Planned non-working days
- **Working Day Calculation**: Only count days explicitly marked as "Actually Worked" or "Plan to Work"
- **Flexible Planning**: Allow last-minute changes to planned days

### Data Sources & Calendar Integration
- **UK Bank Holidays**: Automatic API integration for England/Wales holidays
- **School Holidays**: PraeWood School (Hertfordshire) calendar integration
- **Modular Data Sources**: Extensible system to add additional holiday/calendar sources
- **ICS Export**: Generate dynamic ICS URL for "Days As Holiday" that updates automatically
- **Suggestion System**: All data sources show as suggestions - manual approval required

### Holiday Management
- **Holiday Highlighting**: Display imposed holidays (Christmas, etc.) as highlighted periods
- **Constraint Warnings**: Alert when violating "max 2 weeks holiday + 1 week gap" rule
- **Flexible Allocation**: Allow overrides despite constraint warnings
- **Financial Year Optimization**: Support moving holidays across financial year boundary for income balancing

### Financial Tracking
- **Daily Rate**: £575 + configurable VAT rate
- **Earned vs Predicted**: Separate tracking of actual earnings vs predicted income
- **Financial Year**: Configurable period (default: 15-Jul to 14-Jul)
- **Income Forecasting**: Predict total income based on planned calendar

### Data Management
- **File Format**: JSON for contract files
- **Save/Load**: Full contract data persistence including all planned days and settings
- **Configuration**: System settings for financial year, VAT rates, default constraints

## Technical Requirements

### Technology Stack
- **Backend**: Python Web Application
- **Framework**: Flask/FastAPI (TBD)
- **Data Storage**: JSON files with option to migrate to database later
- **Frontend**: HTML/CSS/JavaScript (modern responsive design)

### API Integrations
- UK Bank Holidays API (gov.uk or alternative)
- School calendar data for PraeWood School
- Extensible module system for additional data sources

### Key Features
1. **Calendar View**: Interactive calendar showing working days, holidays, and constraints
2. **Contract Dashboard**: Overview of all active contracts with key metrics
3. **Day Planner**: Drag-and-drop interface for planning working days
4. **Financial Summary**: Earned vs predicted income with financial year breakdown
5. **Export Functions**: ICS calendar export, contract data backup/restore
6. **Settings Panel**: Configure financial year, VAT rates, holiday constraints

### User Interface Requirements
- **Responsive Design**: Work on desktop and tablet
- **Intuitive Planning**: Easy day allocation with visual feedback
- **Constraint Alerts**: Clear warnings for rule violations
- **Data Source Management**: Add/remove/modify calendar data sources
- **Multi-Contract Navigation**: Easy switching between different contracts

### Future Extensibility
- Invoice generation module (out of scope for initial version)
- Additional staff member support (Corrine)
- Integration with Keyed-In timesheet system
- Advanced reporting and analytics

## Implementation Status

### Completed Features ✅

#### Core Application
- **Flask Web Application**: Full Python web app with modular architecture
- **Docker Containerization**: Complete Docker setup with docker-compose.yml
- **JSON Data Persistence**: Contract and settings data stored in JSON format
- **RESTful API**: Complete API endpoints for all contract operations
- **HTML Frontend**: Full responsive web interface with Bootstrap styling

#### Contract Management
- **Multi-Contract Support**: System handles multiple contracts simultaneously
- **Contract CRUD Operations**: Create, read, update, delete contracts
- **Contract Validation**: Comprehensive validation with health scoring
- **Day Allocation System**: Track working days, holidays, and planned days
- **Calendar Integration**: Interactive calendar views for each contract

#### Data Sanitization & Security
- **Multi-Layer Sanitization**: Client-side, server-side API, model, and repository sanitization
- **XSS Prevention**: HTML sanitization using bleach library
- **URL Safety**: Contract keys sanitized for safe URL routing
- **Input Validation**: Comprehensive validation for all user inputs

#### User Interface
- **Dashboard**: Overview with contract statistics and quick access
- **Contracts List**: Dedicated contracts management page
- **New Contract Form**: Interactive form with real-time validation
- **Contract Details**: Individual contract management pages
- **Settings Page**: Application configuration with helpful descriptions
- **Calendar Views**: Interactive calendar for day planning

#### Settings & Configuration
- **Financial Settings**: Configurable daily rate, VAT rate, financial year
- **Holiday Constraints**: Max holiday weeks, gap weeks configuration
- **Calendar Settings**: Week start day (Monday/Sunday), weekend display options
- **Data Sources**: UK Bank Holidays, PraeWood School Holidays integration

#### Data Sources Integration
- **UK Bank Holidays**: Automatic holiday data integration
- **School Holidays**: PraeWood School calendar integration
- **Suggestion System**: Smart day allocation suggestions
- **Constraint Warnings**: Holiday constraint violation alerts

### Technical Implementation
- **Modular Architecture**: Clean separation of models, services, API, and data layers
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5
- **Git Version Control**: Complete version control setup
- **Health Monitoring**: Docker container health checks
- **Environment Configuration**: Proper environment variable management

### Testing & Quality Assurance
- **Comprehensive Testing**: Full application flow testing completed
- **Data Sanitization Testing**: XSS and injection attack prevention verified
- **Cross-Page Navigation**: All page transitions and URL routing tested
- **Error Recovery**: Error handling and recovery mechanisms tested
- **Browser Compatibility**: Chrome browser testing completed

### Documentation
- **Project Documentation**: Comprehensive Project.md with specifications
- **Docker Documentation**: Complete Docker setup and deployment guide
- **API Documentation**: RESTful API endpoints documented
- **Code Comments**: Well-documented codebase with clear comments


