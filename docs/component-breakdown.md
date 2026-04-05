# SwipeLearn — Component Breakdown

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Flutter Frontend                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │AuthScreen│ │SwipeFeed │ │AddURLSheet│ │Teachers│ │
│  └────┬─────┘ └────┬─────┘ └────┬──────┘ └───┬────┘ │
│       │             │            │             │      │
│       └─────────────┼────────────┼─────────────┘      │
│                     │ API Service Layer               │
└─────────────────────┼────────────────────────────────┘
                      │ HTTPS / JWT
┌─────────────────────┼────────────────────────────────┐
│                FastAPI Backend                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │
│  │Auth Route│ │Cards Route│ │Feed Route│ │Teachers│  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘  │
│       │             │            │            │       │
│  ┌────┴─────────────┴────────────┴────────────┴────┐ │
│  │              Service Layer                       │ │
│  │  ContentScraper → SummarizerAI → FeedService    │ │
│  │  TeacherTracker                                  │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────┬────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───┴───┐      ┌─────┴─────┐    ┌──────┴──────┐
│Supabase│      │   Redis    │    │  OpenAI API  │
│DB+Auth │      │(Job Queue) │    │ (GPT-4o-mini)│
└────────┘      └───────────┘    └──────────────┘
```

## Component Registry

### Backend Components

| # | Component | File | Pattern | Input | Output |
|---|-----------|------|---------|-------|--------|
| 1 | AuthComponent | `routers/auth.py` | Dependency Injection | Email/OAuth token | JWT session |
| 2 | ContentScraper | `services/scraper.py` | Adapter | URL string | Clean text + metadata |
| 3 | SummarizerAI | `services/summarizer.py` | Strategy | Clean text | KnowledgeCard JSON |
| 4 | TeacherTracker | `services/teacher_tracker.py` | Observer | Blog URL | New post alerts |
| 5 | FeedService | `services/feed_service.py` | Service Layer | User ID | Paginated cards |

### Data Models

| Model | File | Fields |
|-------|------|--------|
| KnowledgeCard | `models/card.py` | title, author, tl_dr, key_points, steal_insight |
| Teacher | `models/teacher.py` | name, website_url, blog_rss_url, posts_count |
| User | `models/user.py` | email, display_name, avatar_url |

### Frontend Components (Planned)

| # | Component | File | Pattern |
|---|-----------|------|---------|
| 1 | KnowledgeCardUI | `widgets/knowledge_card_widget.dart` | Composite |
| 2 | SwipeFeed | `widgets/swipe_feed.dart` | Iterator |
| 3 | TeacherCard | `widgets/teacher_card.dart` | Composite |
| 4 | AddURLSheet | `screens/add_url/add_url_screen.dart` | — |
| 5 | BottomNav | `widgets/bottom_nav.dart` | — |

## Data Flow: URL → Knowledge Card

```
User pastes URL
      │
      ▼
  URLExtractor (validate)
      │
      ▼
  ContentScraper (fetch + extract)
      │  ├── httpx: HTTP request
      │  ├── readability: main content extraction
      │  └── BeautifulSoup: HTML cleanup
      │
      ▼
  SummarizerAI (GPT-4o-mini)
      │  ├── System prompt: Knowledge Card schema
      │  ├── JSON response format enforced
      │  └── Temperature: 0.3 (factual)
      │
      ▼
  FeedService.store_card() → Supabase DB
      │
      ▼
  Knowledge Card returned to user
```

## Design Pattern Justification

| Pattern | Component | Why This Pattern? |
|---------|-----------|-------------------|
| **Strategy** | SummarizerAI | Swap GPT-4o-mini for Claude/local LLM without changing calling code |
| **Adapter** | ContentScraper | Different websites need different scraping approaches |
| **Observer** | TeacherTracker | Background monitoring that triggers actions on new posts |
| **Dependency Injection** | Auth | Middleware injects user context into every protected endpoint |
| **Composite** | KnowledgeCardUI | Card is composed of Header + Body + Footer sub-widgets |
