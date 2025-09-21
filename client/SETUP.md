# Quick Setup Guide

This guide will help you get both the frontend and backend running quickly.

## Prerequisites

- Node.js 18+
- Python 3.8+
- npm or yarn

## Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd ../backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

   The backend will be available at: http://localhost:8000

   **Database Note**: The backend uses SQLite by default. The database file (`feature_voting.db`) will be created automatically in the backend directory.

## Frontend Setup

1. **Navigate to client directory:**
   ```bash
   cd client
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at: http://localhost:5173

## Testing the Application

1. **Open the frontend** in your browser: http://localhost:5173
2. **Create a new user** or select an existing one (if any)
3. **Add some features** using the "Add Feature" button
4. **Vote on features** to test the voting functionality
5. **Check pagination** by adding multiple features

## API Testing

You can also test the backend API directly:

```bash
# Health check
curl http://localhost:8000/health

# Create a user
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com"}'

# Get features
curl "http://localhost:8000/api/features/"
```

## Database Information

- **Type**: SQLite (for easy development)
- **File**: `feature_voting.db` (created automatically in `/backend`)
- **Schema**: Users, Features, and Votes tables
- **Data**: Persists between server restarts

## Troubleshooting

- **Port conflicts**: Make sure ports 8000 (backend) and 5173 (frontend) are available
- **CORS issues**: The backend is configured to allow requests from the frontend
- **Database errors**: Delete `feature_voting.db` to reset the database if needed