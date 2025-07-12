# Denas Backend API

FastAPI backend with PostgreSQL, Firebase Authentication, and Cookie-based Sessions.

## Features

- **Authentication**: Firebase Authentication with cookie-based sessions
- **Database**: PostgreSQL with SQLAlchemy ORM
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Session Management**: Automatic token refresh with httpOnly cookies
- **CORS**: Configurable CORS settings for development and production

## Quick Start

### 1. Environment Configuration

Create environment files in the `env/` directory:

#### Firebase Configuration (Required for Cookie Authentication)

Add the following Firebase configuration to your environment file:

```env
# Firebase Configuration (Required for token refresh)
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your_service_account_email
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_CLIENT_X509_CERT_URL=your_cert_url
```

**How to get Firebase API Key:**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click on Project Settings (gear icon)
4. Go to "General" tab
5. Under "Your apps" section, find "Web API Key"
6. Copy the API key value

#### Database Configuration

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=denas_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 2. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

### 3. API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Cookie-Based Authentication

This backend now supports cookie-based authentication with automatic token refresh:

### How it works:

1. **Login**: User authenticates with Firebase on frontend
2. **Session Setup**: Frontend calls `/auth/set-cookie` with Firebase tokens
3. **Session Storage**: Backend stores tokens in httpOnly cookies
4. **Auto Refresh**: Tokens are automatically refreshed every 30 minutes
5. **Logout**: `/auth/logout` clears all authentication cookies

### Key Endpoints:

- `POST /auth/set-cookie` - Set authentication cookies
- `POST /auth/refresh-token` - Refresh expired tokens
- `GET /auth/session` - Check current session status
- `POST /auth/logout` - Clear authentication cookies

### Security Features:

- **HttpOnly Cookies**: Prevents XSS attacks
- **Secure Cookies**: HTTPS only in production
- **SameSite**: CSRF protection
- **Auto Token Refresh**: Seamless user experience

## Environment Variables

### Required

```env
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_PROJECT_ID=your_project_id
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=denas_db
```

### Optional

```env
ENVIRONMENT=development|production
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## CORS Configuration

The backend automatically configures CORS based on environment:

- **Development**: Allows localhost:3000, localhost:3001
- **Production**: Allows specified domains only

Update `app/main.py` to add your production domains.

## Health Check

Check if the backend is running and properly configured:

```bash
curl http://localhost:8000/health
```

Response includes:
- Database connection status
- Environment information
- Firebase configuration status

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Troubleshooting

### Firebase Configuration Issues

1. **Missing API Key**: Ensure `FIREBASE_API_KEY` is set in your environment
2. **Token Refresh Fails**: Check that the API key has proper permissions
3. **CORS Issues**: Verify your frontend URL is in the allowed origins

### Database Issues

1. **Connection Refused**: Check if PostgreSQL is running
2. **Migration Errors**: Ensure database exists and user has proper permissions

## Production Deployment

1. Set `ENVIRONMENT=production`
2. Update CORS allowed origins in `app/main.py`
3. Use secure values for all environment variables
4. Enable HTTPS for secure cookies

## Project Structure

```
denas-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── users.py      # User API endpoints
│   │       └── api.py            # API router
│   ├── core/
│   │   └── config.py             # Application configuration
│   ├── db/
│   │   ├── base.py               # Database base model
│   │   └── session.py            # Database session
│   ├── models/
│   │   └── user.py               # User database model
│   ├── schemas/
│   │   └── user.py               # Pydantic schemas
│   └── main.py                   # FastAPI application
├── alembic/                      # Database migrations
├── scripts/                      # Development scripts
├── docker-compose.yml            # Docker services
├── Dockerfile                    # Container configuration
├── requirements.txt              # Python dependencies
└── .env                          # Environment variables
```

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### 1. Clone and Setup

```bash
cd denas-backend
```

### 2. Start Development Environment

```bash
# Using the provided script
./scripts/start.sh

# Or manually
docker-compose up --build -d
```

### 3. Run Database Migrations

```bash
# If using the start script, migrations are run automatically
# To run manually:
docker-compose exec app alembic upgrade head
```

### 4. Access the Application

- **API**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Database**: localhost:5432

## Development

### Environment Variables

The application uses the following environment variables (defined in `.env`):

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=denas_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Database Migrations

```bash
# Create a new migration
docker-compose exec app alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose exec app alembic upgrade head

# Rollback migration
docker-compose exec app alembic downgrade -1
```

### API Endpoints

#### Users

- `GET /api/v1/users/` - List all users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/{user_id}` - Get a specific user

#### Health Check

- `GET /health` - Check application and database health
- `GET /` - Root endpoint

### Running Tests

```bash
# Run tests (when implemented)
docker-compose exec app python -m pytest
```

### Development Scripts

```bash
# Start development environment
./scripts/start.sh

# Stop development environment
./scripts/stop.sh

# Reset database (removes all data)
./scripts/reset-db.sh
```

### Local Development (without Docker)

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up local PostgreSQL and update environment variables

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the application:
```bash
uvicorn app.main:app --reload
```

## Database Schema

### Users Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| email | String | User email (unique) |
| username | String | Username (unique) |
| hashed_password | String | Hashed password |
| is_active | Boolean | User active status |
| is_superuser | Boolean | Admin privileges |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

## Configuration

### FastAPI Settings

The application configuration is managed in `app/core/config.py`:

- **PROJECT_NAME**: Application name
- **VERSION**: API version
- **API_V1_STR**: API version prefix
- **DATABASE_URL**: PostgreSQL connection string

### Docker Configuration

- **PostgreSQL**: Port 5432
- **FastAPI**: Port 8000
- **Volumes**: Database data persisted in Docker volume

## Production Deployment

For production deployment:

1. Update environment variables for production
2. Use a production WSGI server (already configured with Uvicorn)
3. Set up proper SSL/TLS certificates
4. Configure CORS settings appropriately
5. Set up monitoring and logging
6. Use a production-grade PostgreSQL instance

## Troubleshooting

### Common Issues

1. **Port already in use**: Change ports in `docker-compose.yml`
2. **Database connection issues**: Ensure PostgreSQL container is running
3. **Migration errors**: Check database connectivity and migration files

### Logs

```bash
# View application logs
docker-compose logs app

# View database logs
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 