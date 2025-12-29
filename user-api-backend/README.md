# User API Backend

Flask-based REST API for user management with JWT authentication.

## Features

- User registration and login
- JWT token-based authentication
- Password hashing with bcrypt
- MongoDB database integration
- Input validation
- Protected API endpoints

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

3. Update `.env` with your configuration:
- Set a secure `JWT_SECRET_KEY`
- Configure MongoDB connection if needed

4. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (requires JWT)

### Users (Protected)

- `GET /api/users` - Get all users (requires JWT)
- `GET /api/users/<user_id>` - Get user by ID (requires JWT)
- `GET /api/users/username/<username>` - Get user by username (requires JWT)

### Health

- `GET /api/health` - Health check endpoint

## Authentication

Protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

Obtain a token by registering or logging in.
