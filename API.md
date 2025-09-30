# Contract Tracker API Documentation

This document provides comprehensive documentation for the Contract Tracker REST API.

## Base URL

- **Development**: `http://localhost:5000/api`
- **Production**: `https://your-domain.com/api`

## Authentication

Currently, the API does not require authentication. Future versions will implement JWT-based authentication.

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Endpoints

### Contracts

#### List All Contracts
```http
GET /api/contracts/
```

**Response:**
```json
{
  "success": true,
  "contracts": {
    "John_EBRD_2025_Contract": {
      "key": "John_EBRD_2025_Contract",
      "staff_name": "John",
      "client_company": "EBRD",
      "contract_name": "2025 Contract",
      "start_date": "2025-07-01",
      "end_date": "2026-06-30",
      "total_days": 110,
      "daily_rate": 575,
      "working_days_count": 0,
      "remaining_days": 110,
      "is_balanced": false,
      "total_value": 63250,
      "earned_value": 0,
      "created_at": "2025-09-30T11:14:55.474662",
      "updated_at": "2025-09-30T11:14:55.474662"
    }
  }
}
```

#### Create Contract
```http
POST /api/contracts/
Content-Type: application/json

{
  "staff_name": "John",
  "client_company": "EBRD",
  "contract_name": "2025 Contract",
  "start_date": "2025-07-01",
  "end_date": "2026-06-30",
  "total_days": 110,
  "daily_rate": 575
}
```

**Response:**
```json
{
  "success": true,
  "contract": { ... },
  "contract_key": "John_EBRD_2025_Contract"
}
```

#### Get Contract
```http
GET /api/contracts/{contract_key}
```

**Response:**
```json
{
  "success": true,
  "contract": {
    "staff_name": "John",
    "client_company": "EBRD",
    "contract_name": "2025 Contract",
    "start_date": "2025-07-01",
    "end_date": "2026-06-30",
    "total_days": 110,
    "daily_rate": 575,
    "days": {
      "2025-07-01": {
        "date": "2025-07-01",
        "status": "working",
        "is_weekend": false,
        "notes": null
      }
    },
    "created_at": "2025-09-30T11:14:55.474662",
    "updated_at": "2025-09-30T11:14:55.474662"
  },
  "validation": {
    "is_valid": false,
    "violations": ["Insufficient working days: 1 < 110"],
    "warnings": [],
    "suggestions": []
  }
}
```

#### Update Contract
```http
PUT /api/contracts/{contract_key}
Content-Type: application/json

{
  "daily_rate": 600,
  "total_days": 120
}
```

#### Delete Contract
```http
DELETE /api/contracts/{contract_key}
```

### Day Management

#### Update Day Status
```http
POST /api/contracts/{contract_key}/days
Content-Type: application/json

{
  "date": "2025-07-01",
  "status": "working",
  "notes": "First day of contract"
}
```

**Response:**
```json
{
  "success": true,
  "working_days_count": 1,
  "remaining_days": 109,
  "is_balanced": false,
  "validation": { ... }
}
```

**Day Status Values:**
- `working`: Working day
- `bank_holiday`: Bank holiday/office shut
- `holiday`: Holiday/sick day
- `in_lieu`: In lieu (off but paid)
- `on_call`: On call/carry over time
- `not_applicable`: Not applicable

### Suggestions

#### Get Working Day Suggestions
```http
GET /api/contracts/{contract_key}/suggestions?avoid_weekends=true&strategy=balanced
```

**Query Parameters:**
- `avoid_weekends`: boolean (default: true)
- `avoid_holidays`: boolean (default: true)
- `strategy`: string (balanced, front_loaded, back_loaded)

**Response:**
```json
{
  "success": true,
  "suggestions": [
    "2025-07-01",
    "2025-07-03",
    "2025-07-07",
    ...
  ],
  "count": 110
}
```

#### Apply Suggestions
```http
POST /api/contracts/{contract_key}/suggestions
Content-Type: application/json

{
  "suggested_dates": [
    "2025-07-01",
    "2025-07-03",
    ...
  ]
}
```

### Validation

#### Validate Contract
```http
GET /api/contracts/{contract_key}/validate
```

