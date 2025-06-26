// app/api/cart/route.js
import { NextResponse } from "next/server";
import { db } from "@/utils/db";
import { CartItem, Product } from "@/utils/schema";
import { currentUser } from "@clerk/nextjs/server"; // ← correct import
import { eq } from "drizzle-orm";

export async function GET() {
  const user = await currentUser();
  if (!user) {
    return NextResponse.json([], { status: 401 });
  }
  const email = user.emailAddresses[0].emailAddress;

  // Join CartItem → Product so we get product fields in one request
  const items = await db
    .select({
      cartId: CartItem.id,
      quantity: CartItem.quantity,
      productId: CartItem.productId,
      name: Product.name,
      price: Product.price,
      imageUrl: Product.imageUrl,
    })
    .from(CartItem)
    .leftJoin(Product, eq(Product.id, CartItem.productId))
    .where(eq(CartItem.email, email));

  return NextResponse.json(items);
}

export async function POST(req) {
  const user = await currentUser();
  if (!user) {
    console.log("🚫 Not signed in");
    return NextResponse.json({ error: "Not signed in" }, { status: 401 });
  }
  const { productId } = await req.json();
  const email = user.emailAddresses[0]?.emailAddress;

  console.log(`🛒 Adding product ${productId} to cart for ${email}`);
  await db.insert(CartItem).values({ productId, email, quantity: 1 });
  console.log("✅ Inserted successfully");
  return NextResponse.json({ success: true });
}

export async function DELETE(req) {
  const user = await currentUser();
  if (!user)
    return NextResponse.json({ error: "Not signed in" }, { status: 401 });
  const { cartId } = await req.json();
  const email = user.emailAddresses[0].emailAddress;

  // only delete if it belongs to this user
  await db
    .delete(CartItem)
    .where(eq(CartItem.id, cartId), eq(CartItem.email, email));

  return NextResponse.json({ success: true });
}
