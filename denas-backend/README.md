# Denas Backend

A modern FastAPI backend with PostgreSQL database and Alembic migrations, containerized with Docker.

## Features

- **FastAPI** - Modern, fast Python web framework
- **PostgreSQL** - Robust relational database
- **Alembic** - Database migrations
- **Docker** - Containerized development environment
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Pydantic** - Data validation using Python type hints

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