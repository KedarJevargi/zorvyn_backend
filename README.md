# Zorvyn Backend API

A well-structured REST API for a finance dashboard system with role-based access control, financial record management, and aggregated analytics.

Built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy 2.0**.

> System is optimized for read-heavy workloads with indexed queries and connection pooling.

---

## System Architecture
```
Client (Swagger UI / Frontend)
  │
  │  HTTP Request + Bearer Token
  ▼
FastAPI (Routers)
  │
  ├── JWT Middleware (authentication)
  ├── Role Guard (authorization)
  └── Pydantic Validation (input validation)
  │
  ▼
Services (Business Logic)
  │
  ├── auth_service.py
  ├── user_service.py
  ├── record_service.py
  └── dashboard_service.py
  │
  ▼
SQLAlchemy ORM (Async)
  │
  ▼
PostgreSQL (Docker Container)
  │
  ├── users
  ├── financial_records
  └── refresh_tokens
```

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Framework | FastAPI | Async, auto Swagger docs, fast |
| Database | PostgreSQL | Multi-user concurrent reads, ACID compliant |
| ORM | SQLAlchemy 2.0 | Async support, type-safe models |
| Driver | asyncpg | Async PostgreSQL driver |
| Migrations | Alembic | Version controlled schema changes |
| Auth | JWT (python-jose) | Stateless, scalable authentication |
| Validation | Pydantic v2 | Request/response validation |
| Password | bcrypt (passlib) | Industry standard hashing |

---

## Project Structure
```
zorvyn_backend/
├── app/
│   ├── core/
│   │   ├── config.py           # Environment configuration via Pydantic Settings
│   │   ├── security.py         # JWT creation, verification and password hashing
│   │   └── dependencies.py     # Auth guards and role enforcement middleware
│   ├── models/
│   │   ├── user.py             # User SQLAlchemy model
│   │   ├── record.py           # FinancialRecord SQLAlchemy model
│   │   └── refresh_token.py    # RefreshToken SQLAlchemy model
│   ├── schemas/
│   │   ├── user.py             # User request/response Pydantic schemas
│   │   ├── record.py           # Record request/response Pydantic schemas
│   │   └── token.py            # Token response schema
│   ├── routers/
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── users.py            # User management endpoints
│   │   ├── records.py          # Financial record endpoints
│   │   └── dashboard.py        # Analytics and summary endpoints
│   ├── services/
│   │   ├── auth_service.py     # Auth business logic
│   │   ├── user_service.py     # User management business logic
│   │   ├── record_service.py   # Record CRUD business logic
│   │   └── dashboard_service.py # Aggregation and analytics logic
│   ├── database.py             # Async SQLAlchemy engine, session and base
│   └── main.py                 # FastAPI app entry point
├── alembic/                    # Database migration files
├── seed.py                     # Creates initial admin user in DB
├── docker-compose.yml          # PostgreSQL container configuration
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md
```

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Docker and Docker Compose

### 1. Clone the repository
```bash
git clone <https://github.com/KedarJevargi/zorvyn_backend.git>
```

