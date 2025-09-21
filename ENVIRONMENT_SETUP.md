# Environment Setup Guide

Comprehensive guide for configuring the Feature Voting System across different environments. This document covers backend API configuration, iOS app settings, and deployment considerations.

## 📋 Overview

The system supports multiple environments with different configurations:
- **Development**: Local development with debug features
- **Staging**: Pre-production testing environment
- **Production**: Live production deployment

## 🔧 Backend Environment Configuration

### Environment Variables

The backend uses environment variables for configuration. These are loaded from `.env` files or system environment variables.

#### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost/db` | ✅ |
| `SECRET_KEY` | Application secret for security | `super-secret-key-here` | ✅ |

#### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ALGORITHM` | JWT algorithm (future use) | `HS256` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` | `1440` |
| `DEBUG` | Enable debug mode | `False` | `True` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |
| `CORS_ORIGINS` | Allowed CORS origins | `["*"]` | `["https://app.example.com"]` |

### Environment Files

#### Development (.env)
```bash
# Database Configuration
DATABASE_URL=postgresql://feature_voting_user:secure_password@localhost/feature_voting_db

# Security
SECRET_KEY=development-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Debug Settings
DEBUG=True
LOG_LEVEL=DEBUG

# CORS (allow all origins in development)
CORS_ORIGINS=["*"]

# Optional: Database Pool Settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

#### Staging (.env.staging)
```bash
# Database Configuration
DATABASE_URL=postgresql://staging_user:staging_password@staging-db.example.com/feature_voting_staging

# Security
SECRET_KEY=staging-secret-key-different-from-prod
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# Debug Settings
DEBUG=False
LOG_LEVEL=INFO

# CORS (specific domains only)
CORS_ORIGINS=["https://staging.example.com", "https://staging-admin.example.com"]

# Performance
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

#### Production (.env.production)
```bash
# Database Configuration
DATABASE_URL=postgresql://prod_user:ultra_secure_password@prod-db.example.com/feature_voting_prod

# Security (use strong, unique values)
SECRET_KEY=production-secret-key-super-secure-change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Production Settings
DEBUG=False
LOG_LEVEL=WARNING

# CORS (production domains only)
CORS_ORIGINS=["https://app.example.com", "https://admin.example.com"]

# Performance
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=60

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### Database URL Format

The `DATABASE_URL` follows the PostgreSQL connection string format:

```
postgresql://[user[:password]@][host][:port][/database][?param1=value1&...]
```

#### Examples
```bash
# Local development
DATABASE_URL=postgresql://username:password@localhost:5432/feature_voting_db

# Remote database
DATABASE_URL=postgresql://user:pass@db.example.com:5432/feature_voting_prod

# With connection parameters
DATABASE_URL=postgresql://user:pass@localhost/db?sslmode=require&connect_timeout=10

# Using environment variables in URL
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}
```

### Security Best Practices

#### Secret Key Generation
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using OpenSSL
openssl rand -base64 32
```

#### Environment Variable Security
1. **Never commit .env files**: Add to `.gitignore`
2. **Use different keys per environment**: Never reuse secret keys
3. **Rotate keys regularly**: Change keys periodically
4. **Use environment variable injection**: For containerized deployments

## 📱 iOS Environment Configuration

### Environment Enum

The iOS app uses a Swift enum for environment configuration in `Config/Environment.swift`:

```swift
enum AppEnvironment {
    case development
    case staging
    case production

    static var current: AppEnvironment {
        #if DEBUG
        return .development
        #elseif STAGING
        return .staging
        #else
        return .production
        #endif
    }
}
```

### Development Configuration

```swift
case .development:
    // API Configuration
    apiBaseURL = "http://localhost:8000"
    networkTimeout = 30.0
    isDebugMode = true

    // Features
    enableVerboseLogging = true
    enableNetworkMocking = false
    enableUIDebugging = true
```

### Staging Configuration

```swift
case .staging:
    // API Configuration
    apiBaseURL = "https://staging-api.example.com"
    networkTimeout = 15.0
    isDebugMode = true

    // Features
    enableVerboseLogging = true
    enableNetworkMocking = false
    enableUIDebugging = false
```

### Production Configuration

```swift
case .production:
    // API Configuration
    apiBaseURL = "https://api.example.com"
    networkTimeout = 15.0
    isDebugMode = false

    // Features
    enableVerboseLogging = false
    enableNetworkMocking = false
    enableUIDebugging = false
```

### Build Configurations

#### Xcode Scheme Setup

1. **Debug Scheme** (Development)
   - Swift Compilation Flags: `-DDEBUG`
   - Preprocessor Macros: `DEBUG=1`

2. **Staging Scheme** (Staging)
   - Swift Compilation Flags: `-DSTAGING`
   - Preprocessor Macros: `STAGING=1`

3. **Release Scheme** (Production)
   - Swift Compilation Flags: (none)
   - Optimization Level: `-O`

#### Info.plist Configuration

```xml
<!-- Development -->
<key>CFBundleDisplayName</key>
<string>FeatureVoting Dev</string>
<key>CFBundleIdentifier</key>
<string>com.example.featurevoting.dev</string>

<!-- Staging -->
<key>CFBundleDisplayName</key>
<string>FeatureVoting Staging</string>
<key>CFBundleIdentifier</key>
<string>com.example.featurevoting.staging</string>

<!-- Production -->
<key>CFBundleDisplayName</key>
<string>FeatureVoting</string>
<key>CFBundleIdentifier</key>
<string>com.example.featurevoting</string>
```

## 🚀 Deployment Configuration

### Docker Environment

