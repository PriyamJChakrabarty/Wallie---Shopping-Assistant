// components/Products.jsx
import React from "react";
import Image from "next/image";
import AddToCartButton from "./AddToCartButton";
import { db } from "@/utils/db";
import { Product, CartItem } from "@/utils/schema";
import { currentUser } from "@clerk/nextjs/server";
import { eq, and } from "drizzle-orm";

export const dynamic = 'force-dynamic'; // ← turn off caching so cart state is always fresh

export default async function Products() {
  // 1️⃣ Get the current user’s email (server side)
  const user = await currentUser();
  if (!user) {
    // you could redirect to /sign-in or just show all as “Add to Cart”
  }
  const email = user?.emailAddresses[0]?.emailAddress ?? "";

  // 2️⃣ Fetch products LEFT JOIN cart_item ON (email & productId)
  const rows = await db
    .select({
      id:      Product.id,
      name:    Product.name,
      description: Product.description,
      price:   Product.price,
      imageUrl: Product.imageUrl,
      category: Product.category,
      createdAt: Product.createdAt,
      cartId:  CartItem.id,   // will be null if not in cart
    })
    .from(Product)
    .leftJoin(
      CartItem,
      and(
        eq(CartItem.email, email),
        eq(CartItem.productId, Product.id)
      )
    );

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Our Products</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {rows.map((p) => (
          <div
            key={p.id}
            className="border border-gray-200 rounded-xl overflow-hidden flex flex-col shadow-sm"
          >
            <div className="relative h-48 w-full">
              <Image
                src={p.imageUrl}
                alt={p.name}
                fill
                className="object-cover"
              />
            </div>
            <div className="p-4 flex-1 flex flex-col">
              <h2 className="text-lg font-semibold mb-2">{p.name}</h2>
              <p className="text-sm text-gray-600 flex-1">
                {p.description}
              </p>
              <div className="mt-4 flex items-center justify-between">
                <span className="text-xl font-bold">${p.price}</span>
                <AddToCartButton
                  productId={p.id}
                  initialInCart={p.cartId != null}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
