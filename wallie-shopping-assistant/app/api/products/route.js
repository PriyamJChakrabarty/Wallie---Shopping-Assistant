// app/api/products/route.js
import { NextResponse } from "next/server";
import { db } from "@/utils/db";
import { Product } from "@/utils/schema";

export async function GET() {
  try {
    // Fetch all products from database
    const products = await db
      .select({
        id: Product.id,
        name: Product.name,
        description: Product.description,
        price: Product.price,
        imageUrl: Product.imageUrl,
        category: Product.category,
      })
      .from(Product);

    return NextResponse.json(products);
  } catch (error) {
    console.error("Error fetching products:", error);
    return NextResponse.json(
      { error: "Failed to fetch products" },
      { status: 500 }
    );
  }
}
