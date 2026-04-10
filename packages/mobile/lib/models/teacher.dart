/// Data model for a Teacher (Creator/Blogger).
/// Maps directly to the backend Teacher schema.

class Teacher {
  final String id;
  final String name;
  final String websiteUrl;
  final String? blogRssUrl;
  final String? avatarUrl;
  final DateTime createdAt;
  final int postsCount;
  final DateTime? followedAt;

  Teacher({
    required this.id,
    required this.name,
    required this.websiteUrl,
    this.blogRssUrl,
    this.avatarUrl,
    required this.createdAt,
    this.postsCount = 0,
    this.followedAt,
  });

  factory Teacher.fromJson(Map<String, dynamic> json) {
    return Teacher(
      id: json['id'] as String,
      name: json['name'] as String,
      websiteUrl: json['website_url'] as String,
      blogRssUrl: json['blog_rss_url'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      postsCount: json['posts_count'] as int? ?? 0,
      followedAt: json['followed_at'] != null
          ? DateTime.parse(json['followed_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'website_url': websiteUrl,
    'blog_rss_url': blogRssUrl,
    'avatar_url': avatarUrl,
    'created_at': createdAt.toIso8601String(),
    'posts_count': postsCount,
  };

  /// Get initials for avatar placeholder
  String get initials {
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.substring(0, name.length >= 2 ? 2 : 1).toUpperCase();
  }

  /// Domain extracted from website URL
  String get domain {
    try {
      final uri = Uri.parse(websiteUrl);
      return uri.host.replaceFirst('www.', '');
    } catch (_) {
      return websiteUrl;
    }
  }
}
