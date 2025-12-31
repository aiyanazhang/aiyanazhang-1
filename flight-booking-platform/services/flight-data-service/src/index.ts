import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import { AmadeusAdapter } from './adapters/AmadeusAdapter';
import { FlightSearchQuery } from '@flight-booking/shared-types';
import { logger } from './utils/logger';

dotenv.config();

const app = express();
const port = process.env.PORT || 3002;

app.use(express.json());

const amadeusAdapter = new AmadeusAdapter();

app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', service: 'flight-data-service' });
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

    const offers = await amadeusAdapter.searchFlights(query);

    res.json({
      success: true,
      data: offers,
      metadata: {
        total: offers.length,
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
    const keyword = req.query.keyword as string;
    
    if (!keyword || keyword.length < 2) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'INVALID_KEYWORD',
          message: 'Keyword must be at least 2 characters',
        },
      });
    }

    const airports = await amadeusAdapter.searchAirports(keyword);

    res.json({
      success: true,
      data: airports,
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
  logger.info(`Flight Data Service listening on port ${port}`);
});
