# SwipeLearn — Product Requirement Document (PRD)

## 1. The Problem

Learning from high-quality blogs is slow, unfocused, unorganized, and not designed for modern, mobile-first habits. People, especially in tech, design, and entrepreneurship, want to "steal like an artist" and absorb key ideas from top creators, developers, and entrepreneurs. However, they don't have the time to read long, 2,000-word articles in an organized, interactive way.

Users are drowning in content and lack a tool that can surface the signal from the noise quickly and engagingly. Additionally, it's hard to consistently follow the creators, developers, and entrepreneurs they care about, as these individuals often share information through multiple channels in different formats.

## 2. The Solution

A mobile-first learning app that transforms blog posts from any creator into a "TikTok-style" feed of swipe-able, summarized knowledge cards. It lets users follow specific creators, automatically gets their new posts, and delivers concentrated insights in a format that is as addictive as social media but 100% educational.

## 3. Target User

- **Software Engineers**: Who need to stay updated on new frameworks, techniques, and architectures.
- **UI/UX Designers**: Who follow thought leaders for trends, case studies, and design principles.
- **AI Learners & Creators**: Who need to consume the latest research, tool updates, and creative prompts.
- **Students & Lifelong Learners**: Who want a more efficient way to learn from the best minds on the internet.

## 4. The MVP: Core Features (Must-Haves)

### Feature 1: Knowledge Card Feed
- Blog Title, Source/Author, 1-sentence TL;DR, 3–5 Key Bullet Points, 1 "Steal Like an Artist" Insight
- Swipe Up to next card, Tap for details, Save button

### Feature 2: Add by URL + Optional Teacher Tracking
- Paste URL → Scrape → AI Summarize → Knowledge Card
- Optionally save creator as Teacher for auto-updates

### Feature 3: Teachers Management Tab
- View/manage followed creators
- Remove teachers, view post counts

### Feature 4: User Authentication & Saved List
- Email/password + Google Sign-In via Supabase Auth
- Saved cards persist across devices

## 5. Tech Stack

- **Mobile App (Frontend)**: Flutter
- **Backend API**: FastAPI (Python)
- **Database & Auth**: Supabase
- **Background Jobs**: arq + Redis
- **AI Summarization**: OpenAI API (GPT-4o-mini)

## 6. Key Success Metrics (First 30 Days)

| Metric | Target |
|--------|--------|
| Activation | 50% follow ≥1 creator on day 1 |
| Engagement | 15+ cards swiped/day |
| Retention | 20% Day-7 retention |
| Core Value | 30% DAU paste a URL |
