"use server";

import { headers } from "next/headers";

import { stripe } from "@/app/lib/stripe";

export async function fetchClientSecret() {
  const origin = (await headers()).get("origin");

  const session = await stripe.checkout.sessions.create({
    ui_mode: "embedded",
    line_items: [
      {
        // Provide the exact Price ID (for example, price_1234) of
        // the product you want to sell
        price: "price_1Rfue8Q2e11KHE2H0EPgpk9m",
        quantity: 1,
      },
    ],
    mode: "subscription",
    return_url: `${origin}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
  });

  return session.client_secret;
}
