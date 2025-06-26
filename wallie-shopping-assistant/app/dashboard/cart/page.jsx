"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { useUser } from "@clerk/nextjs";
import Link from "next/link";

export default function Cart() {
  const { isLoaded, isSignedIn } = useUser();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      setLoading(false);
      return;
    }

    fetch("/api/cart")
      .then((res) => res.json())
      .then(setItems)
      .catch((err) => console.error("Failed to load cart:", err))
      .finally(() => setLoading(false));
  }, [isLoaded, isSignedIn]);

  const handleRemove = async (cartId) => {
    // Immediately optimistically update UI
    setItems((prev) => prev.filter((i) => i.cartId !== cartId));
    await fetch("/api/cart", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cartId }),
    });
  };

  if (!isLoaded || loading) {
    return <div className="p-6 text-gray-500">Loading your cart…</div>;
  }

  if (!isSignedIn) {
    return (
      <div className="p-6">
        <p>
          Please{" "}
          <Link href="/sign-in" className="text-blue-600">
            sign in
          </Link>{" "}
          to view your cart.
        </p>
      </div>
    );
  }

  if (items.length === 0) {
    return <div className="p-6">Your cart is empty.</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Your Cart</h1>
      <ul className="space-y-6">
        {items.map((item) => (
          <li
            key={item.cartId}
            className="flex items-center space-x-4 border-b pb-4"
          >
            <div className="relative h-24 w-24 flex-shrink-0">
              <Image
                src={item.imageUrl}
                alt={item.name}
                fill
                className="object-cover rounded"
              />
            </div>
            <div className="flex-1">
              <h2 className="font-semibold">{item.name}</h2>
              <p>Quantity: {item.quantity}</p>
              <p className="font-bold">
                ${(item.price * item.quantity).toFixed(2)}
              </p>
            </div>
            <button
              onClick={() => handleRemove(item.cartId)}
              className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition"
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
      <div className="mt-6 text-right">
        <Link
          href="/checkout"
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Proceed to Checkout
        </Link>
      </div>
    </div>
  );
}
