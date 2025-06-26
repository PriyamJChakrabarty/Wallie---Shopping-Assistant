// components/AddToCartButton.jsx
"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function AddToCartButton({ productId, initialInCart }) {
  const [inCart, setInCart]   = useState(initialInCart);
  const [loading, setLoading] = useState(false);
  const router                = useRouter();

  const handleClick = async () => {
    if (inCart) {
      // if already in cart, just navigate
      router.push("/dashboard/cart");
      return;
    }
    console.log("[AddToCart] Clicked, sending request for productId=", productId);

    setLoading(true);
    try {
      const res = await fetch("/api/cart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ productId }),
      });

      console.log("[AddToCart] Fetch returned:", res.status, res.statusText);
      
      if (!res.ok) throw new Error("Network error");

      // flip the button
      setInCart(true);

      // re-render any server components that read from cart
      router.refresh();
    } catch (err) {
      console.error(err);
      // you can show an error toast here
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className={`px-4 py-2 rounded transition ${
        inCart
          ? "bg-gray-300 text-gray-700 hover:bg-gray-400"
          : "bg-blue-600 text-white hover:bg-blue-700"
      }`}
    >
      {inCart ? "View Cart" : loading ? "Adding…" : "Add to Cart"}
    </button>
  );
}
