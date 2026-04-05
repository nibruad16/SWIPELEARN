-- =============================================
-- SwipeLearn Database Schema
-- Platform: Supabase (PostgreSQL)
-- =============================================

-- Enable UUID extension (already enabled in Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- 1. User Profiles
-- Extends Supabase Auth users with app-specific data
-- =============================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, display_name, avatar_url)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
        NEW.raw_user_meta_data->>'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- =============================================
-- 2. Teachers (Creators/Bloggers)
-- =============================================
CREATE TABLE IF NOT EXISTS teachers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    website_url TEXT NOT NULL,
    blog_rss_url TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(name, website_url)
);

CREATE INDEX idx_teachers_website ON teachers(website_url);

-- =============================================
-- 3. User-Teacher Relationships (Follows)
-- =============================================
CREATE TABLE IF NOT EXISTS user_teachers (
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES teachers(id) ON DELETE CASCADE,
    followed_at TIMESTAMPTZ DEFAULT NOW(),
    
    PRIMARY KEY (user_id, teacher_id)
);

CREATE INDEX idx_user_teachers_user ON user_teachers(user_id);
CREATE INDEX idx_user_teachers_teacher ON user_teachers(teacher_id);

-- =============================================
-- 4. Knowledge Cards
-- =============================================
CREATE TABLE IF NOT EXISTS knowledge_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    author TEXT,
    teacher_id UUID REFERENCES teachers(id) ON DELETE SET NULL,
    tl_dr TEXT NOT NULL,
    key_points JSONB NOT NULL DEFAULT '[]'::jsonb,
    steal_insight TEXT NOT NULL,
    raw_content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cards_teacher ON knowledge_cards(teacher_id);
CREATE INDEX idx_cards_created ON knowledge_cards(created_at DESC);
CREATE INDEX idx_cards_source_url ON knowledge_cards(source_url);

-- =============================================
-- 5. Saved Cards (User Bookmarks)
-- =============================================
CREATE TABLE IF NOT EXISTS saved_cards (
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    card_id UUID REFERENCES knowledge_cards(id) ON DELETE CASCADE,
    saved_at TIMESTAMPTZ DEFAULT NOW(),
    
    PRIMARY KEY (user_id, card_id)
);

CREATE INDEX idx_saved_user ON saved_cards(user_id);

-- =============================================
-- 6. Feed History (Seen Tracking)
-- =============================================
CREATE TABLE IF NOT EXISTS feed_history (
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    card_id UUID REFERENCES knowledge_cards(id) ON DELETE CASCADE,
    seen_at TIMESTAMPTZ DEFAULT NOW(),
    
    PRIMARY KEY (user_id, card_id)
);

CREATE INDEX idx_feed_history_user ON feed_history(user_id);

-- =============================================
-- Row Level Security (RLS) Policies
-- =============================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE teachers ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_teachers ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE feed_history ENABLE ROW LEVEL SECURITY;

-- Profiles: users can read/update their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Teachers: anyone authenticated can read, service role can write
CREATE POLICY "Authenticated users can view teachers" ON teachers
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Service role can manage teachers" ON teachers
    FOR ALL USING (auth.role() = 'service_role');

-- User-Teachers: users manage their own follows
CREATE POLICY "Users can view own follows" ON user_teachers
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can follow teachers" ON user_teachers
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can unfollow teachers" ON user_teachers
    FOR DELETE USING (auth.uid() = user_id);

-- Knowledge Cards: authenticated users can read, service role can write
CREATE POLICY "Authenticated users can view cards" ON knowledge_cards
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Service role can manage cards" ON knowledge_cards
    FOR ALL USING (auth.role() = 'service_role');

-- Saved Cards: users manage their own saves
CREATE POLICY "Users can view own saves" ON saved_cards
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can save cards" ON saved_cards
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can unsave cards" ON saved_cards
    FOR DELETE USING (auth.uid() = user_id);

-- Feed History: users manage their own history
CREATE POLICY "Users can view own history" ON feed_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can track seen cards" ON feed_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);
