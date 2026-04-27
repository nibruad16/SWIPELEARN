# 🏗️ Ride-Share Monorepo Architecture

Welcome! This repository demonstrates how to structure a robust system using a **Monorepo** approach. We've built a unified architecture containing four distinct Next.js frontend applications that all share a single central UI design system and interact with a shared backend Express service and SQLite database.

By the end of this guide, you will understand how to isolate domains into strict packages, manage shared dependencies (like global Tailwind v4 CSS), and orchestrate multiple applications simultaneously using Turborepo.

## 🎯 Architecture Overview

* **Frontends (`apps/*`):** `driver`, `customer`, `admin`, `call-center` (Next.js v15+)
* **Central Backend (`packages/api`):** A shared Express API service (Port 3005) demonstrating route and service abstraction.
* **Central Database (`packages/db`):** Drizzle ORM with Better-SQLite3, acting as the single source of truth for the database schema.
* **Central UI (`packages/ui`):** A shared React component library and centralized Tailwind v4 configuration.

---

## 🚀 Step-by-Step Implementation Guide

### Phase 1: Scaffold the Monorepo

We use Turborepo to manage our workspace, as it provides excellent caching and execution orchestration.

1. **Initialize the workspace:**
   ```bash
   npx create-turbo@latest ride-share-monorepo --use pnpm
   cd ride-share-monorepo

   # check to see if your workspace is set up correctly
   pnpm turbo run dev
   ```

2. **Restructure the frontend apps:**
   Turborepo creates `apps/web` and `apps/docs` by default. Remove them and generate our four system applications.
   ```bash
   cd apps
   Remove-Item -Recurse -Force docs, web
   npx create-next-app@latest driver --typescript --tailwind --eslint --app
   npx create-next-app@latest customer --typescript --tailwind --eslint --app
   npx create-next-app@latest admin --typescript --tailwind --eslint --app
   npx create-next-app@latest call-center --typescript --tailwind --eslint --app
   cd ..

   # check to see if your workspace is set up correctly 
   # you should see all apps running on different ports
   pnpm turbo run dev
   ```

### Phase 2: Configure the Central Database (`packages/db`)

Creating a dedicated database package ensures that any service needing database access uses a strictly typed, single source of truth.

1. **Setup the shared database package:**
   ```bash
   pnpm dlx turbo gen workspace --name db --type package
   # don't configure any dependancies yet
   ```

2. **Add Dependencies: (`packages/db/package.json`):**
   ```json
   {
     "name": "@repo/db",
     "version": "0.0.0",
     "main": "./src/index.ts",
     "types": "./src/index.ts",
     "scripts": {
       "db:push": "drizzle-kit push",
       "build": "tsc --noEmit"
     },
     "dependencies": {
       "drizzle-orm": "^0.39.0",
       "better-sqlite3": "^11.0.0"
     },
     "devDependencies": {
       "drizzle-kit": "^0.30.0",
       "@types/better-sqlite3": "^7.6.0",
       "typescript": "^5"
     }
   }
   ```
   

3. **Define the Schema (`packages/db/src/schema.ts`):**
   ```typescript
   import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";

   export const clickStats = sqliteTable("click_stats", {
       app: text("app").primaryKey(),
       count: integer("count").notNull().default(0),
   });
   ```

3. **Export the Client (`packages/db/src/index.ts`):**
   ```typescript
   import { drizzle } from "drizzle-orm/better-sqlite3";
   import Database from "better-sqlite3";
   import * as schema from "./schema";
   import path from "path";

   const DB_PATH = path.resolve(process.cwd(), "../../clicks.db");

   const sqlite = new Database(DB_PATH);
   export const db = drizzle(sqlite, { schema });
   export { clickStats } from "./schema";
   export { sql } from "drizzle-orm"; // Export sql directly for ease of use
   ```

4. **Setup Drizzle Configuration at Default Location (`packages/db/drizzle.config.ts`):**
   ```typescript
   import { defineConfig } from "drizzle-kit";

   export default defineConfig({
       schema: "./src/schema.ts",
       out: "./drizzle",
       dialect: "sqlite",
       dbCredentials: { url: "../../clicks.db" },
   });
   ```

5. **Initialize the database:** Run `pnpm install` & `pnpm db:push` inside `packages/db` to create the SQLite file.

### Phase 3: Build the Central API Package - Manual Creation(`packages/api`)

For this demonstration, we will build our backend as a shared package. This is a great way to learn how to modularize logic into services and routes. 

1. **Initialize the API Package:**
   ```bash
   cd ../../packages
   mkdir api
   cd api
   pnpm init
   pnpm add express cors
   pnpm add -D typescript @types/express @types/cors tsx
   ```

2. **Link the Database:**
   Update `packages/api/package.json` to include our local DB package and a dev script:
   ```json
   {
     "name": "@repo/api",
     "main": "./src/server.ts",
     "scripts": {
       "dev": "tsx watch src/server.ts",
       "build": "tsc"
     },
     "dependencies": {
      --> "@repo/db": "workspace:*",
       "cors": "^2.8.5",
       "express": "^4.18.2"
     }
   }
   ```

3. **Create the Services (`packages/api/services.ts`):**
   Haul all DB Operations here. [ THE DATABASE COMPONENT IS CONTAINMENTED CONNCETED TO API ]
   ```typescript
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
   ```