**Response:**
```json
{
  "success": true,
  "validation": {
    "is_valid": false,
    "violations": [
      "Insufficient working days: 1 < 110"
    ],
    "warnings": [
      "Only 109 working days remaining to allocate"
    ],
    "suggestions": [
      "Consider using the suggestion service to auto-allocate the remaining 109 days"
    ]
  },
  "health_score": {
    "score": 85,
    "status": "Good",
    "violations_count": 1,
    "warnings_count": 1,
    "suggestions_count": 1
  }
}
```

### Dashboard

#### Get Dashboard Data
```http
GET /api/dashboard/
```

**Response:**
```json
{
  "success": true,
  "dashboard": {
    "total_contracts": 1,
    "total_value": 63250,
    "total_earned": 0,
    "total_remaining": 63250,
    "contracts": [
      {
        "key": "John_EBRD_2025_Contract",
        "staff_name": "John",
        "client_company": "EBRD",
        "contract_name": "2025 Contract",
        "start_date": "2025-07-01",
        "end_date": "2026-06-30",
        "total_days": 110,
        "daily_rate": 575,
        "working_days_count": 0,
        "remaining_days": 110,
        "is_balanced": false,
        "total_value": 63250,
        "earned_value": 0,
        "progress_percentage": 0.0,
        "health_score": {
          "score": 100,
          "status": "Excellent"
        }
      }
    ]
  },
  "settings": {
    "financial_year_start": "15-Jul",
    "vat_rate": 20,
    "daily_rate": 575,
    "max_holiday_weeks": 2,
    "holiday_gap_weeks": 1,
    "week_starts_monday": true,
    "show_weekends": true,
    "enabled_data_sources": {
      "uk_bank_holidays": true,
      "praewood_school": true
    }
  }
}
```

#### Get Settings
```http
GET /api/dashboard/settings
```

#### Update Settings
```http
PUT /api/dashboard/settings
Content-Type: application/json

{
  "daily_rate": 600,
  "vat_rate": 20,
  "financial_year_start": "01-Apr"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `CONTRACT_NOT_FOUND` | Contract with specified key does not exist |
| `INVALID_DATE_FORMAT` | Date format is invalid (use YYYY-MM-DD) |
| `INVALID_DAY_STATUS` | Day status value is not recognized |
| `MISSING_REQUIRED_FIELD` | Required field is missing from request |
| `CONTRACT_EXISTS` | Contract with this key already exists |
| `VALIDATION_FAILED` | Contract validation failed |

## Rate Limiting

- **API Endpoints**: 10 requests per second
- **Web Interface**: 30 requests per second
- **Static Files**: 50 requests per second

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1696075200
```

## Examples

### Complete Workflow

1. **Create a contract:**
```bash
curl -X POST http://localhost:5000/api/contracts/ \
  -H "Content-Type: application/json" \
  -d '{
    "staff_name": "John",
    "client_company": "EBRD",
    "contract_name": "2025 Contract",
    "start_date": "2025-07-01",
    "end_date": "2026-06-30",
    "total_days": 110,
    "daily_rate": 575
  }'
```

2. **Get working day suggestions:**
```bash
curl http://localhost:5000/api/contracts/John_EBRD_2025_Contract/suggestions
```

3. **Apply suggestions:**
```bash
curl -X POST http://localhost:5000/api/contracts/John_EBRD_2025_Contract/suggestions \
  -H "Content-Type: application/json" \
  -d '{"suggested_dates": ["2025-07-01", "2025-07-03", ...]}'
```

4. **Validate contract:**
```bash
curl http://localhost:5000/api/contracts/John_EBRD_2025_Contract/validate
```

5. **Update specific day:**
```bash
curl -X POST http://localhost:5000/api/contracts/John_EBRD_2025_Contract/days \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-07-01",
    "status": "holiday",
    "notes": "Personal holiday"
  }'
```

## SDKs and Libraries

Currently, no official SDKs are available. The API is designed to be consumed by any HTTP client. Future versions may include:

- Python SDK
- JavaScript/TypeScript SDK
- CLI tool
- Postman collection

## Support

For API support:
- Create an issue on GitHub
- Check the main README for general help
- Review the inline documentation in the code
