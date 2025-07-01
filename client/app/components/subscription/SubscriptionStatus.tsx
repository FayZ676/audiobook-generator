"use client";

import { useState } from 'react';
import { useUser } from '@clerk/nextjs';

interface SubscriptionStatusProps {
  isSubscribed?: boolean;
  subscriptionEndDate?: string;
}

export default function SubscriptionStatus({ 
  isSubscribed = false, 
  subscriptionEndDate 
}: SubscriptionStatusProps) {
  const { user } = useUser();
  const [isLoading, setIsLoading] = useState(false);

  const handleManageSubscription = async () => {
    if (!user) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/stripe/create-portal-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: user.id,
        }),
      });

      const { url } = await response.json();
      if (url) {
        window.location.href = url;
      }
    } catch (error) {
      console.error('Error creating portal session:', error);
      alert('Failed to open billing portal');
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className="bg-base-200 p-4 rounded-lg">
      <h3 className="font-semibold mb-2">Subscription Status</h3>
      
      {isSubscribed ? (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-green-600">Premium Active</span>
          </div>
          {subscriptionEndDate && (
            <p className="text-xs text-gray-500">
              Next billing: {new Date(subscriptionEndDate).toLocaleDateString()}
            </p>
          )}
          <button
            onClick={handleManageSubscription}
            disabled={isLoading}
            className="btn btn-sm btn-outline"
          >
            {isLoading ? 'Loading...' : 'Manage Subscription'}
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
            <span className="text-sm text-gray-600">Free Tier</span>
          </div>
          <p className="text-xs text-gray-500">
            Upgrade to unlock premium features
          </p>
        </div>
      )}
    </div>
  );
}