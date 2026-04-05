# SwipeLearn — API Specification

## Base URL
```
Development: http://localhost:8000
Production:  https://api.swipelearn.app
```

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <supabase_jwt_token>
```

---

## Endpoints

### Auth

#### POST /auth/signup
Create a new account with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123",
  "display_name": "John Doe"  // optional
}
```

**Response (200):**
```json
{
  "message": "User created successfully",
  "user_id": "uuid-here",
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

#### POST /auth/login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com"
  }
}
```

#### POST /auth/google
Login with Google OAuth ID token.

**Request:**
```json
{
  "id_token": "google_id_token_here"
}
```

---

### Knowledge Cards

#### POST /cards/summarize 🔒
Summarize a blog URL into a Knowledge Card.

**Request:**
```json
{
  "url": "https://blog.example.com/article",
  "save_teacher": true  // optional, default false
}
```

**Response (200):**
```json
{
  "card": {
    "id": "uuid",
    "source_url": "https://blog.example.com/article",
    "title": "How to Build Better APIs",
    "author": "Jane Dev",
    "tl_dr": "Focus on developer experience by designing APIs that are predictable, well-documented, and versioned.",
    "key_points": [
      "Use consistent naming conventions across all endpoints",
      "Version your API from day one to avoid breaking changes",
      "Provide detailed error messages with actionable suggestions",
      "Document every endpoint with request/response examples"
    ],
    "steal_insight": "Add a 'debug' query parameter that returns extra metadata about the request processing — developers will love you for it.",
    "created_at": "2026-03-17T10:00:00Z"
  },
  "teacher_name": "Jane Dev",
  "message": "Successfully summarized",
  "is_new": true
}
```

#### GET /cards/{card_id} 🔒
Get a single Knowledge Card by ID.

#### POST /cards/{card_id}/save 🔒
Save a card to the user's list.

#### DELETE /cards/{card_id}/save 🔒
Remove a card from saved list.

---

### Feed

#### GET /feed 🔒
Get the user's personalized Knowledge Card feed.

**Query Parameters:**
- `page` (int, default 1)
- `page_size` (int, default 20, max 50)

**Response (200):**
```json
{
  "cards": [...],
  "page": 1,
  "page_size": 20,
  "has_more": true
}
```

#### GET /feed/saved 🔒
Get the user's saved cards.

#### POST /feed/seen/{card_id} 🔒
Mark a card as seen (for feed algorithm).

---

### Teachers

#### GET /teachers 🔒
List all followed teachers.

#### POST /teachers 🔒
Follow a new teacher.

**Request:**
```json
{
  "name": "Dan Abramov",
  "website_url": "https://overreacted.io",
  "blog_rss_url": null,  // auto-discovered if null
  "avatar_url": null
}
```

#### DELETE /teachers/{teacher_id} 🔒
Unfollow a teacher.

#### GET /teachers/{teacher_id}/cards 🔒
Get all cards from a specific teacher.

---

## Error Responses

All errors follow this format:
```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad request (validation error) |
| 401 | Not authenticated |
| 404 | Resource not found |
| 422 | Unprocessable (e.g., can't scrape URL) |
| 500 | Internal server error |
