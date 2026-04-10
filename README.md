# SwipeLearn

> Transform blog posts into TikTok-style swipeable Knowledge Cards. A mobile-first learning app for busy professionals.

## 🏗️ Monorepo Architecture

```
SwipeLearn/
├── packages/
│   ├── core/             # Shared Pydantic models & schemas
│   ├── services/         # Business logic components
│   ├── api/              # FastAPI server (thin orchestration)
│   └── mobile/           # Flutter mobile app
├── docs/                 # Documentation & DB schema
├── docker-compose.yml    # Container orchestration
└── Makefile              # Dev task runner
```

### Package Dependency Graph

```
  ┌──────────┐
  │  mobile  │  (Flutter — standalone)
  └──────────┘

  ┌──────────┐     ┌────────────┐     ┌──────────┐
  │   api    │ ──▶ │  services  │ ──▶ │   core   │
  └──────────┘     └────────────┘     └──────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Flutter SDK 3.x
- Docker & Docker Compose
- Supabase account
- OpenAI API key

### 1. Set up Supabase
1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run `docs/schema.sql`
3. Enable Google Auth in Authentication > Providers
4. Copy your project URL, anon key, and service key

### 2. Install All Packages
```bash
make install
```

### 3. Backend Setup
```bash
cd packages/api
cp .env.example .env
# Edit .env with your keys

make dev-api
```

API docs available at: `http://localhost:8000/docs`

### 4. Docker Setup (Alternative)
```bash
make docker-up
```

### 5. Mobile Setup
```bash
make dev-mobile
```

## 📦 Packages

### `packages/core` — Shared Models
Pydantic schemas used across all backend packages.

```python
from swipelearn_core.models.card import KnowledgeCard
from swipelearn_core.models.teacher import Teacher
```

### `packages/services` — Business Logic
Independent service components with clean design patterns.

| Component | Pattern | Responsibility |
|-----------|---------|----------------|
| ContentScraper | Adapter | Fetch & extract blog content |
| SummarizerAI | Strategy | AI-powered summarization |
| TeacherTracker | Observer | Monitor blogs for new posts |
| FeedService | Service | Feed generation & card management |
| ContentPipeline | Orchestrator | URL → Knowledge Card pipeline |

### `packages/api` — FastAPI Server
Thin REST API layer that wires together services.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Email/password signup |
| POST | `/auth/login` | Email/password login |
| POST | `/auth/google` | Google OAuth |
| GET | `/feed` | Knowledge card feed |
| POST | `/cards/summarize` | Summarize a URL |
| GET | `/cards/{id}` | Get card details |
| POST | `/cards/{id}/save` | Save card |
| DELETE | `/cards/{id}/save` | Unsave card |
| GET | `/feed/saved` | Saved cards |
| GET | `/teachers` | List followed teachers |
| POST | `/teachers` | Follow a teacher |
| DELETE | `/teachers/{id}` | Unfollow teacher |

### `packages/mobile` — Flutter App
Mobile-first UI with swipeable card feed.

## 🛠️ Tech Stack
- **Frontend**: Flutter
- **Backend**: FastAPI (Python)
- **Database & Auth**: Supabase (PostgreSQL)
- **Background Jobs**: arq + Redis
- **AI Summarization**: OpenAI GPT-4o-mini
- **Containerization**: Docker

## 📄 License
Proprietary - All rights reserved.
