import { db, clickStats, sql } from "@repo/db";

const validApps = ["Driver App", "Customer App", "Admin App", "Call Center App"] as const;

export async function getAllClicks() {
    const stats = await db.select().from(clickStats);
    return validApps.map((app) => ({
        appName: app,
        clicks: stats.find((s) => s.app === app)?.count ?? 0,
    }));
}

export async function incrementClick(app: string) {
    if (!validApps.includes(app as any)) throw new Error("Invalid app");
    await db
        .insert(clickStats)
        .values({ app, count: 1 })
        .onConflictDoUpdate({
            target: clickStats.app,
            set: { count: sql`${clickStats.count} + 1` },
        });
}