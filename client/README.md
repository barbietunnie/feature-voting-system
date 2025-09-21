# Feature Voting System - Frontend Client

A modern React web application for the Feature Voting System, built with TypeScript, Vite, and shadcn/ui.

## Features

- **User Authentication**: Login with existing users or create new user profiles
- **Feature Management**: View, create, and vote on feature requests
- **Real-time Updates**: Optimistic UI updates for voting
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UI**: Beautiful interface built with shadcn/ui components
- **Type Safety**: Full TypeScript support for better development experience

## Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful and accessible UI components
- **Axios** - HTTP client for API communication
- **React Hook Form** - Form handling and validation
- **Zod** - Schema validation

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API server running on http://localhost:8000

**Note**: The backend is currently configured to use SQLite for easy setup and testing. The database file (`feature_voting.db`) will be automatically created in the backend directory when you first start the server.

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open http://localhost:5173 in your browser

### Environment Variables

Create a `.env` file in the root directory (optional):

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Project Structure

```
client/
├── src/
│   ├── components/          # React components
│   │   ├── ui/              # shadcn/ui components
│   │   ├── LoginView.tsx    # User authentication
│   │   ├── FeatureList.tsx  # Feature listing and voting
│   │   ├── AddFeatureModal.tsx # Feature creation modal
│   │   └── VoteButton.tsx   # Voting component
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.tsx      # Authentication state management
│   │   └── useFeatures.tsx  # Feature data management
│   ├── services/            # API services
│   │   └── api.ts           # HTTP client and API calls
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts         # API response types
│   ├── lib/                 # Utility functions
│   │   └── utils.ts         # shadcn/ui utilities
│   ├── App.tsx              # Main application component
│   ├── main.tsx             # Application entry point
│   └── index.css            # Global styles and Tailwind imports
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── vite.config.ts
└── README.md
```

## Application Flow

1. **Login/Registration**: Users can select an existing user or create a new one
2. **Feature Listing**: View all features sorted by vote count
3. **Voting**: Vote for features with optimistic UI updates
4. **Feature Creation**: Add new feature requests via modal form
5. **Pagination**: Load more features as needed

## API Integration

The frontend communicates with the backend API using Axios with comprehensive error handling and loading states.

## Database Configuration

The backend is currently configured to use **SQLite** for easy development and testing:

- **Current Setup**: SQLite database (`feature_voting.db`)
- **Location**: Created automatically in the `/backend` directory
- **Benefits**: No additional setup required, perfect for development and demo

### Production Considerations

For production deployment, the backend can be easily switched to PostgreSQL:

1. **Configure PostgreSQL connection** in the backend's `database.py`
2. **Set DATABASE_URL environment variable** with PostgreSQL connection string
3. **Example**: `postgresql://user:password@localhost:5432/feature_voting_db`

The frontend will work seamlessly with either database backend since it only communicates through the REST API.

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.
