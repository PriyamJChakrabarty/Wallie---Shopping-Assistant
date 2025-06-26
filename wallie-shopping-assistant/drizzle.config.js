/**@type {import ("drizzle-kit").Config} */
export default {
  dialect: "postgresql",
  schema: "./utils/schema.js",
  dbCredentials: {
    url: "postgresql://neondb_owner:npg_frg6YLiSB0Pa@ep-small-tree-a4fb2q8x-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
  },
};
