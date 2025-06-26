import {
  pgTable,
  serial,
  varchar,
  text,
  timestamp,
  numeric,
} from "drizzle-orm/pg-core";

export const Product = pgTable("product", {
  id: serial("id").primaryKey(),
  name: varchar("name", { length: 255 }).notNull(),
  description: text("description"),
  price: numeric("price", { precision: 10, scale: 2 }).notNull(),
  imageUrl: text("imageUrl").notNull(),
  category: varchar("category", { length: 100 }),
  createdAt: timestamp("createdAt", { withTimezone: true }).defaultNow(),
});
