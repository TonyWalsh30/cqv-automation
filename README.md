# CQV Automation Demonstrator

An intelligent Commissioning, Qualification, and Validation (CQV) automation system for pharmaceutical manufacturing equipment.

## Overview

This system demonstrates automated document generation and digital execution for equipment validation, using:

- **ISA-88 Physical Model**: Standardized equipment hierarchy (Unit → Equipment Module → Control Module)
- **B2MML Data Ingestion**: Simulated manufacturing data import
- **Gherkin Requirements**: Machine-readable functional requirements
- **Automated Protocol Generation**: IQ/OQ document generation from structured data
- **Digital Execution**: Paperless validation workflow

## Architecture

### Backend (Python/Flask)
- **Database**: SQLite (development) with PostgreSQL-compatible schema
- **API**: RESTful endpoints for asset management
- **Services**: B2MML parser, asset queries, protocol generation (coming soon)
- **ORM**: SQLAlchemy for database operations

### Frontend (React - Coming Soon)
- Modern React UI with Vite
- Asset hierarchy visualization
- Requirement management interface
- Digital protocol execution

## Project Structure

```
cqv-automation/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── models.py              # SQLAlchemy ORM models
│   ├── database.py            # Database configuration
│   ├── services/
│   │   ├── b2mml_parser.py   # XML parsing service
│   │   └── asset_service.py   # Asset query logic
│   └── routes/
│       └── assets.py          # Asset API endpoints
├── data/
│   ├── bio-01-b2mml.xml      # Sample B2MML equipment data
│   └── cqv_automation.db     # SQLite database (generated)
└── frontend/                  # React frontend (coming soon)
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend)
- pip (Python package manager)

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Initialize the database**:
   ```bash
   python app.py
   ```
   The database will be automatically created in `data/cqv_automation.db`

3. **Ingest sample B2MML data**:
   ```bash
   # Option 1: Via API (with server running)
   curl -X POST http://localhost:5000/api/ingest/b2mml

   # Option 2: Direct script
   cd services
   python b2mml_parser.py
   ```

### API Endpoints

**Health Check**:
```bash
GET http://localhost:5000/api/health
```

**Get All Assets**:
```bash
GET http://localhost:5000/api/assets
```

**Get Asset Hierarchy**:
```bash
GET http://localhost:5000/api/assets/tag/BIO-01/hierarchy
```

**Get Control Modules** (for IQ generation):
```bash
GET http://localhost:5000/api/assets/tag/BIO-01/control-modules
```

**Ingest B2MML XML**:
```bash
POST http://localhost:5000/api/ingest/b2mml
```

## Sample Data: Bioreactor BIO-01

The system includes a sample 500L Bioreactor unit with:

- **Unit**: BIO-01 (500L Bioreactor)
  - **Equipment Module**: EM-01 (Temperature Control Loop)
    - Temperature Transmitter (TT-101)
    - Steam Inlet Valve (VLV-101)
  - **Equipment Module**: EM-02 (Agitation System)
    - Agitator Motor (MTR-101)
    - Speed Controller (SC-101)

Each control module includes properties like Manufacturer, Serial Number, Model, etc.

## Development Roadmap

### Phase 1: Data Architecture ✅ (Current)
- [x] Database schema (ISA-88)
- [x] B2MML XML parser
- [x] Asset API endpoints
- [ ] Frontend asset viewer

### Phase 2: Requirement Management (Next)
- [ ] Requirements database model
- [ ] Gherkin parser service
- [ ] Requirements management UI
- [ ] Asset-to-requirement traceability

### Phase 3: Automation Engine
- [ ] Jinja2 template integration
- [ ] IQ generator algorithm
- [ ] OQ generator algorithm
- [ ] Document generation API

### Phase 4: Execution Workflow
- [ ] Digital execution interface
- [ ] User authentication
- [ ] Audit logging
- [ ] Requirement Traceability Matrix (RTM)

## Technology Stack

- **Backend**: Python 3.9+, Flask, SQLAlchemy
- **Database**: SQLite (dev), PostgreSQL (production-ready)
- **XML Parsing**: lxml
- **Templating**: Jinja2
- **Frontend**: React, Vite (coming soon)

## License

Proprietary - Internal Use Only
