# Stripe Payment Integration Setup Guide

This document outlines the requirements and steps needed to complete the Stripe payment integration for the audiobook generator application.

## Environment Variables Required

The following environment variables need to be configured in production:

### Client (.env.local)
```
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
NEXT_PUBLIC_APP_URL=https://your-production-domain.com
```

## Stripe Dashboard Configuration

### 1. Create Product and Price
1. Go to Products in your Stripe Dashboard
2. Create a new product named "Audiobook Generator Premium"
3. Add a recurring price of $9.99/month
4. Copy the Price ID and update `SUBSCRIPTION_PRICE_ID` in `/app/lib/stripe.ts`

### 2. Configure Webhooks
1. Go to Webhooks in your Stripe Dashboard
2. Add endpoint: `https://your-domain.com/api/stripe/webhook`
3. Select these events:
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.deleted`
4. Copy the webhook signing secret

### 3. Enable Customer Portal
1. Go to Settings > Billing > Customer Portal
2. Enable the customer portal
3. Configure allowed features:
   - Update payment methods
   - Cancel subscriptions
   - View invoices

## Database Schema Requirements

You'll need to add subscription tracking to your database:

```sql
-- Add to your user table or create a subscriptions table
ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255);
ALTER TABLE users ADD COLUMN subscription_status VARCHAR(50) DEFAULT 'inactive';
ALTER TABLE users ADD COLUMN subscription_id VARCHAR(255);
ALTER TABLE users ADD COLUMN current_period_end TIMESTAMP;
```

## Implementation TODOs

### High Priority
- [ ] Create database migration for subscription fields
- [ ] Implement subscription status checking middleware
- [ ] Add subscription status checks to audiobook generation endpoints
- [ ] Create user subscription management page
- [ ] Implement proper error handling for failed payments

### Medium Priority
- [ ] Add email notifications for subscription events
- [ ] Implement usage limits for free tier
- [ ] Add analytics tracking for subscription events
- [ ] Create admin dashboard for subscription management

### Low Priority
- [ ] Add promo codes support
- [ ] Implement annual subscription option
- [ ] Add subscription upgrade/downgrade flows
- [ ] Create subscription cancellation flow with feedback

## Security Considerations

1. **Webhook Verification**: Always verify webhook signatures
2. **Environment Variables**: Never commit real API keys to version control
3. **HTTPS Only**: Stripe requires HTTPS in production
4. **Input Validation**: Validate all data from Stripe webhooks
5. **Rate Limiting**: Implement rate limiting on payment endpoints

## Testing

### Local Testing with Stripe CLI
1. Install Stripe CLI: `brew install stripe/stripe-cli/stripe`
2. Login: `stripe login`
3. Forward webhooks: `stripe listen --forward-to localhost:3000/api/stripe/webhook`
4. Use test card numbers from Stripe documentation

### Test Cards
- Success: `4242424242424242`
- Declined: `4000000000000002`
- Requires 3DS: `4000002500003155`

## Production Checklist

- [ ] Update all environment variables with live keys
- [ ] Configure webhook endpoint with production URL
- [ ] Test complete subscription flow
- [ ] Verify webhook event handling
- [ ] Set up monitoring and alerting
- [ ] Configure customer support workflow
- [ ] Update terms of service and privacy policy
- [ ] Set up subscription analytics

## API Endpoints Created

- `POST /api/stripe/create-checkout-session` - Creates Stripe checkout session
- `POST /api/stripe/webhook` - Handles Stripe webhook events
- `POST /api/stripe/create-portal-session` - Creates customer portal session

## Components Created

- `/subscription` - Main subscription page with pricing
- `/subscription/success` - Success page after payment
- `SubscriptionStatus` - Component to show subscription status