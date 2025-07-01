import { NextRequest, NextResponse } from 'next/server';
import { stripeServer } from '@/app/lib/stripe';

export async function POST(request: NextRequest) {
  try {
    if (!stripeServer) {
      return NextResponse.json(
        { error: 'Stripe is not configured' },
        { status: 500 }
      );
    }

    const { userId } = await request.json();

    if (!userId) {
      return NextResponse.json(
        { error: 'Missing user ID' },
        { status: 400 }
      );
    }

    // In a real app, you would fetch the customer ID from your database
    // For now, we'll create a mock customer or return an error
    const customers = await stripeServer.customers.list({
      metadata: { userId },
      limit: 1,
    });

    if (customers.data.length === 0) {
      return NextResponse.json(
        { error: 'No subscription found' },
        { status: 404 }
      );
    }

    const customer = customers.data[0];

    const session = await stripeServer.billingPortal.sessions.create({
      customer: customer.id,
      return_url: `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/subscription`,
    });

    return NextResponse.json({ url: session.url });
  } catch (error) {
    console.error('Error creating portal session:', error);
    return NextResponse.json(
      { error: 'Failed to create portal session' },
      { status: 500 }
    );
  }
}