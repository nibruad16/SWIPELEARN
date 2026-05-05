import 'package:flutter/material.dart';
import 'package:swipelearn/core/theme/app_theme.dart';
import 'package:swipelearn/core/providers/progress_provider.dart';
import 'package:swipelearn/models/progress.dart';

/// ProfileScreen — Shows the user's XP, level, streak, badges, and leaderboard.
/// Accessed via the Profile tab in BottomNav (index 4).

class ProfileScreen extends StatefulWidget {
  final ProgressProvider progressProvider;

  const ProfileScreen({super.key, required this.progressProvider});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      widget.progressProvider.loadProgress();
      widget.progressProvider.loadLeaderboard();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.progressProvider,
      builder: (context, _) {
        final provider = widget.progressProvider;
        return Scaffold(
          backgroundColor: AppColors.background,
          body: CustomScrollView(
            slivers: [
              _buildAppBar(provider),
              if (provider.isLoading)
                const SliverFillRemaining(
                  child: Center(
                    child: CircularProgressIndicator(color: AppColors.primary),
                  ),
                )
              else if (provider.progress != null) ...[
                SliverToBoxAdapter(child: _buildStatsRow(provider.progress!)),
                SliverToBoxAdapter(child: _buildLevelCard(provider.progress!)),
                SliverToBoxAdapter(child: _buildTabBar()),
                SliverFillRemaining(
                  hasScrollBody: true,
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _BadgesTab(progress: provider.progress!),
                      _LeaderboardTab(provider: provider),
                    ],
                  ),
                ),
              ] else
                const SliverFillRemaining(
                  child: Center(
                    child: Text(
                      'Could not load progress.',
                      style: TextStyle(color: AppColors.textMuted),
                    ),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  // ─── App Bar ───
  SliverAppBar _buildAppBar(ProgressProvider provider) {
    return SliverAppBar(
      expandedHeight: 160,
      floating: false,
      pinned: true,
      backgroundColor: AppColors.background,
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF1A1A3A), AppColors.background],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  Row(
                    children: [
                      // Avatar circle
                      Container(
                        width: 56,
                        height: 56,
                        decoration: BoxDecoration(
                          gradient: AppColors.primaryGradient,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: AppColors.primary.withOpacity(0.4),
                              blurRadius: 16,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Center(
                          child: Text(
                            'L${provider.progress?.level ?? 1}',
                            style: const TextStyle(
                              fontFamily: 'Inter',
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'My Progress',
                            style: TextStyle(
                              fontFamily: 'Inter',
                              fontSize: 22,
                              fontWeight: FontWeight.w800,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          Text(
                            provider.progress != null
                                ? '${provider.progress!.streakDays} day streak 🔥'
                                : 'Loading…',
                            style: const TextStyle(
                              fontFamily: 'Inter',
                              fontSize: 13,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  // ─── Stats Row ───
  Widget _buildStatsRow(UserProgress p) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
      child: Row(
        children: [
          _StatChip(label: 'XP', value: '${p.xp}', icon: Icons.bolt_rounded, color: AppColors.accentWarm),
          const SizedBox(width: 12),
          _StatChip(label: 'Cards', value: '${p.cardsRead}', icon: Icons.style_rounded, color: AppColors.secondary),
          const SizedBox(width: 12),
          _StatChip(label: 'Best Streak', value: '${p.longestStreak}d', icon: Icons.local_fire_department_rounded, color: AppColors.accent),
        ],
      ),
    );
  }

  // ─── Level Card ───
  Widget _buildLevelCard(UserProgress p) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: AppColors.surfaceBorder),
          boxShadow: [
            BoxShadow(
              color: AppColors.primary.withOpacity(0.08),
              blurRadius: 24,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Level ${p.level}',
                  style: const TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textPrimary,
                  ),
                ),
                Text(
                  '${p.xp} / ${p.xpForNextLevel} XP',
                  style: const TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 13,
                    color: AppColors.textMuted,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Progress bar
            Stack(
              children: [
                Container(
                  height: 10,
                  decoration: BoxDecoration(
                    color: AppColors.surfaceLight,
                    borderRadius: BorderRadius.circular(6),
                  ),
                ),
                AnimatedFractionallySizedBox(
                  duration: const Duration(milliseconds: 900),
                  curve: Curves.easeOutCubic,
                  widthFactor: p.levelProgress,
                  child: Container(
                    height: 10,
                    decoration: BoxDecoration(
                      gradient: AppColors.primaryGradient,
                      borderRadius: BorderRadius.circular(6),
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.primary.withOpacity(0.5),
                          blurRadius: 6,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              '${((p.levelProgress) * 100).toStringAsFixed(0)}% to Level ${p.level + 1}',
              style: const TextStyle(
                fontFamily: 'Inter',
                fontSize: 12,
                color: AppColors.textMuted,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTabBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.surfaceBorder),
        ),
        child: TabBar(
          controller: _tabController,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textMuted,
          indicatorColor: AppColors.primary,
          indicatorSize: TabBarIndicatorSize.tab,
          dividerColor: Colors.transparent,
          labelStyle: const TextStyle(
            fontFamily: 'Inter',
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
          tabs: const [
            Tab(text: '🏅  Badges'),
            Tab(text: '🏆  Leaderboard'),
          ],
        ),
      ),
    );
  }
}

// ──────────────────────────────────────────────────────────────────────────────
//  Stat Chip Widget
// ──────────────────────────────────────────────────────────────────────────────

class _StatChip extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const _StatChip({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 22),
            const SizedBox(height: 6),
            Text(
              value,
              style: TextStyle(
                fontFamily: 'Inter',
                fontSize: 18,
                fontWeight: FontWeight.w800,
                color: color,
              ),
            ),
            Text(
              label,
              style: const TextStyle(
                fontFamily: 'Inter',
                fontSize: 11,
                color: AppColors.textMuted,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ──────────────────────────────────────────────────────────────────────────────
//  Badges Tab
// ──────────────────────────────────────────────────────────────────────────────

class _BadgesTab extends StatelessWidget {
  final UserProgress progress;

  const _BadgesTab({required this.progress});

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      padding: const EdgeInsets.all(20),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 0.85,
      ),
      itemCount: progress.badges.length,
      itemBuilder: (context, index) {
        final badge = progress.badges[index];
        return _BadgeTile(badge: badge);
      },
    );
  }
}

class _BadgeTile extends StatelessWidget {
  final Badge badge;

  const _BadgeTile({required this.badge});

  static const _badgeEmojis = <String, String>{
    'first_swipe':  '✨',
    'curious':      '🤔',
    'explorer':     '🧭',
    'scholar':      '📚',
    'streak_3':     '🔥',
    'streak_7':     '⚡',
    'streak_30':    '🚀',
    'xp_500':       '💎',
    'xp_2000':      '👑',
  };

  @override
  Widget build(BuildContext context) {
    final emoji = _badgeEmojis[badge.id] ?? '🏅';
    final earned = badge.earned;

    return GestureDetector(
      onTap: () => _showBadgeDetail(context),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        decoration: BoxDecoration(
          color: earned ? AppColors.primary.withOpacity(0.12) : AppColors.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: earned ? AppColors.primary.withOpacity(0.4) : AppColors.surfaceBorder,
            width: earned ? 1.5 : 1,
          ),
          boxShadow: earned
              ? [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.15),
                    blurRadius: 12,
                  )
                ]
              : [],
        ),
        child: Opacity(
          opacity: earned ? 1.0 : 0.35,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(emoji, style: const TextStyle(fontSize: 30)),
              const SizedBox(height: 6),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: Text(
                  badge.name,
                  textAlign: TextAlign.center,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: earned ? AppColors.textPrimary : AppColors.textMuted,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showBadgeDetail(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (_) => Padding(
        padding: const EdgeInsets.all(28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              _badgeEmojis[badge.id] ?? '🏅',
              style: const TextStyle(fontSize: 56),
            ),
            const SizedBox(height: 12),
            Text(
              badge.name,
              style: const TextStyle(
                fontFamily: 'Inter',
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              badge.description,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontFamily: 'Inter',
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
            ),
            if (badge.earned && badge.earnedAt != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: AppColors.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.success.withOpacity(0.3)),
                ),
                child: Text(
                  '✅ Earned on ${badge.earnedAt!.substring(0, 10)}',
                  style: const TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 13,
                    color: AppColors.success,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ] else if (!badge.earned) ...[
              const SizedBox(height: 16),
              const Text(
                '🔒 Keep learning to unlock this badge!',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 13,
                  color: AppColors.textMuted,
                ),
              ),
            ],
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

// ──────────────────────────────────────────────────────────────────────────────
//  Leaderboard Tab
// ──────────────────────────────────────────────────────────────────────────────

class _LeaderboardTab extends StatelessWidget {
  final ProgressProvider provider;

  const _LeaderboardTab({required this.provider});

  @override
  Widget build(BuildContext context) {
    if (provider.isLeaderboardLoading) {
      return const Center(child: CircularProgressIndicator(color: AppColors.primary));
    }

    if (provider.leaderboard.isEmpty) {
      return const Center(
        child: Text('No leaderboard data yet.', style: TextStyle(color: AppColors.textMuted)),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        if (provider.myRank != null && provider.myRank! > 10)
          _MyRankBanner(rank: provider.myRank!, xp: provider.progress?.xp ?? 0),
        ...provider.leaderboard.map((entry) => _LeaderboardRow(entry: entry)),
      ],
    );
  }
}

class _MyRankBanner extends StatelessWidget {
  final int rank;
  final int xp;

  const _MyRankBanner({required this.rank, required this.xp});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.primary.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.person_rounded, color: AppColors.primary, size: 20),
          const SizedBox(width: 10),
          Text(
            'Your rank: #$rank  •  $xp XP',
            style: const TextStyle(
              fontFamily: 'Inter',
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }
}

class _LeaderboardRow extends StatelessWidget {
  final LeaderboardEntry entry;

  const _LeaderboardRow({required this.entry});

  static const _rankEmoji = {1: '🥇', 2: '🥈', 3: '🥉'};

  @override
  Widget build(BuildContext context) {
    final rankLabel = _rankEmoji[entry.rank] ?? '#${entry.rank}';
    final highlight = entry.isMe;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: highlight ? AppColors.primary.withOpacity(0.12) : AppColors.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: highlight ? AppColors.primary.withOpacity(0.4) : AppColors.surfaceBorder,
        ),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 36,
            child: Text(
              rankLabel,
              style: TextStyle(
                fontFamily: 'Inter',
                fontSize: entry.rank <= 3 ? 20 : 14,
                fontWeight: FontWeight.w700,
                color: highlight ? AppColors.primary : AppColors.textSecondary,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              entry.displayName + (highlight ? ' (you)' : ''),
              style: TextStyle(
                fontFamily: 'Inter',
                fontSize: 15,
                fontWeight: highlight ? FontWeight.w700 : FontWeight.w500,
                color: highlight ? AppColors.primary : AppColors.textPrimary,
              ),
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${entry.xp} XP',
                style: TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: highlight ? AppColors.primary : AppColors.accentWarm,
                ),
              ),
              Text(
                'Lv ${entry.level}',
                style: const TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 11,
                  color: AppColors.textMuted,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