#### Backend Dockerfile.env
```bash
# Use for Docker deployments
DATABASE_URL=${DATABASE_URL}
SECRET_KEY=${SECRET_KEY}
DEBUG=False
LOG_LEVEL=INFO
```

#### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/feature_voting
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=feature_voting
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Cloud Deployment

#### Heroku Configuration
```bash
# Set environment variables in Heroku
heroku config:set DATABASE_URL="postgresql://..." --app your-app-name
heroku config:set SECRET_KEY="your-secret-key" --app your-app-name
heroku config:set DEBUG=False --app your-app-name
```

#### AWS ECS Configuration
```json
{
  "environment": [
    {
      "name": "DATABASE_URL",
      "value": "postgresql://user:pass@rds-endpoint:5432/db"
    },
    {
      "name": "SECRET_KEY",
      "valueFrom": "arn:aws:ssm:region:account:parameter/app/secret-key"
    }
  ]
}
```

#### Kubernetes ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DEBUG: "False"
  LOG_LEVEL: "INFO"
  ALGORITHM: "HS256"

---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  DATABASE_URL: "postgresql://..."
  SECRET_KEY: "..."
```

## 🔒 Security Configuration

### SSL/TLS Configuration

#### Backend HTTPS
```python
# For production deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="/path/to/keyfile.pem",
        ssl_certfile="/path/to/certfile.pem"
    )
```

#### iOS App Transport Security
```xml
<!-- Info.plist -->
<key>NSAppTransportSecurity</key>
<dict>
    <!-- Allow HTTP for development -->
    <key>NSAllowsArbitraryLoads</key>
    <false/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>localhost</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>
```

### Database Security

#### PostgreSQL Configuration
```bash
# postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'

# Connection encryption
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

## 🧪 Testing Environments

### Test Database
```bash
# Separate test database
TEST_DATABASE_URL=postgresql://test_user:test_pass@localhost/feature_voting_test

# In-memory testing (for CI)
TEST_DATABASE_URL=sqlite:///:memory:
```

### iOS Testing Configuration
```swift
#if TESTING
extension AppEnvironment {
    static var testing: AppEnvironment {
        // Use mock API for testing
        apiBaseURL = "http://mock-api.test"
        networkTimeout = 5.0
        enableNetworkMocking = true
    }
}
#endif
```

### CI/CD Environment Variables
```yaml
# GitHub Actions
env:
  DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
  SECRET_KEY: test-secret-key
  DEBUG: True
  LOG_LEVEL: DEBUG
```

## 🔍 Environment Validation

### Backend Validation Script
```python
# scripts/validate_env.py
import os
from urllib.parse import urlparse

def validate_environment():
    """Validate required environment variables."""
    required = ['DATABASE_URL', 'SECRET_KEY']
    missing = [var for var in required if not os.getenv(var)]

    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")

    # Validate DATABASE_URL format
    db_url = os.getenv('DATABASE_URL')
    parsed = urlparse(db_url)
    if not all([parsed.scheme, parsed.hostname, parsed.path]):
        raise ValueError("Invalid DATABASE_URL format")

    print("✅ Environment validation passed")

if __name__ == "__main__":
    validate_environment()
```

### iOS Environment Validation
```swift
// Config/EnvironmentValidator.swift
struct EnvironmentValidator {
    static func validate() {
        let config = AppConfig.environment

        // Validate API URL
        guard URL(string: config.apiBaseURL) != nil else {
            fatalError("Invalid API base URL: \(config.apiBaseURL)")
        }

        // Validate timeout
        guard config.networkTimeout > 0 else {
            fatalError("Network timeout must be positive")
        }

        print("✅ iOS environment validation passed")
    }
}
```

## 📊 Environment Monitoring

### Health Check Endpoints

#### Backend Health Check
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "debug": os.getenv("DEBUG", "False").lower() == "true",
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### Environment Info Endpoint
```python
@app.get("/info")
async def app_info():
    return {
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": "connected" if database_is_connected() else "disconnected",
        "features": {
            "debug": os.getenv("DEBUG", "False").lower() == "true",
            "cors_enabled": len(os.getenv("CORS_ORIGINS", "").split(",")) > 0
        }
    }
```

### iOS Environment Info
```swift
struct EnvironmentInfo: Codable {
    let environment: String
    let apiBaseURL: String
    let debugMode: Bool
    let version: String

    static var current: EnvironmentInfo {
        EnvironmentInfo(
            environment: AppEnvironment.current.name,
            apiBaseURL: AppConfig.apiBaseURL,
            debugMode: AppConfig.isDebugMode,
            version: Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "unknown"
        )
    }
}
```

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Test connection manually
psql $DATABASE_URL

# Check connection pool settings
echo "Current pool size: $DB_POOL_SIZE"
```

#### iOS API Connection Issues
```swift
// Debug network requests
func debugNetworkRequest(_ request: URLRequest) {
    #if DEBUG
    print("🌐 Request URL: \(request.url?.absoluteString ?? "unknown")")
    print("🌐 Headers: \(request.allHTTPHeaderFields ?? [:])")
    #endif
}
```

#### Environment Variable Loading
```python
# Check if .env file is loaded
from dotenv import load_dotenv
load_dotenv()
print(f"DATABASE_URL loaded: {bool(os.getenv('DATABASE_URL'))}")
```

### Configuration Validation Checklist

- [ ] All required environment variables are set
- [ ] Database connection is working
- [ ] Secret keys are unique per environment
- [ ] CORS origins are properly configured
- [ ] SSL/TLS is enabled in production
- [ ] iOS app has correct API endpoints
- [ ] Build configurations match environments
- [ ] Log levels are appropriate for environment

---

For complete project documentation, see the [main README.md](README.md).