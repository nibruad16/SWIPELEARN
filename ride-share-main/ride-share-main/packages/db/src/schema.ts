import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";

export const clickStats = sqliteTable("click_stats", {
    app: text("app").primaryKey(),
    count: integer("count").notNull().default(0),
});