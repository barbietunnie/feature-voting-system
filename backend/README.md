# Feature Voting System - Backend

FastAPI-based backend for the Feature Voting System with PostgreSQL database, comprehensive error handling, and automatic API documentation.

## 🏗️ Backend Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   SQLAlchemy    │    │   PostgreSQL    │
│   Routes        │────┤   Models        │────┤   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │
        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐
│   Pydantic      │    │   Alembic       │
│   Schemas       │    │   Migrations    │
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Setup

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### 1. Environment Setup
```bash
# Clone and navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Install PostgreSQL (macOS with Homebrew)
brew install postgresql
brew services start postgresql

# Create database and user
psql postgres
CREATE DATABASE feature_voting_db;
CREATE USER feature_voting_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE feature_voting_db TO feature_voting_user;
\q
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your database credentials
nano .env
```

Required environment variables:
```bash
DATABASE_URL=postgresql://feature_voting_user:your_secure_password@localhost/feature_voting_db
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Database Migration
```bash
# Run database migrations
alembic upgrade head
```

### 5. Start Development Server
```bash
# Start the server
uvicorn app.main:app --reload

# Or using the run script
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
backend/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── requirements-test.txt       # Test dependencies
├── .env.example               # Environment template
├── alembic.ini               # Alembic configuration
├── pytest.ini               # Pytest configuration
├── run_tests.py              # Test runner script
├── alembic/                  # Database migrations
│   ├── env.py               # Alembic environment
│   └── versions/            # Migration files
│       └── 001_initial_schema.py
├── app/                      # Main application
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication logic
│   │   ├── database.py      # Database configuration
│   │   └── exceptions.py    # Exception handlers
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py          # User model
│   │   ├── feature.py       # Feature model
│   │   └── vote.py          # Vote model
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py          # User schemas
│   │   ├── feature.py       # Feature schemas
│   │   ├── vote.py          # Vote schemas
│   │   └── pagination.py    # Pagination schemas
│   └── routes/              # API routes
│       ├── __init__.py
│       ├── users.py         # User endpoints
│       └── features.py      # Feature and voting endpoints
└── tests/                   # Test suites
    ├── __init__.py
    ├── conftest.py          # Test configuration
    ├── factories.py         # Test data factories
    ├── test_users.py        # User tests
    ├── test_features.py     # Feature tests
    ├── test_voting.py       # Voting tests
    ├── test_database_constraints.py
    ├── test_integration.py
    └── test_exception_handling.py
```

## 🛠️ Development

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_users.py

# Run with verbose output
python -m pytest -v

# Generate HTML coverage report
python -m pytest --cov=app --cov-report=html
```

### Database Operations

#### Creating Migrations
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column to features"

# Create empty migration
alembic revision -m "Custom migration"
```

#### Applying Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade abc123

# Show current revision
alembic current

# Show migration history
alembic history
```

#### Rolling Back
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

### API Development

#### Adding New Endpoints
1. Create/update models in `app/models/`
2. Create/update schemas in `app/schemas/`
3. Add routes in `app/routes/`
4. Update `app/main.py` to include new routes
5. Write tests in `tests/`

#### Error Handling
The application includes comprehensive error handling:
- **Custom Exceptions**: Defined in `app/core/exceptions.py`
- **HTTP Status Codes**: Proper status codes for different error types
- **Structured Responses**: Consistent error response format
- **Logging**: Automatic error logging for debugging

#### Authentication
Current implementation uses a simple header-based system:
- Users identified by `X-User-ID` header
- For production, replace with JWT or OAuth2

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | ✅ |
| `SECRET_KEY` | Application secret key | - | ✅ |
| `ALGORITHM` | JWT algorithm (future use) | HS256 | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 | ❌ |

### Database Configuration
```python
# In app/core/database.py
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## 🧪 Testing Strategy

### Test Coverage
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Database Tests**: Data integrity and constraints
- **Exception Tests**: Error handling validation

### Test Data
Tests use factories (`tests/factories.py`) for generating test data:
```python
from tests.factories import UserFactory, FeatureFactory

# Create test user
user = UserFactory()

# Create test feature
feature = FeatureFactory(author_id=user.id)
```

### Running Specific Tests
```bash
# Test user functionality
python -m pytest tests/test_users.py

# Test with specific pattern
python -m pytest -k "test_create"

# Test with markers (if defined)
python -m pytest -m "unit"
```

## 📊 API Endpoints

### Quick Reference
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/api/users` | Create user |
| GET | `/api/users` | List users |
| GET | `/api/users/{id}` | Get user |
| POST | `/api/features` | Create feature |
| GET | `/api/features` | List features (paginated) |
| GET | `/api/features/{id}` | Get feature |
| PUT | `/api/features/{id}` | Update feature |
| POST | `/api/features/{id}/vote` | Vote for feature |
| DELETE | `/api/features/{id}/vote` | Remove vote |

For complete API documentation, see [API_DOCUMENTATION.md](../API_DOCUMENTATION.md)

## 🚀 Production Deployment

### Using Gunicorn
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Environment Setup
```bash
# Production environment variables
export DATABASE_URL="postgresql://user:pass@prod-db:5432/feature_voting"
export SECRET_KEY="super-secure-production-key"
export PYTHONPATH="/app"
```

## 🔍 Monitoring and Logging

### Health Checks
The `/health` endpoint provides basic health information:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### Logging Configuration
Logs are configured in `app/main.py`:
- **Development**: Console output with DEBUG level
- **Production**: File output with INFO level

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Check database exists
psql -l | grep feature_voting

# Test connection
psql $DATABASE_URL
```

#### Migration Issues
```bash
# Reset migrations (development only!)
alembic downgrade base
alembic upgrade head

# Check migration status
alembic current
alembic history
```

#### Import Errors
```bash
# Check Python path
echo $PYTHONPATH

# Install in development mode
pip install -e .
```

### Performance Optimization
- **Database Indexing**: Ensure proper indexes on frequently queried columns
- **Query Optimization**: Use SQLAlchemy query profiling
- **Connection Pooling**: Configure appropriate pool size
- **Caching**: Consider Redis for frequently accessed data

## 🤝 Contributing

1. Follow PEP 8 style guidelines
2. Write tests for new functionality
3. Update documentation
4. Use meaningful commit messages
5. Ensure all tests pass before submitting PR

### Code Style
```bash
# Format code with black
black app/ tests/

# Check with flake8
flake8 app/ tests/

# Type checking with mypy
mypy app/
```

---

For complete project documentation, see the [main README.md](../README.md).