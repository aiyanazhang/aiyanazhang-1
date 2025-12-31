import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import { FlightSearchQuery, FlightOffer } from '@flight-booking/shared-types';
import { logger } from './utils/logger';

dotenv.config();

const app = express();
const port = process.env.PORT || 3002;

app.use(express.json());

app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', service: 'flight-data-service-mock' });
});

app.post('/api/flights/search', async (req: Request, res: Response) => {
  try {
    const query: FlightSearchQuery = req.body;
    
    if (!query.origin || !query.destination || !query.departureDate) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'INVALID_QUERY',
          message: 'Missing required fields: origin, destination, departureDate',
        },
      });
    }

    logger.info('Flight search request', { query });

    const mockOffers: FlightOffer[] = [
      {
        id: 'mock-1',
        origin: {
          iataCode: query.origin,
          name: `${query.origin} Airport`,
          city: query.origin,
          country: 'Mock Country',
          latitude: 0,
          longitude: 0,
          timezone: 'UTC',
        },
        destination: {
          iataCode: query.destination,
          name: `${query.destination} Airport`,
          city: query.destination,
          country: 'Mock Country',
          latitude: 0,
          longitude: 0,
          timezone: 'UTC',
        },
        outbound: [
          {
            departureAirport: query.origin,
            arrivalAirport: query.destination,
            departureTime: new Date(`${query.departureDate}T08:00:00`),
            arrivalTime: new Date(`${query.departureDate}T12:00:00`),
            duration: 240,
            airline: 'AA',
            flightNumber: 'AA100',
            stops: [],
          },
        ],
        price: {
          amount: 299.99,
          currency: 'USD',
          pricePerPassenger: 299.99,
        },
        passengers: query.passengers,
        bookingClass: query.cabinClass,
        provider: 'amadeus',
        deepLink: 'https://example.com/booking/mock-1',
        availableSeats: 10,
      },
      {
        id: 'mock-2',
        origin: {
          iataCode: query.origin,
          name: `${query.origin} Airport`,
          city: query.origin,
          country: 'Mock Country',
          latitude: 0,
          longitude: 0,
          timezone: 'UTC',
        },
        destination: {
          iataCode: query.destination,
          name: `${query.destination} Airport`,
          city: query.destination,
          country: 'Mock Country',
          latitude: 0,
          longitude: 0,
          timezone: 'UTC',
        },
        outbound: [
          {
            departureAirport: query.origin,
            arrivalAirport: query.destination,
            departureTime: new Date(`${query.departureDate}T14:00:00`),
            arrivalTime: new Date(`${query.departureDate}T18:30:00`),
            duration: 270,
            airline: 'DL',
            flightNumber: 'DL200',
            stops: [],
          },
        ],
        price: {
          amount: 249.99,
          currency: 'USD',
          pricePerPassenger: 249.99,
        },
        passengers: query.passengers,
        bookingClass: query.cabinClass,
        provider: 'amadeus',
        deepLink: 'https://example.com/booking/mock-2',
        availableSeats: 5,
      },
    ];

    res.json({
      success: true,
      data: mockOffers,
      metadata: {
        total: mockOffers.length,
      },
    });
  } catch (error: any) {
    logger.error('Flight search endpoint error', { error: error.message });
    res.status(500).json({
      success: false,
      error: {
        code: 'SEARCH_FAILED',
        message: 'Failed to search flights',
        details: error.message,
      },
    });
  }
});

app.get('/api/airports/search', async (req: Request, res: Response) => {
  try {
    const keyword = (req.query.keyword as string || '').toLowerCase();
    
    if (!keyword || keyword.length < 2) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'INVALID_KEYWORD',
          message: 'Keyword must be at least 2 characters',
        },
      });
    }

    const mockAirports = [
      { iataCode: 'JFK', name: 'John F. Kennedy International Airport', city: 'New York', country: 'United States', latitude: 40.6413, longitude: -73.7781, timezone: 'America/New_York' },
      { iataCode: 'LAX', name: 'Los Angeles International Airport', city: 'Los Angeles', country: 'United States', latitude: 33.9416, longitude: -118.4085, timezone: 'America/Los_Angeles' },
      { iataCode: 'PEK', name: 'Beijing Capital International Airport', city: 'Beijing', country: 'China', latitude: 40.0799, longitude: 116.6031, timezone: 'Asia/Shanghai' },
      { iataCode: 'PVG', name: 'Shanghai Pudong International Airport', city: 'Shanghai', country: 'China', latitude: 31.1443, longitude: 121.8083, timezone: 'Asia/Shanghai' },
      { iataCode: 'LHR', name: 'London Heathrow Airport', city: 'London', country: 'United Kingdom', latitude: 51.4700, longitude: -0.4543, timezone: 'Europe/London' },
    ];

    const filtered = mockAirports.filter(
      (airport) =>
        airport.iataCode.toLowerCase().includes(keyword) ||
        airport.name.toLowerCase().includes(keyword) ||
        airport.city.toLowerCase().includes(keyword)
    );

    res.json({
      success: true,
      data: filtered,
    });
  } catch (error: any) {
    logger.error('Airport search endpoint error', { error: error.message });
    res.status(500).json({
      success: false,
      error: {
        code: 'SEARCH_FAILED',
        message: 'Failed to search airports',
      },
    });
  }
});

app.listen(port, () => {
  logger.info(`Flight Data Service (Mock Mode) listening on port ${port}`);
  logger.warn('Running in MOCK mode - using simulated data instead of Amadeus API');
});
