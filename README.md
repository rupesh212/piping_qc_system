# Piping QA/QC Automation System

An enterprise-grade system for automating piping isometric QA/QC validation — replacing manual checking done via Bluebeam, Excel, and manual review.

## Phase 1 — MVP Features

- **ISO Module**: Upload PDF/image ISO drawings, extract line number/size/spec via OCR
- **Line List Module**: Upload Excel line lists, parse and store entries
- **PMS Module**: Upload Piping Material Specification Excel, validate spec/material/rating
- **Rule Engine**: 5 cross-validation rules (spec_match, size_match, pms_spec_exists, pms_material_valid, pms_rating_check)
- **Dashboard**: Real-time summary, error panel, line status tracking
- **Auth**: JWT-based login with role-based access (Admin / QA / Site)

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + SQLAlchemy + PostgreSQL |
| OCR | pytesseract + pdf2image |
| Excel | pandas + openpyxl |
| Auth | JWT (python-jose) + bcrypt |
| Frontend | React 18 + Vite + Tailwind CSS |
| Infrastructure | Docker + docker-compose |

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env if needed (DB credentials, SECRET_KEY)

# 2. Start all services
docker-compose up --build

# 3. Run DB migrations + seed admin user
docker-compose exec backend alembic upgrade head
docker-compose exec backend python seed.py

# 4. Open the app
# Frontend:  http://localhost:3000
# API docs:  http://localhost:8000/docs
# Health:    http://localhost:8000/health
```

### Default Credentials

| Username | Password | Role |
|---|---|---|
| admin | admin123 | Admin |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /api/v1/auth/login | Login → JWT token |
| POST | /api/v1/auth/register | Create user (admin only) |
| GET | /api/v1/auth/me | Current user |
| POST | /api/v1/iso/upload | Upload ISO drawing |
| GET | /api/v1/iso/ | List ISOs |
| POST | /api/v1/iso/{id}/validate | Run rule engine |
| POST | /api/v1/linelist/upload | Upload Line List Excel |
| GET | /api/v1/linelist/{batch_id} | Get line list entries |
| POST | /api/v1/pms/upload | Upload PMS Excel |
| GET | /api/v1/pms/{batch_id} | Get PMS entries |
| GET | /api/v1/dashboard/summary | KPI summary |
| GET | /api/v1/dashboard/errors | Recent errors |
| GET | /api/v1/dashboard/line-status | Per-line status |

## Validation Rules

| Rule | Logic |
|---|---|
| `spec_match` | ISO spec == Line List spec |
| `size_match` | ISO pipe size == Line List pipe size |
| `pms_spec_exists` | Spec code exists in PMS |
| `pms_material_valid` | PMS material is non-empty |
| `pms_rating_check` | PMS rating is non-empty |

## Project Structure

```
piping_qc_system/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Route handlers
│   │   ├── core/            # JWT + deps
│   │   ├── models/          # SQLAlchemy ORM
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # OCR, Excel, Rule Engine
│   │   └── utils/
│   ├── alembic/             # DB migrations
│   └── seed.py
├── frontend/
│   └── src/
│       ├── pages/           # Dashboard, ISO, LineList, PMS, Login
│       ├── components/      # Navbar, FileUpload, DataTable, StatusBadge
│       └── contexts/        # AuthContext
└── docker-compose.yml
```

## Roadmap

- **Phase 2**: Navisworks plugin, routing comparison, BOM validation
- **Phase 3**: AI-powered ISO parser (LayoutLMv3 + YOLOv8)
- **Phase 4**: Unity 3D viewer, QR weld tracking, Flutter mobile app
- **Phase 5**: CI/CD, cloud deployment (AWS/Azure), monitoring