### 2. Create virtual environment

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your values
```

### 5. Start PostgreSQL
```bash
docker-compose up -d
```

### 6. Run migrations
```bash
alembic upgrade head
```

### 7. Seed admin user
```bash
python seed.py
```

### 8. Start the server
```bash
uvicorn app.main:app --reload
```

### 9. Access API docs
```
http://localhost:8000/docs
```

### Default Admin Credentials
```
Email:    admin@zorvyn.com
Password: admin123
```

---

## Database Schema

### Users
| Column | Type | Constraints |
|---|---|---|
| id | Integer | Primary Key |
| name | String(100) | Not Null |
| email | String(100) | Unique, Not Null, Indexed |
| hashed_password | String(255) | Not Null |
| role | Enum(viewer, analyst, admin) | Default: viewer, Indexed |
| is_active | Boolean | Default: True, Indexed |
| is_deleted | Boolean | Default: False, Indexed |
| created_at | DateTime(timezone) | Auto set on insert |
| updated_at | DateTime(timezone) | Auto set on update |

### FinancialRecord
| Column | Type | Constraints |
|---|---|---|
| id | Integer | Primary Key |
| user_id | Integer | FK → users.id (RESTRICT), Indexed |
| amount | Numeric(10,2) | Not Null, >= 0 |
| type | Enum(income, expense) | Not Null, Indexed |
| category | String(50) | Not Null, Indexed, Lowercase |
| notes | String(255) | Nullable |
| date | DateTime(timezone) | Not Null, Indexed |
| is_deleted | Boolean | Default: False, Indexed |
| deleted_at | DateTime(timezone) | Nullable |
| created_at | DateTime(timezone) | Auto set on insert |
| updated_at | DateTime(timezone) | Auto set on update |

### RefreshToken
| Column | Type | Constraints |
|---|---|---|
| id | Integer | Primary Key |
| user_id | Integer | FK → users.id (CASCADE), Indexed |
| token | String(512) | Unique, Not Null, Indexed |
| expires_at | DateTime(timezone) | Not Null |
| is_revoked | Boolean | Default: False, Indexed |
| created_at | DateTime(timezone) | Auto set on insert |

### Composite Indexes on FinancialRecord
```
idx_user_date     → (user_id, date)
idx_user_type     → (user_id, type)
idx_user_category → (user_id, category)
```

### DB Constraints
```
check_amount_positive         → amount >= 0
check_soft_delete_consistency → is_deleted and deleted_at must be consistent
```

### Relationships
```
User (1) ──────────── (many) FinancialRecord
User (1) ──────────── (many) RefreshToken
```

| Relationship | Strategy | Reason |
|---|---|---|
| User → FinancialRecord | `ondelete="RESTRICT"` | Prevents deleting a user who has records. Financial history must be preserved. |
| User → RefreshToken | Hard delete on soft delete | Tokens have no audit value. Cleaned up immediately when user is removed. |

---

## Role Permission Matrix

| Endpoint | Viewer | Analyst | Admin |
|---|---|---|---|
| POST /auth/register | ✅ | ✅ | ✅ |
| POST /auth/login | ✅ | ✅ | ✅ |
| POST /auth/refresh | ✅ | ✅ | ✅ |
| POST /auth/logout | ✅ | ✅ | ✅ |
| GET /auth/me | ✅ | ✅ | ✅ |
| GET /users | ❌ | ❌ | ✅ |
| GET /users/{id} | ❌ | ❌ | ✅ |
| PATCH /users/{id}/role | ❌ | ❌ | ✅ |
| PATCH /users/{id}/status | ❌ | ❌ | ✅ |
| DELETE /users/{id} | ❌ | ❌ | ✅ |
| PATCH /users/{id}/restore | ❌ | ❌ | ✅ |
| POST /records | ❌ | ❌ | ✅ |
| GET /records | ❌ | ✅ | ✅ |
| GET /records/{id} | ❌ | ✅ | ✅ |
| PATCH /records/{id} | ❌ | ❌ | ✅ |
| DELETE /records/{id} | ❌ | ❌ | ✅ |
| PATCH /records/{id}/restore | ❌ | ❌ | ✅ |
| GET /dashboard/* | ✅ | ✅ | ✅ |

---

## API Endpoints

### Auth
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | /auth/register | Register new user (viewer by default) | Public |
| POST | /auth/login | Login, returns access token + sets HttpOnly refresh cookie | Public |
| POST | /auth/refresh | Get new access token using refresh cookie | Public |
| POST | /auth/logout | Revoke refresh token and clear cookie | Public |
| GET | /auth/me | Get current user profile | Any |

### Users
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | /users | List users with optional filters | Admin |
| GET | /users/{id} | Get single user by ID | Admin |
| PATCH | /users/{id}/role | Update user role | Admin |
| PATCH | /users/{id}/status | Activate or deactivate user | Admin |
| DELETE | /users/{id} | Soft delete user | Admin |
| PATCH | /users/{id}/restore | Restore soft deleted user | Admin |

### Records
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | /records | Create financial record | Admin |
| GET | /records | List records with filters, search and pagination | Analyst+ |
| GET | /records/{id} | Get single record | Analyst+ |
| PATCH | /records/{id} | Update record | Admin |
| DELETE | /records/{id} | Soft delete record | Admin |
| PATCH | /records/{id}/restore | Restore soft deleted record | Admin |

#### Record Query Parameters
```
GET /records?type=income&category=salary&date_from=2026-01-01T00:00:00Z&date_to=2026-03-31T00:00:00Z&search=bonus&page=1&limit=10
```

### Dashboard
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | /dashboard/summary | Total income, expenses, net balance | Any |
| GET | /dashboard/categories | Category wise totals grouped by type | Any |
| GET | /dashboard/trends | Monthly or weekly income/expense trends | Any |
| GET | /dashboard/recent | Most recent financial records | Any |

All dashboard endpoints support optional `date_from` and `date_to` query parameters.

#### Dashboard Query Parameters
```
GET /dashboard/summary?date_from=2026-01-01T00:00:00Z&date_to=2026-03-31T00:00:00Z
GET /dashboard/trends?period=monthly
GET /dashboard/trends?period=weekly
GET /dashboard/recent?limit=5
```

---

## Request / Response Examples

### Register
```json
POST /auth/register

Request:
{
  "name": "Rahul Sharma",
  "email": "rahul@example.com",
  "password": "securepassword"
}

