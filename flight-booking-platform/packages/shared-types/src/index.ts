export interface Airport {
  iataCode: string;
  icaoCode?: string;
  name: string;
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  timezone: string;
  metadata?: Record<string, any>;
}

export interface Airline {
  iataCode: string;
  icaoCode?: string;
  name: string;
  country: string;
  logoUrl?: string;
  alliance?: 'Star Alliance' | 'SkyTeam' | 'Oneworld' | null;
}

export interface Stop {
  airport: string;
  duration: number;
  arrivalTime: Date;
  departureTime: Date;
}

export interface FlightSegment {
  departureAirport: string;
  arrivalAirport: string;
  departureTime: Date;
  arrivalTime: Date;
  duration: number;
  airline: string;
  flightNumber: string;
  aircraft?: string;
  stops: Stop[];
}

export interface Price {
  amount: number;
  currency: string;
  pricePerPassenger?: number;
  taxes?: number;
  fees?: number;
}

export interface PassengerCount {
  adults: number;
  children: number;
  infants: number;
}

export type CabinClass = 'economy' | 'premium_economy' | 'business' | 'first';

export type FlightProvider = 'amadeus' | 'kiwi';

export interface FlightOffer {
  id: string;
  origin: Airport;
  destination: Airport;
  outbound: FlightSegment[];
  inbound?: FlightSegment[];
  price: Price;
  passengers: PassengerCount;
  bookingClass: CabinClass;
  provider: FlightProvider;
  deepLink: string;
  availableSeats?: number;
  baggageAllowance?: {
    checked: number;
    cabin: number;
  };
}

export interface FlightSearchQuery {
  origin: string;
  destination: string;
  departureDate: string;
  returnDate?: string;
  passengers: PassengerCount;
  cabinClass: CabinClass;
  directFlightsOnly?: boolean;
  maxStops?: number;
  preferredAirlines?: string[];
}

export interface FlightSearchFilters {
  priceRange?: {
    min: number;
    max: number;
  };
  airlines?: string[];
  departureTimeRange?: {
    start: string;
    end: string;
  };
  arrivalTimeRange?: {
    start: string;
    end: string;
  };
  maxStops?: number;
  maxDuration?: number;
}

export type SortOption = 'price' | 'duration' | 'departure_time' | 'arrival_time' | 'best';

export interface FlightSearchResponse {
  offers: FlightOffer[];
  total: number;
  filters: {
    priceRange: { min: number; max: number };
    airlines: string[];
    maxStops: number;
  };
  searchId: string;
}

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone?: string;
  emailVerified: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export type OrderStatus = 'pending' | 'confirmed' | 'cancelled' | 'refunded' | 'completed';

export type PaymentStatus = 'pending' | 'processing' | 'succeeded' | 'failed' | 'refunded';

export interface Passenger {
  id?: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  passportNumber?: string;
  nationality: string;
  passengerType: 'adult' | 'child' | 'infant';
}

export interface Order {
  id: string;
  userId: string;
  orderNumber: string;
  status: OrderStatus;
  totalPrice: number;
  currency: string;
  paymentMethod?: string;
  paymentStatus: PaymentStatus;
  flightData: FlightOffer;
  passengers: Passenger[];
  createdAt: Date;
  updatedAt: Date;
}

export interface PriceAlert {
  id: string;
  userId: string;
  origin: string;
  destination: string;
  departureDate: string;
  returnDate?: string;
  targetPrice: number;
  currency: string;
  active: boolean;
  createdAt: Date;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata?: {
    page?: number;
    limit?: number;
    total?: number;
  };
}

export interface AmadeusAccessToken {
  access_token: string;
  token_type: string;
  expires_in: number;
  state?: string;
}

export interface AmadeusFlightOffer {
  type: string;
  id: string;
  source: string;
  instantTicketingRequired: boolean;
  nonHomogeneous: boolean;
  oneWay: boolean;
  lastTicketingDate: string;
  numberOfBookableSeats: number;
  itineraries: AmadeusItinerary[];
  price: AmadeusPrice;
  pricingOptions: {
    fareType: string[];
    includedCheckedBagsOnly: boolean;
  };
  validatingAirlineCodes: string[];
  travelerPricings: AmadeusTravelerPricing[];
}

export interface AmadeusItinerary {
  duration: string;
  segments: AmadeusSegment[];
}

export interface AmadeusSegment {
  departure: {
    iataCode: string;
    terminal?: string;
    at: string;
  };
  arrival: {
    iataCode: string;
    terminal?: string;
    at: string;
  };
  carrierCode: string;
  number: string;
  aircraft: {
    code: string;
  };
  operating?: {
    carrierCode: string;
  };
  duration: string;
  id: string;
  numberOfStops: number;
  blacklistedInEU: boolean;
}

export interface AmadeusPrice {
  currency: string;
  total: string;
  base: string;
  fees: Array<{
    amount: string;
    type: string;
  }>;
  grandTotal: string;
}

export interface AmadeusTravelerPricing {
  travelerId: string;
  fareOption: string;
  travelerType: string;
  price: {
    currency: string;
    total: string;
    base: string;
  };
  fareDetailsBySegment: Array<{
    segmentId: string;
    cabin: string;
    fareBasis: string;
    class: string;
    includedCheckedBags: {
      weight?: number;
      weightUnit?: string;
    };
  }>;
}
