// app/api/voice-cart/route.js
import { NextResponse } from "next/server";
import { db } from "@/utils/db";
import { CartItem, Product } from "@/utils/schema";
import { eq } from "drizzle-orm";

export async function POST(req) {
  try {
    const { productId, email, quantity = 1 } = await req.json();
    
    if (!productId || !email) {
      return NextResponse.json(
        { error: "Product ID and email are required" },
        { status: 400 }
      );
    }

    // Check if product exists
    const product = await db
      .select()
      .from(Product)
      .where(eq(Product.id, productId))
      .limit(1);

    if (product.length === 0) {
      return NextResponse.json(
        { error: "Product not found" },
        { status: 404 }
      );
    }

    // Check if item already exists in cart
    const existingItem = await db
      .select()
      .from(CartItem)
      .where(eq(CartItem.productId, productId))
      .where(eq(CartItem.email, email))
      .limit(1);

    if (existingItem.length > 0) {
      // Update quantity if item exists
      await db
        .update(CartItem)
        .set({ quantity: existingItem[0].quantity + quantity })
        .where(eq(CartItem.id, existingItem[0].id));
    } else {
      // Insert new item
      await db.insert(CartItem).values({ 
        productId, 
        email, 
        quantity 
      });
    }

    return NextResponse.json({ 
      success: true, 
      message: "Item added to cart successfully",
      product: product[0]
    });
  } catch (error) {
    console.error("Error adding to cart:", error);
    return NextResponse.json(
      { error: "Failed to add item to cart" },
      { status: 500 }
    );
  }
}
