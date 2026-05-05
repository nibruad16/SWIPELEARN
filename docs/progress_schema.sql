-- ============================================================
-- SwipeLearn: Progress & Gamification Schema Migration
-- ============================================================
-- Run this in your Supabase SQL Editor after schema.sql
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- 1. user_progress — one row per user
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_progress (
    user_id         UUID        PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    xp              INTEGER     NOT NULL DEFAULT 0 CHECK (xp >= 0),
    streak_days     INTEGER     NOT NULL DEFAULT 0 CHECK (streak_days >= 0),
    longest_streak  INTEGER     NOT NULL DEFAULT 0 CHECK (longest_streak >= 0),
    cards_read      INTEGER     NOT NULL DEFAULT 0 CHECK (cards_read >= 0),
    last_active_date DATE,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_user_progress_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_user_progress_updated_at ON user_progress;
CREATE TRIGGER trg_user_progress_updated_at
    BEFORE UPDATE ON user_progress
    FOR EACH ROW EXECUTE FUNCTION update_user_progress_updated_at();

-- ────────────────────────────────────────────────────────────
-- 2. user_badges — many-to-one per user
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_badges (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    badge_id    TEXT        NOT NULL,                 -- e.g. "streak_7"
    earned_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, badge_id)
);

-- ────────────────────────────────────────────────────────────
-- 3. Indexes
-- ────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_user_progress_xp       ON user_progress (xp DESC);
CREATE INDEX IF NOT EXISTS idx_user_badges_user_id    ON user_badges (user_id);
CREATE INDEX IF NOT EXISTS idx_user_badges_badge_id   ON user_badges (badge_id);

-- ────────────────────────────────────────────────────────────
-- 4. Row-Level Security
-- ────────────────────────────────────────────────────────────
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_badges   ENABLE ROW LEVEL SECURITY;

-- Users can read their own progress; service role bypasses RLS for writes
CREATE POLICY "Users read own progress"
    ON user_progress FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users read own badges"
    ON user_badges FOR SELECT
    USING (auth.uid() = user_id);

-- Allow service_role full access (API server uses service key)
CREATE POLICY "Service role full access to progress"
    ON user_progress FOR ALL
    USING (true);

CREATE POLICY "Service role full access to badges"
    ON user_badges FOR ALL
    USING (true);