Response 201:
{
  "id": 3,
  "name": "Rahul Sharma",
  "email": "rahul@example.com",
  "role": "viewer",
  "is_active": true,
  "is_deleted": false,
  "created_at": "2026-04-03T10:00:00Z",
  "updated_at": "2026-04-03T10:00:00Z"
}
```

### Login
```json
POST /auth/login

Request:
{
  "email": "admin@zorvyn.com",
  "password": "admin123"
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```
> refresh_token is set as HttpOnly cookie — not visible in response body

### Create Record
```json
POST /records
Authorization: Bearer <access_token>

Request:
{
  "amount": 50000,
  "type": "income",
  "category": "salary",
  "notes": "Monthly salary March 2026",
  "date": "2026-03-01T00:00:00Z"
}

Response 201:
{
  "id": 1,
  "user_id": 2,
  "amount": 50000.00,
  "type": "income",
  "category": "salary",
  "notes": "Monthly salary March 2026",
  "date": "2026-03-01T00:00:00Z",
  "is_deleted": false,
  "created_at": "2026-04-03T10:00:00Z",
  "updated_at": "2026-04-03T10:00:00Z"
}
```

### Dashboard Summary
```json
GET /dashboard/summary?date_from=2026-01-01T00:00:00Z&date_to=2026-03-31T00:00:00Z
Authorization: Bearer <access_token>

Response 200:
{
  "total_income": 85000.00,
  "total_expenses": 11500.00,
  "net_balance": 73500.00
}
```

### Error Responses
```json
POST /records (as Analyst)
Response 403:
{
  "detail": "Insufficient permissions"
}

POST /auth/login (wrong password)
Response 401:
{
  "detail": "Invalid credentials"
}
```

> For complete interactive documentation with all request/response schemas visit Swagger UI at `http://localhost:8000/docs`

### Dashboard Summary
```
GET /dashboard/summary?date_from=2026-01-01T00:00:00Z&date_to=2026-03-31T00:00:00Z
Authorization: Bearer <access_token>

Response 200:
{
  "total_income": 85000.00,
  "total_expenses": 11500.00,
  "net_balance": 73500.00
}
```

### Error Response Example
```
POST /records (as Analyst)
Response 403:
{
  "detail": "Insufficient permissions"
}

POST /auth/login (wrong password)
Response 401:
{
  "detail": "Invalid credentials"
}
```

---

## Validation and Error Handling

- **Pydantic v2** validates all request bodies — invalid input returns `422 Unprocessable Entity` with field-level errors
- **EmailStr** validates email format on register and login
- **Enum validation** on `type` (income/expense) and `role` (viewer/analyst/admin)
- **Amount validator** rejects values <= 0
- **Category normalizer** strips whitespace and lowercases on input
- **DB constraints** enforce `amount >= 0` and soft delete consistency at database level
- **Consistent HTTP status codes:**

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 204 | No content (delete/logout) |
| 401 | Not authenticated |
| 403 | Not authorized (wrong role) |
| 404 | Resource not found |
| 422 | Validation error |

---

## Design Decisions

**Public registration with admin role assignment**
Anyone can register via `POST /auth/register` and gets `viewer` role by default. Admin then upgrades roles via `PATCH /users/{id}/role`. First admin is created via `seed.py` directly in the DB — avoids "first user becomes admin" race condition security risk.

**Admin-only record creation**
Designed for centralized finance systems where data entry is controlled and audited. Only trusted admins can create, update, or delete financial records. Analysts and Viewers are consumers of data, not producers.

**Read-heavy system design**
The system is read-biased — 1-2 admins write occasionally while many Viewers and Analysts constantly read dashboards and records. PostgreSQL was chosen over SQLite for its ability to handle concurrent connections cleanly.

**Database Connection Pool Configuration**

| Parameter | Value | Reason |
|---|---|---|
| `pool_size` | 12 | Handles consistent dashboard reads without overloading DB |
| `max_overflow` | 18 | Total max 30 connections — covers bursts from multiple users hitting dashboard simultaneously |
| `pool_timeout` | 20s | Fail fast under overload — prevents request pile-up and protects UX |
| `pool_recycle` | 1200s | Recycle connections every 20 min — avoids idle disconnects and stale sessions |
| `pool_pre_ping` | True | Verifies connection health before use — prevents stale connection errors |

> Dashboards cause bursty traffic, not constant load. `max_overflow=18` absorbs those bursts while `pool_size=12` handles the baseline.

**Soft delete over hard delete**
Financial records must be preserved for audit trails and historical analysis. `ondelete="RESTRICT"` on `FinancialRecord.user_id` prevents hard deleting users who have records at the DB level. Soft delete is the only safe option.

| Entity | Strategy | Reason |
|---|---|---|
| User | Soft delete | Preserves `user_id` FK reference on records |
| FinancialRecord | Soft delete + `deleted_at` timestamp | Audit trail, recovery, accidental delete protection |
| RefreshToken | Hard delete | No audit value, temporary by nature |

**Numeric(10,2) for amount**
`float` has rounding errors for financial data. `Decimal` + `Numeric(10,2)` is the industry standard for monetary values.

**One refresh token per user**
Multiple logins accumulate tokens indefinitely. On each login, old tokens are hard deleted and a new one created — keeping the `refresh_tokens` table clean.

**HttpOnly cookie for refresh token**
HttpOnly cookies cannot be accessed by JavaScript, protecting against XSS attacks. Access token remains in response body for frontend use.

**Composite indexes on FinancialRecord**
Dashboard queries filter by `user_id + date`, `user_id + type`, `user_id + category` frequently. Composite indexes on these combinations are more efficient than single column indexes for multi-column queries.

**Category as free text normalized to lowercase**
Category is open-ended. Normalized to lowercase on input via Pydantic validator to ensure consistent filtering (`Food` and `food` are treated the same).

**HTTPBearer over OAuth2PasswordBearer**
Our login endpoint accepts JSON body. `OAuth2PasswordBearer` expects form data which conflicts. `HTTPBearer` works cleanly with JSON-based auth.

**REST over GraphQL**
Data model is simple and relational, not deeply nested or multi-client. REST maps naturally to our resources with no over-fetching concerns at this scope.

---

## Scalability Considerations

### Current Strengths
- Async FastAPI enables high concurrency with non-blocking I/O
- PostgreSQL supports multi-user workloads with ACID guarantees
- Connection pooling improves performance under load
- Composite indexes optimize frequent dashboard queries
- Pagination prevents large response payloads

### Current Limitations
- No caching layer — every request hits the DB directly
- Single database instance — no read replicas
- No rate limiting — vulnerable to abuse
- No background jobs — all work is synchronous per request

### Future Improvements
- Redis caching for dashboard aggregation endpoints
- Horizontal scaling with multiple FastAPI instances behind a load balancer
- Read replicas for scaling read-heavy dashboard queries
- Rate limiting with slowapi + Redis
- Background workers (Celery) for heavy computations

---

## Tradeoffs

| Decision | Tradeoff |
|---|---|
| Integer ID | Simple but predictable. UUID would prevent ID enumeration attacks |
| ILIKE search on notes | Simple substring search. Production: Full Text Search or Elasticsearch |
| No Redis caching on dashboard | Dashboard queries hit DB every request. Production: cache with Redis |
| No rate limiting | Keeps scope manageable. Production: implement with slowapi + Redis |
| No unit tests | Time constraint. Future: pytest with async test client |
| CORS allow all origins | Development convenience. Production: restrict to specific domains |
| No forgot/reset password | Requires email service (SMTP/SendGrid). Future enhancement |
| `func.date_trunc` PostgreSQL specific | Trends query won't work on MySQL/SQLite. Acceptable tradeoff |
| `secure=False` on refresh cookie | Local dev only. Set `secure=True` in production with HTTPS |

---

## Assumptions


- Category is free-text — no predefined list, normalized to lowercase
- Soft deleted users cannot login even with a valid JWT token
- Dashboard endpoints are accessible to all authenticated users including Viewers
- One refresh token per user at all times — old tokens deleted on new login

---

## Optional Features Implemented

| Feature | Status |
|---|---|
| JWT Authentication + HttpOnly refresh cookie | ✅ |
| Pagination on record listing (max 100) | ✅ |
| Search on notes field (PostgreSQL ILIKE) | ✅ |
| Soft delete with restore for users and records | ✅ |
| Auto-generated Swagger + ReDoc documentation | ✅ |
| Rate limiting | ❌ Future enhancement |
| Unit / integration tests | ❌ Future enhancement |

---

## Future Enhancements

- Forgot/reset password via email (SendGrid)
- Rate limiting with slowapi + Redis
- Unit and integration tests with pytest
- Hard delete option for users with no financial records
- CSV bulk import for financial records
- UUID primary keys to prevent ID enumeration
- Redis caching for dashboard aggregation queries
- Full Text Search for notes field
- Docker Compose for full stack deployment
- Integrate AI-powered insights on dashboard — use an LLM to automatically summarize spending patterns, flag unusual transactions, or suggest budget optimizations based on financial record trends
- Add anomaly detection for financial records using ML to identify suspicious entries
- Natural language query support — allow analysts to ask questions like "show me all expenses above 10000 in Q1" instead of manually building filters

---

## API Documentation



Interactive Swagger UI: `http://localhost:8000/docs`

ReDoc: `http://localhost:8000/redoc`