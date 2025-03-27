# Garmin Connect REST API

A REST API wrapper for Garmin Connect, built with FastAPI and deployed on Vercel.

## Features

- RESTful API endpoints for Garmin Connect data
- JWT-based authentication
- Rate limiting
- CORS enabled
- Type-safe with Pydantic models
- Deployed on Vercel

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To use the API:

1. First, get an access token by making a POST request to `/token`:
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your.email@example.com&password=your.password"
```

2. Use the received token in subsequent requests:
```bash
curl -X GET "http://localhost:8000/stats?date=2024-03-27" \
  -H "Authorization: Bearer your.access.token"
```

## Rate Limiting

- Login endpoint: 5 requests per minute
- Other endpoints: 30 requests per minute

## Endpoints

### Authentication
- `POST /token` - Get access token

### User Data
- `GET /user/profile` - Get user profile information
- `GET /stats` - Get user stats for a specific date
- `GET /activities` - Get activities for a date range

### Health Data
- `GET /body-composition` - Get body composition data for a date range
- `GET /steps` - Get steps data for a specific date
- `GET /heart-rate` - Get heart rate data for a specific date
- `GET /sleep` - Get sleep data for a specific date
- `GET /stress` - Get stress data for a specific date
- `GET /body-battery` - Get body battery data for a date range

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run the development server:
   ```bash
   uvicorn api.main:app --reload
   ```

## Development

The API is configured for development with:
- Hot reload enabled
- Debug mode on
- Swagger UI at `/docs`
- ReDoc at `/redoc`

## Deployment

The API is configured for deployment on Vercel. To deploy:

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set up environment variables in Vercel:
   - `SECRET_KEY` - Your JWT secret key
4. Deploy!

## API Documentation

Once the server is running, visit:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Security

- All endpoints require authentication except `/token`
- Passwords are never stored, only used for Garmin Connect authentication
- JWT tokens expire after 30 minutes
- Rate limiting is enabled on all endpoints
- CORS is configured (customize for production)

## License

MIT
