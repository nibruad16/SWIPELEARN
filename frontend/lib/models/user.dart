/// User model for authenticated user data.

class AppUser {
  final String id;
  final String email;
  final String? displayName;
  final String? avatarUrl;

  AppUser({
    required this.id,
    required this.email,
    this.displayName,
    this.avatarUrl,
  });

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id'] as String,
      email: json['email'] as String,
      displayName: json['display_name'] as String?,
      avatarUrl: json['avatar_url'] as String?,
    );
  }

  String get nameOrEmail => displayName ?? email.split('@').first;

  String get initials {
    final name = nameOrEmail;
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.substring(0, name.length >= 2 ? 2 : 1).toUpperCase();
  }
}

/// Auth tokens for session management.
class AuthTokens {
  final String accessToken;
  final String refreshToken;

  AuthTokens({
    required this.accessToken,
    required this.refreshToken,
  });
}
