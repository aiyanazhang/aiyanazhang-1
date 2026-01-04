import axios, { AxiosInstance } from 'axios';
import Redis from 'ioredis';
import {
  FlightOffer,
  FlightSearchQuery,
  AmadeusAccessToken,
  AmadeusFlightOffer,
  Airport,
  FlightSegment,
  Price,
  CabinClass,
} from '@flight-booking/shared-types';
import { logger } from '../utils/logger';

export class AmadeusAdapter {
  private client: AxiosInstance;
  private redis: Redis;
  private apiKey: string;
  private apiSecret: string;
  private baseUrl: string;
  private accessToken: string | null = null;
  private tokenExpiresAt: number = 0;

  constructor() {
    this.apiKey = process.env.AMADEUS_API_KEY || '';
    this.apiSecret = process.env.AMADEUS_API_SECRET || '';
    this.baseUrl = process.env.AMADEUS_API_URL || 'https://test.api.amadeus.com';
    
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 10000,
    });

    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
    });
  }

  private async getAccessToken(): Promise<string> {
    const now = Date.now();
    
    if (this.accessToken && now < this.tokenExpiresAt) {
      return this.accessToken;
    }

    const cachedToken = await this.redis.get('amadeus:access_token');
    if (cachedToken) {
      this.accessToken = cachedToken;
      const ttl = await this.redis.ttl('amadeus:access_token');
      this.tokenExpiresAt = now + (ttl * 1000);
      return cachedToken;
    }

    try {
      const response = await axios.post<AmadeusAccessToken>(
        `${this.baseUrl}/v1/security/oauth2/token`,
        new URLSearchParams({
          grant_type: 'client_credentials',
          client_id: this.apiKey,
          client_secret: this.apiSecret,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      this.accessToken = response.data.access_token;
      const expiresIn = response.data.expires_in;
      this.tokenExpiresAt = now + (expiresIn * 1000);

      await this.redis.setex('amadeus:access_token', expiresIn - 100, this.accessToken);

      logger.info('Amadeus access token refreshed');
      return this.accessToken;
    } catch (error: any) {
      logger.error('Failed to get Amadeus access token', { error: error.message });
      throw new Error('Failed to authenticate with Amadeus API');
    }
  }

  async searchFlights(query: FlightSearchQuery): Promise<FlightOffer[]> {
    const cacheKey = this.buildCacheKey(query);
    
    const cachedResult = await this.redis.get(cacheKey);
    if (cachedResult) {
      logger.info('Returning cached flight search results', { cacheKey });
      return JSON.parse(cachedResult);
    }

    try {
      const token = await this.getAccessToken();
      
      const params: any = {
        originLocationCode: query.origin,
        destinationLocationCode: query.destination,
        departureDate: query.departureDate,
        adults: query.passengers.adults,
        children: query.passengers.children || 0,
        infants: query.passengers.infants || 0,
        travelClass: this.mapCabinClass(query.cabinClass),
        nonStop: query.directFlightsOnly || false,
        max: 50,
      };

      if (query.returnDate) {
        params.returnDate = query.returnDate;
      }

      if (query.maxStops !== undefined) {
        params.maxStops = query.maxStops;
      }

      const response = await this.client.get('/v2/shopping/flight-offers', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        params,
      });

      const offers = this.transformAmadeusOffers(response.data.data || []);
      
      await this.redis.setex(cacheKey, 300, JSON.stringify(offers));
      
      logger.info('Flight search completed', {
        origin: query.origin,
        destination: query.destination,
        resultsCount: offers.length,
      });

      return offers;
    } catch (error: any) {
      if (error.response?.status === 401) {
        this.accessToken = null;
        await this.redis.del('amadeus:access_token');
        logger.warn('Amadeus token expired, retrying...');
        return this.searchFlights(query);
      }

      logger.error('Flight search failed', {
        error: error.message,
        response: error.response?.data,
      });
      throw new Error('Failed to search flights');
    }
  }

  private transformAmadeusOffers(amadeusOffers: AmadeusFlightOffer[]): FlightOffer[] {
    return amadeusOffers.map((offer) => this.transformSingleOffer(offer));
  }

  private transformSingleOffer(offer: AmadeusFlightOffer): FlightOffer {
    const outboundItinerary = offer.itineraries[0];
    const inboundItinerary = offer.itineraries[1];

    const outbound = this.transformSegments(outboundItinerary.segments);
    const inbound = inboundItinerary ? this.transformSegments(inboundItinerary.segments) : undefined;

    const price: Price = {
      amount: parseFloat(offer.price.grandTotal),
      currency: offer.price.currency,
      pricePerPassenger: parseFloat(offer.price.total) / offer.travelerPricings.length,
      taxes: offer.price.fees?.reduce((sum, fee) => sum + parseFloat(fee.amount), 0) || 0,
    };

    const totalPassengers = offer.travelerPricings.length;
    const adultCount = offer.travelerPricings.filter(t => t.travelerType === 'ADULT').length;
    const childCount = offer.travelerPricings.filter(t => t.travelerType === 'CHILD').length;
    const infantCount = totalPassengers - adultCount - childCount;

    const cabinClass = this.extractCabinClass(offer);

    return {
      id: offer.id,
      origin: this.createAirportStub(outbound[0].departureAirport),
      destination: this.createAirportStub(outbound[outbound.length - 1].arrivalAirport),
      outbound,
      inbound,
      price,
      passengers: {
        adults: adultCount,
        children: childCount,
        infants: infantCount,
      },
      bookingClass: cabinClass,
      provider: 'amadeus',
      deepLink: `https://www.amadeus.com/booking/${offer.id}`,
      availableSeats: offer.numberOfBookableSeats,
    };
  }

  private transformSegments(segments: any[]): FlightSegment[] {
    return segments.map((segment) => ({
      departureAirport: segment.departure.iataCode,
      arrivalAirport: segment.arrival.iataCode,
      departureTime: new Date(segment.departure.at),
      arrivalTime: new Date(segment.arrival.at),
      duration: this.parseDuration(segment.duration),
      airline: segment.carrierCode,
      flightNumber: `${segment.carrierCode}${segment.number}`,
      aircraft: segment.aircraft?.code,
      stops: [],
    }));
  }

  private parseDuration(isoDuration: string): number {
    const match = isoDuration.match(/PT(?:(\d+)H)?(?:(\d+)M)?/);
    if (!match) return 0;
    const hours = parseInt(match[1] || '0');
    const minutes = parseInt(match[2] || '0');
    return hours * 60 + minutes;
  }

  private mapCabinClass(cabinClass: CabinClass): string {
    const mapping: Record<CabinClass, string> = {
      economy: 'ECONOMY',
      premium_economy: 'PREMIUM_ECONOMY',
      business: 'BUSINESS',
      first: 'FIRST',
    };
    return mapping[cabinClass] || 'ECONOMY';
  }

  private extractCabinClass(offer: AmadeusFlightOffer): CabinClass {
    const cabin = offer.travelerPricings[0]?.fareDetailsBySegment[0]?.cabin || 'ECONOMY';
    const mapping: Record<string, CabinClass> = {
      ECONOMY: 'economy',
      PREMIUM_ECONOMY: 'premium_economy',
      BUSINESS: 'business',
      FIRST: 'first',
    };
    return mapping[cabin] || 'economy';
  }

  private createAirportStub(iataCode: string): Airport {
    return {
      iataCode,
      name: iataCode,
      city: iataCode,
      country: '',
      latitude: 0,
      longitude: 0,
      timezone: '',
    };
  }

  private buildCacheKey(query: FlightSearchQuery): string {
    const { origin, destination, departureDate, returnDate, passengers, cabinClass } = query;
    const passengerStr = `${passengers.adults}-${passengers.children}-${passengers.infants}`;
    return `flight:search:${origin}:${destination}:${departureDate}:${returnDate || 'oneway'}:${passengerStr}:${cabinClass}`;
  }

  async searchAirports(keyword: string): Promise<Airport[]> {
    const cacheKey = `airport:search:${keyword.toLowerCase()}`;
    
    const cached = await this.redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    try {
      const token = await this.getAccessToken();
      
      const response = await this.client.get('/v1/reference-data/locations', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        params: {
          keyword,
          subType: 'AIRPORT',
          'page[limit]': 10,
        },
      });

      const airports: Airport[] = (response.data.data || []).map((location: any) => ({
        iataCode: location.iataCode,
        name: location.name,
        city: location.address?.cityName || '',
        country: location.address?.countryName || '',
        latitude: location.geoCode?.latitude || 0,
        longitude: location.geoCode?.longitude || 0,
        timezone: location.timeZoneOffset || '',
      }));

      await this.redis.setex(cacheKey, 86400, JSON.stringify(airports));

      return airports;
    } catch (error: any) {
      logger.error('Airport search failed', { error: error.message });
      return [];
    }
  }
}
