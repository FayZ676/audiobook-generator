"use client";

import { useEffect, useState } from 'react';
import { stripe } from '@/app/lib/stripe';
import { useUser } from '@clerk/nextjs';

export default function SubscriptionPage() {
  const [stripeLoaded, setStripeLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useUser();

  useEffect(() => {
    const loadStripe = async () => {
      const stripeInstance = await stripe;
      if (stripeInstance) {
        setStripeLoaded(true);
      }
    };
    loadStripe();
  }, []);

  const handleSubscribe = async () => {
    if (!user) {
      alert('Please sign in to subscribe');
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await fetch('/api/stripe/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: user.id,
          email: user.emailAddresses[0]?.emailAddress,
        }),
      });

      const { url } = await response.json();
      
      if (url) {
        window.location.href = url;
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
      alert('Failed to start checkout process');
    } finally {
      setIsLoading(false);
    }
  };

  if (!stripeLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-16 px-4">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-4">Upgrade to Premium</h1>
          <p className="text-gray-600">
            Unlock unlimited audiobook generation with our monthly subscription
          </p>
        </div>

        <div className="bg-base-200 p-6 rounded-lg border-2 border-primary">
          <div className="text-center">
            <h2 className="text-xl font-semibold mb-2">Premium Plan</h2>
            <div className="text-3xl font-bold text-primary mb-1">$9.99</div>
            <div className="text-sm text-gray-600 mb-6">per month</div>

            <div className="space-y-3 mb-6 text-left">
              <div className="flex items-center gap-2">
                <svg className="h-4 w-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-sm">Unlimited voice cloning</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="h-4 w-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-sm">Multi-speaker audiobooks</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="h-4 w-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-sm">Priority processing</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="h-4 w-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-sm">High-quality output</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="h-4 w-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-sm">Email support</span>
              </div>
            </div>

            <button
              onClick={handleSubscribe}
              disabled={isLoading || !user}
              className="btn btn-primary btn-block mb-4"
            >
              {isLoading ? (
                <>
                  <span className="loading loading-spinner loading-sm"></span>
                  Processing...
                </>
              ) : (
                'Subscribe Now'
              )}
            </button>
            
            {!user && (
              <p className="text-xs text-gray-500">Please sign in to subscribe</p>
            )}
          </div>
        </div>

        <div className="text-center mt-6">
          <p className="text-xs text-gray-500">
            Cancel anytime. Secure payment processed by Stripe.
          </p>
        </div>
      </div>
    </div>
  );
}