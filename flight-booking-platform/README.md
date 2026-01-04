# Flight Booking Platform

A modern microservices-based flight route query and booking system built with React, Node.js, and PostgreSQL.

## Architecture

- **Frontend**: React 18 + TypeScript + Ant Design
- **Backend**: Node.js + Express + TypeScript
- **Databases**: PostgreSQL + Redis + Elasticsearch
- **External APIs**: Amadeus API for flight data

## Project Structure

```
flight-booking-platform/
├── apps/
│   ├── web-client/          # React frontend
│   └── api-gateway/         # Express API Gateway
├── services/
│   ├── flight-data-service/ # Amadeus API integration
│   ├── search-service/      # Flight search logic
│   ├── auth-service/        # Authentication
│   ├── order-service/       # Booking management
│   ├── price-service/       # Price tracking
│   └── recommendation-service/
├── packages/
│   ├── shared-types/        # TypeScript interfaces
│   ├── database-schemas/    # Prisma schemas
│   └── api-clients/         # Inter-service SDKs
└── docker-compose.yml
```

## Getting Started

### Prerequisites

- Node.js >= 18
- Docker & Docker Compose
- Amadeus API credentials (free tier: https://developers.amadeus.com)

### Setup

1. **Clone and install dependencies**:
```bash
npm install
```

2. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env and add your Amadeus API credentials
```

3. **Start databases with Docker**:
```bash
npm run docker:up
```

4. **Run database migrations**:
```bash
npm run prisma:migrate
```

5. **Start all services**:
```bash
npm run dev
```

This will start:
- API Gateway: http://localhost:3000
- Flight Data Service: http://localhost:3002
- Web Client: http://localhost:5173

### Individual Service Commands

```bash
# Start only API Gateway
npm run dev:gateway

# Start only Flight Data Service
npm run dev:flight-data

# Start only Web Client
npm run dev:web

# View Docker logs
npm run docker:logs

# Stop Docker services
npm run docker:down

# Open Prisma Studio (database GUI)
npm run prisma:studio
```

## Development

### Running Tests
```bash
npm run test
```

### Linting
```bash
npm run lint
```

### Code Formatting
```bash
npm run format
```

## API Endpoints

### Flight Data Service (Port 3002)
- `POST /api/flights/search` - Search for flights
- `GET /api/airports/search?keyword={query}` - Search airports

### API Gateway (Port 3000)
- `GET /health` - Health check
- `POST /api/flights/search` - Proxied flight search
- `GET /api/airports/search` - Proxied airport search

## Environment Variables

See `.env.example` for required configuration:
- Database credentials (PostgreSQL, Redis)
- Amadeus API credentials
- JWT secrets
- Service URLs

## Phase 1: MVP Features (Current)

- ✅ Flight search (one-way & round-trip)
- ✅ Airport autocomplete
- ✅ Real-time Amadeus API integration
- ✅ Redis caching for performance
- 🚧 Search results display with filters
- 🚧 Sort by price, duration, departure time
- ⏳ User authentication
- ⏳ Booking flow

## Roadmap

### Phase 2: User Management & Bookings (Weeks 5-7)
- User registration and login
- Booking workflow
- Payment integration (Stripe)
- Order management

### Phase 3: Advanced Features (Weeks 8-9)
- Price tracking and alerts
- Historical price data
- Popular routes recommendations

### Phase 4: Production Ready (Weeks 10-11)
- Kubernetes deployment
- Monitoring (Prometheus + Grafana)
- Load testing
- CI/CD pipeline

## Tech Stack Details

### Frontend
- React 19 + TypeScript
- Ant Design (UI components)
- React Query (API state management)
- React Router (navigation)
- Day.js (date handling)
- Vite (build tool)

### Backend
- Node.js + Express
- TypeScript
- Prisma (ORM)
- Redis (caching)
- Winston (logging)
- Axios (HTTP client)

### Infrastructure
- Docker Compose (development)
- PostgreSQL 15 with PostGIS
- Redis 7
- Elasticsearch 8

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

MIT

## Support

For questions or issues, please open a GitHub issue.
