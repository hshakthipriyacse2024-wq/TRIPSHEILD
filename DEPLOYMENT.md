# TripShield AI — Deployment Guide

## Local Development

### Prerequisites
- Python 3.11+ ([Download](https://python.org))
- Node.js 18+ ([Download](https://nodejs.org))
- Git ([Download](https://git-scm.com))

### Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example .env

# Start the server
uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`
API docs at `http://localhost:8000/docs` (Swagger UI)
Alternative docs at `http://localhost:8000/redoc`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file (or set env var)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Start development server
npm run dev
```

Frontend runs at `http://localhost:3000`

---

## Docker Deployment

### Prerequisites
- Docker ([Download](https://docker.com))
- Docker Compose

### Quick Start

```bash
# From project root
cp .env.example .env
# Edit .env with your settings (change SECRET_KEY!)

# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### Services
| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |

### Docker Commands

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build

# Remove volumes (reset database)
docker-compose down -v
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///./tripshield.db` | Database connection string |
| `SECRET_KEY` | Yes | (dev default) | JWT signing key — **CHANGE IN PRODUCTION** |
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` | Token expiry (24 hours) |
| `CORS_ORIGINS` | No | `["http://localhost:3000"]` | Allowed CORS origins |
| `AI_PROVIDER` | No | `mock` | AI provider: mock, gemini, openai |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000/api/v1` | Backend API URL for frontend |

---

## Database

### Development (SQLite)
No setup needed — SQLite database file is created automatically on first run.

### Production (PostgreSQL)

```bash
# Install PostgreSQL
# Create database
createdb tripshield

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/tripshield
```

The SQLAlchemy models work with both SQLite and PostgreSQL without code changes.

---

## Running Tests

### Backend Tests
```bash
cd backend
pip install pytest httpx
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## Production Deployment Checklist

- [ ] Change `SECRET_KEY` to a cryptographically random value
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `CORS_ORIGINS` to your actual frontend domain
- [ ] Enable HTTPS (use a reverse proxy like nginx or cloud load balancer)
- [ ] Set `LOG_LEVEL` to `WARNING` or `ERROR`
- [ ] Configure proper rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure database backups
- [ ] Review and restrict CORS settings
- [ ] Use environment-specific configuration
- [ ] Set up CI/CD pipeline

---

## Cloud Deployment Options

### Vercel (Frontend) + Railway (Backend)
1. Deploy frontend to Vercel (auto-detects Next.js)
2. Deploy backend to Railway with Python buildpack
3. Set environment variables in each platform

### AWS
1. Use ECS/Fargate with Docker containers
2. RDS for PostgreSQL
3. CloudFront for frontend CDN
4. Application Load Balancer

### Google Cloud Platform
1. Cloud Run for containerized services
2. Cloud SQL for PostgreSQL
3. Cloud CDN for frontend

### Render
1. Web Service for backend (Python)
2. Static Site for frontend (Next.js)
3. PostgreSQL database add-on