3. **Create the Routes (`packages/api/src/routes.ts`):**
   ```typescript
   import { Router } from "express";
   import { getAllClicks, incrementClick } from "./services";

   const router = Router();

   router.get("/clicks", async (req, res) => {
       const data = await getAllClicks();
       res.json(data);
   });

   router.post("/clicks", async (req, res) => {
       const { appName } = req.body;
       try {
           await incrementClick(appName);
           res.json({ success: true });
       } catch (e) {
           res.status(400).json({ error: (e as Error).message });
       }
   });

   export default router;
   ```

4. **Create the Server (`packages/api/src/server.ts`):**
   ```typescript
   import express from "express";
   import cors from "cors";
   import clickRouter from "./routes";

   const app = express();
   app.use(cors());
   app.use(express.json());

   app.use("/api", clickRouter);

   const PORT = 3005;
   app.listen(PORT, () => {
       console.log(`🚀 Central API running on http://localhost:${PORT}/api`);
   });
   ```

### Phase 4: Configure the Central UI & Tailwind CSS (`packages/ui`)

We centralized **Tailwind CSS v4** styling within the `@repo/ui` package so all apps share the exact same configuration and class library.

1. **UI Package Dependencies (`packages/ui/package.json`):**
   Move Tailwind to `dependencies` so apps can compile it with Turbopack. Add the `globals.css` export.
   ```json
   {
     "name": "@repo/ui",
     "exports": {
       "./globals.css": "./src/globals.css",
       "./button": "./src/button.tsx"
     },
     "dependencies": {
       "@tailwindcss/postcss": "^4",
       "postcss": "^8.5.10",
       "tailwindcss": "^4",
       "react": "^19.2.0",
       "react-dom": "^19.2.0"
     }
   }
   ```

2. **Centralize Tailwind Configuration (`packages/ui/src/globals.css`):**
   Notice the `@source` tags which instruct Tailwind to magically scan components in apps and the UI package.
   ```css
   @import "tailwindcss";

   @source "./**/*.{js,ts,jsx,tsx}";
   @source "../../../apps/*/app/**/*.{js,ts,jsx,tsx}";

   :root {
     --background: #ffffff;
     --foreground: #171717;
   }

   @theme inline {
     --color-background: var(--background);
     --color-foreground: var(--foreground);
     --font-sans: var(--font-geist-sans);
     --font-mono: var(--font-geist-mono);
   }

   body {
     background: var(--background);
     color: var(--foreground);
     font-family: Arial, Helvetica, sans-serif;
   }
   ```

3. **Build the Premium 3D Button (`packages/ui/src/button.tsx`):**
   ```tsx
   import * as React from "react";

   interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
       appName: string;
       children: React.ReactNode;
   }

   export const SharedButton = ({ appName, children, ...props }: ButtonProps) => {
       return (
           <button
               className="group relative px-8 py-3 bg-blue-600 text-white rounded-full font-bold tracking-wide shadow-[0_5px_0_0_rgba(29,78,216,1)] hover:shadow-[0_2px_0_0_rgba(29,78,216,1)] hover:translate-y-[3px] active:translate-y-[5px] active:shadow-none transition-all duration-75 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
               {...props}
           >
               <span className="relative flex items-center justify-center gap-2">
                   {children}
               </span>
           </button>
       );
   };
   ```

### Phase 5: Wire the Frontend Applications

Apply this logic to `apps/driver`, and then replicate it across `customer`, `admin`, and `call-center`.

1. **Delete local `globals.css`** inside `apps/[app-name]/app/globals.css`.
2. **Update `layout.tsx`** to use the shared UI CSS:
   ```tsx
   import "@repo/ui/globals.css";
   ```

3. **Establish Environment Variable:**
   Create `.env.local` in the root of the workspace.
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:3005/api
   ```

4. **Implement the Dashboard (`apps/[app-name]/app/page.tsx`):**
   ```tsx
   'use client';

   import { useEffect, useState } from 'react';
   import { SharedButton } from '@repo/ui/button';

   const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3005/api';

   export default function AppDashboard() {
     const [stats, setStats] = useState([]);
     const APP_NAME = 'Driver App'; // Set strictly to one of the valid apps

     const fetchStats = async () => {
       const res = await fetch(`${API_URL}/clicks`);
       setStats(await res.json());
     };

     useEffect(() => { fetchStats(); }, []);

     const handleClick = async () => {
       await fetch(`${API_URL}/clicks`, {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ appName: APP_NAME }),
       });
       fetchStats();
     };

     return (
       <div className="p-8 max-w-2xl mx-auto font-sans">
         <h1 className="text-2xl font-bold mb-6">{APP_NAME} Dashboard</h1>

         <div className="mb-8">
           <SharedButton appName={APP_NAME} onClick={handleClick}>
             Trigger Central Action
           </SharedButton>
         </div>

         <div className="border p-4 rounded-md bg-gray-50 text-gray-900">
           <h2 className="text-lg font-semibold mb-4">System-Wide Telemetry</h2>
           <ul>
             {stats.map((stat: any) => (
               <li key={stat.appName} className="flex justify-between py-2 border-b last:border-0">
                 <span>{stat.appName}</span>
                 <span className="font-mono">{stat.clicks} clicks</span>
               </li>
             ))}
           </ul>
         </div>
       </div>
     );
   }
   ```

### 🏃‍♂️ Running the System

Ensure Turborepo runs the DB, API, and Frontends concurrently using `turbo.json`. Include `"@repo/api#dev"` in your pipeline if needed.

From the root of your monorepo, run:
```bash
pnpm install
pnpm dev
```

Turborepo will spin up the Express API on port 3005 and all four Next.js applications on ports 3000-3004. Open multiple tabs, click the shared 3D blue button in any app, and watch the central database update the telemetry across your entire monorepo ecosystem instantly!