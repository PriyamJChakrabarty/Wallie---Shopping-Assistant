// components/Products.jsx
import React from "react";
import Image from "next/image";
import { db } from "@/utils/db";
import { Product } from "@/utils/schema";

//fetch products from db
async function getProducts() {
  return await db.select().from(Product);
}
export default async function Products() {
  const products = await getProducts();

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Our Products</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {products.map((p) => (
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
              <p className="text-sm text-gray-600 flex-1">{p.description}</p>
              <div className="mt-4 flex items-center justify-between">
                <span className="text-xl font-bold">${p.price}</span>
                <button className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
                  Add to Cart
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
