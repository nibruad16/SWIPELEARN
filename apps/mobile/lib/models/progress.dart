/// Progress model — mirrors the backend progress snapshot.

class UserProgress {
  final String userId;
  final int xp;
  final int level;
  final int streakDays;
  final int longestStreak;
  final int cardsRead;
  final List<Badge> badges;
  final String? lastActiveDate;

  const UserProgress({
    required this.userId,
    required this.xp,
    required this.level,
    required this.streakDays,
    required this.longestStreak,
    required this.cardsRead,
    required this.badges,
    this.lastActiveDate,
  });

  factory UserProgress.fromJson(Map<String, dynamic> json) {
    return UserProgress(
      userId: json['user_id'] as String,
      xp: (json['xp'] as num).toInt(),
      level: (json['level'] as num).toInt(),
      streakDays: (json['streak_days'] as num).toInt(),
      longestStreak: (json['longest_streak'] as num).toInt(),
      cardsRead: (json['cards_read'] as num).toInt(),
      badges: (json['badges'] as List<dynamic>)
          .map((b) => Badge.fromJson(b as Map<String, dynamic>))
          .toList(),
      lastActiveDate: json['last_active_date'] as String?,
    );
  }

  /// XP needed to reach the NEXT level.
  int get xpForNextLevel => ((level) * (level)) * 100;

  /// XP accumulated since the START of current level.
  int get xpForCurrentLevel => ((level - 1) * (level - 1)) * 100;

  /// Progress within the current level as 0.0 → 1.0.
  double get levelProgress {
    final needed = xpForNextLevel - xpForCurrentLevel;
    if (needed <= 0) return 1.0;
    return ((xp - xpForCurrentLevel) / needed).clamp(0.0, 1.0);
  }

  List<Badge> get earnedBadges => badges.where((b) => b.earned).toList();
  List<Badge> get unearnedBadges => badges.where((b) => !b.earned).toList();
}

class Badge {
  final String id;
  final String name;
  final String description;
  final bool earned;
  final String? earnedAt;

  const Badge({
    required this.id,
    required this.name,
    required this.description,
    required this.earned,
    this.earnedAt,
  });

  factory Badge.fromJson(Map<String, dynamic> json) {
    return Badge(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      earned: json['earned'] as bool? ?? false,
      earnedAt: json['earned_at'] as String?,
    );
  }
}

class LeaderboardEntry {
  final int rank;
  final String displayName;
  final int xp;
  final int level;
  final bool isMe;

  const LeaderboardEntry({
    required this.rank,
    required this.displayName,
    required this.xp,
    required this.level,
    required this.isMe,
  });

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json) {
    return LeaderboardEntry(
      rank: (json['rank'] as num).toInt(),
      displayName: json['display_name'] as String,
      xp: (json['xp'] as num).toInt(),
      level: (json['level'] as num).toInt(),
      isMe: json['is_me'] as bool? ?? false,
    );
  }
}
