import { loadStripe } from '@stripe/stripe-js';
import Stripe from 'stripe';

const stripePublishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
const stripeSecretKey = process.env.STRIPE_SECRET_KEY;

if (!stripePublishableKey) {
  throw new Error('NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY is not set');
}

export const stripe = loadStripe(stripePublishableKey);

export const stripeServer = stripeSecretKey 
  ? new Stripe(stripeSecretKey, {
      apiVersion: '2024-12-18.acacia',
    })
  : null;

export const SUBSCRIPTION_PRICE_ID = 'price_mock_monthly_subscription';