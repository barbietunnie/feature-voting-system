# Feature Voting System

A full-stack feature voting application that allows users to propose, vote on, and track feature requests. Built with FastAPI backend and SwiftUI iOS frontend.

## 🏗️ Architecture Overview

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐    PostgreSQL    ┌─────────────────┐
│   iOS App       │◄────────────────┤   FastAPI       │◄─────────────────┤   Database      │
│   (SwiftUI)     │                 │   Backend       │                  │                 │
└─────────────────┘                 └─────────────────┘                  └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Backend**: Python 3.11+, PostgreSQL 12+
- **iOS**: Xcode 15+, macOS 13+

### Backend Setup (5 minutes)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
alembic upgrade head
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000

### iOS Setup (2 minutes)
```bash
cd mobile
open FeatureVoting.xcodeproj
# Build and run in Xcode (⌘+R)
```

## 📱 Features

### Core Functionality
- 👤 **User Management**: Create and select user profiles
- 💡 **Feature Proposals**: Submit feature requests with titles and descriptions
- 🗳️ **Voting System**: Vote for features you want to see implemented
- 📊 **Vote Tracking**: Real-time vote counts and feature rankings
- 📱 **Mobile-First**: Native iOS experience with SwiftUI

### Technical Features
- ✅ **Comprehensive Error Handling**: User-friendly error messages
- 🔄 **Real-time Updates**: Automatic refresh and live vote updates
- 📄 **Pagination**: Efficient loading of large feature lists
- 🔒 **Input Validation**: Client and server-side validation
- 🌐 **Network Resilience**: Graceful handling of connection issues

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Relational database
- **Alembic** - Database migration tool
- **Pydantic** - Data validation using Python type hints

### iOS
- **SwiftUI** - Declarative UI framework
- **Combine** - Reactive programming framework
- **URLSession** - Network requests
- **MVVM Architecture** - Clean separation of concerns

## 📁 Project Structure

```
feature-voting-system/
├── README.md                    # This file
├── API_DOCUMENTATION.md         # Complete API documentation
├── DATABASE_SCHEMA.md          # Database schema and relationships
├── ENVIRONMENT_SETUP.md        # Environment configuration guide
├── backend/                    # FastAPI backend
│   ├── README.md              # Backend setup instructions
│   ├── app/                   # Application code
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Test suites
│   └── requirements.txt       # Python dependencies
└── mobile/                     # iOS SwiftUI app
    ├── README.md              # iOS setup instructions
    ├── FeatureVoting/         # App source code
    └── FeatureVoting.xcodeproj # Xcode project
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Backend Setup](backend/README.md) | Detailed backend installation and configuration |
| [iOS Setup](mobile/README.md) | iOS development environment setup |
| [API Documentation](API_DOCUMENTATION.md) | Complete API endpoint reference |
| [Database Schema](DATABASE_SCHEMA.md) | Database design and relationships |
| [Environment Setup](ENVIRONMENT_SETUP.md) | Configuration variables guide |

## 🔧 Development

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Check test coverage
python -m pytest --cov=app
```

### Database Operations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### API Development
The backend includes:
- Automatic API documentation at `/docs` (Swagger UI)
- Interactive API explorer at `/redoc`
- Health check endpoint at `/health`

## 🌟 Key Features Implemented

### Enhanced Error Handling
- **API**: Structured error responses with proper HTTP status codes
- **iOS**: User-friendly error messages and graceful failure recovery
- **Network**: Automatic retry logic and connection status detection

### Comprehensive Validation
- **Input Validation**: Real-time form validation with helpful feedback
- **Data Integrity**: Database constraints and business rule enforcement
- **Security**: Protection against common vulnerabilities

### User Experience
- **Responsive Design**: Smooth animations and loading states
- **Accessibility**: Proper error messaging and visual feedback
- **Performance**: Optimized database queries and efficient pagination

## 🚀 Production Deployment

### Backend Deployment
- Use environment variables for configuration
- Set up proper database connection pooling
- Configure logging and monitoring
- Use a production ASGI server (e.g., Gunicorn with Uvicorn)

### iOS Deployment
- Configure production API endpoints
- Set up proper build configurations
- Test on physical devices
- Submit to App Store Connect

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Known Issues

- Currently uses a simple user session system (not production-ready authentication)
- Real-time updates require manual refresh
- Limited to one vote per user per feature

## 🔮 Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] User authentication with JWT tokens
- [ ] Feature categories and filtering
- [ ] Comment system for features
- [ ] Admin dashboard
- [ ] Push notifications for iOS
- [ ] Dark mode support

---

**Built with ❤️ using FastAPI and SwiftUI**

For detailed setup instructions, please refer to the individual README files in the `backend/` and `mobile/` directories.