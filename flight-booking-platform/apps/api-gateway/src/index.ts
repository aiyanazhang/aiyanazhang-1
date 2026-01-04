import express, { Express, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import dotenv from 'dotenv';
import axios from 'axios';
import { logger } from './utils/logger';

dotenv.config();

const app: Express = express();
const port = process.env.PORT || 3000;

const FLIGHT_DATA_SERVICE_URL = process.env.FLIGHT_DATA_SERVICE_URL || 'http://localhost:3002';

app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
  credentials: true,
}));
app.use(express.json());

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: 'Too many requests from this IP, please try again later.',
});

app.use('/api/', apiLimiter);

app.use((req: Request, res: Response, next: NextFunction) => {
  logger.info(`${req.method} ${req.path}`, {
    query: req.query,
    ip: req.ip,
  });
  next();
});

app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    service: 'api-gateway',
    timestamp: new Date().toISOString(),
  });
});

app.post('/api/flights/search', async (req: Request, res: Response) => {
  try {
    const response = await axios.post(
      `${FLIGHT_DATA_SERVICE_URL}/api/flights/search`,
      req.body,
      { timeout: 30000 }
    );
    res.json(response.data);
  } catch (error: any) {
    logger.error('Error proxying flight search', {
      error: error.message,
      response: error.response?.data,
    });
    
    res.status(error.response?.status || 500).json({
      success: false,
      error: {
        code: 'GATEWAY_ERROR',
        message: error.response?.data?.error?.message || 'Failed to search flights',
      },
    });
  }
});

app.get('/api/airports/search', async (req: Request, res: Response) => {
  try {
    const response = await axios.get(
      `${FLIGHT_DATA_SERVICE_URL}/api/airports/search`,
      {
        params: req.query,
        timeout: 5000,
      }
    );
    res.json(response.data);
  } catch (error: any) {
    logger.error('Error proxying airport search', { error: error.message });
    
    res.status(error.response?.status || 500).json({
      success: false,
      error: {
        code: 'GATEWAY_ERROR',
        message: 'Failed to search airports',
      },
    });
  }
});

app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  logger.error('Unhandled error', { error: err.message, stack: err.stack });
  res.status(500).json({
    success: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred',
    },
  });
});

app.listen(port, () => {
  logger.info(`API Gateway listening on port ${port}`);
  logger.info(`Flight Data Service URL: ${FLIGHT_DATA_SERVICE_URL}`);
});
