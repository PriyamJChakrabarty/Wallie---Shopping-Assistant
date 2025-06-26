const { db } = require("../utils/db");
const { Product } = require("../utils/schema");

async function seed() {
  const now = new Date().toISOString();
  const products = [
    {
      id: 1,
      name: "Wireless Headphones",
      description: "High-quality wireless headphones with noise cancellation.",
      price: 199.99,
      imageUrl: "/products/headphones.png",
      category: "Electronics",
      createdAt: now,
    },
    {
      id: 2,
      name: "Smart Watch",
      description: "Track your fitness and get notifications on the go.",
      price: 149.99,
      imageUrl: "/products/watch.png",
      category: "Wearables",
      createdAt: now,
    },
    {
      id: 3,
      name: "Bluetooth Speaker",
      description: "Portable speaker with deep bass and crisp sound.",
      price: 89.99,
      imageUrl: "/products/speaker.png",
      category: "Audio",
      createdAt: now,
    },
    {
      id: 4,
      name: "Gaming Mouse",
      description: "Ergonomic design with customizable DPI settings.",
      price: 59.99,
      imageUrl: "/products/mouse.png",
      category: "Gaming",
      createdAt: now,
    },
    {
      id: 5,
      name: "Backpack",
      description: "Durable backpack perfect for travel and daily use.",
      price: 69.99,
      imageUrl: "/products/backpack.png",
      category: "Accessories",
      createdAt: now,
    },
    {
      id: 6,
      name: "LED Desk Lamp",
      description: "Modern desk lamp with adjustable brightness.",
      price: 39.99,
      imageUrl: "/products/lamp.png",
      category: "Home",
      createdAt: now,
    },
    {
      id: 7,
      name: "Running Shoes",
      description: "Comfortable and lightweight running shoes.",
      price: 129.99,
      imageUrl: "/products/shoes.png",
      category: "Footwear",
      createdAt: now,
    },
    {
      id: 8,
      name: "Wireless Charger",
      description: "Fast wireless charging pad compatible with all devices.",
      price: 29.99,
      imageUrl: "/products/charger.png",
      category: "Electronics",
      createdAt: now,
    },
    {
      id: 9,
      name: "Notebook",
      description: "Hardcover notebook with premium quality paper.",
      price: 14.99,
      imageUrl: "/products/notebook.png",
      category: "Stationery",
      createdAt: now,
    },
    {
      id: 10,
      name: "Sunglasses",
      description: "Stylish sunglasses with UV protection.",
      price: 24.99,
      imageUrl: "/products/sunglass.png",
      category: "Fashion",
      createdAt: now,
    },
  ];

  try {
    await db.insert(Product).values(products);
    console.log("🌱 Seed data inserted successfully!");
  } catch (err) {
    console.error("❌ Error inserting seed data:", err);
  }
}

seed();
