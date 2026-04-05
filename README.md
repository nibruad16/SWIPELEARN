# SwipeLearn

> Transform blog posts into TikTok-style swipeable Knowledge Cards. A mobile-first learning app for busy professionals.

## 🏗️ Architecture

```
SwipeLearn/
├── backend/          # FastAPI (Python) - API server
├── frontend/         # Flutter - Mobile app
├── docs/             # Documentation & DB schema
└── docker-compose.yml
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

### 2. Backend Setup
```bash
cd backend
cp .env.example .env
# Edit .env with your keys

pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs available at: `http://localhost:8000/docs`

### 3. Docker Setup (Alternative)
```bash
docker-compose up
```

### 4. Frontend Setup
```bash
cd frontend
flutter pub get
flutter run
```

## 📡 API Endpoints

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

## 🧩 Component Architecture

| Component | Pattern | Responsibility |
|-----------|---------|----------------|
| ContentScraper | Adapter | Fetch & extract blog content |
| SummarizerAI | Strategy | AI-powered summarization |
| TeacherTracker | Observer | Monitor blogs for new posts |
| KnowledgeCardUI | Composite | Card display widget |
| SwipeFeed | Iterator | Vertical swipe feed |
| FeedService | Service | Feed generation & card management |

## 🛠️ Tech Stack
- **Frontend**: Flutter
- **Backend**: FastAPI (Python)
- **Database & Auth**: Supabase (PostgreSQL)
- **Background Jobs**: arq + Redis
- **AI Summarization**: OpenAI GPT-4o-mini
- **Containerization**: Docker

## 📄 License
Proprietary - All rights reserved.
