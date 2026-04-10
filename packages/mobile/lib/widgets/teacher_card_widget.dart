import 'package:flutter/material.dart';
import 'package:swipelearn/core/theme/app_theme.dart';
import 'package:swipelearn/models/teacher.dart';

/// TeacherCardWidget — Displays a teacher/creator in a styled card.
/// Shows name, domain, post count, and actions.

class TeacherCardWidget extends StatelessWidget {
  final Teacher teacher;
  final VoidCallback? onTap;
  final VoidCallback? onUnfollow;

  const TeacherCardWidget({
    super.key,
    required this.teacher,
    this.onTap,
    this.onUnfollow,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.surfaceBorder, width: 1),
        ),
        child: Row(
          children: [
            // Avatar
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                gradient: AppColors.accentGradient,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Center(
                child: Text(
                  teacher.initials,
                  style: const TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 14),
            // Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    teacher.name,
                    style: const TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      const Icon(Icons.language, size: 13, color: AppColors.textMuted),
                      const SizedBox(width: 4),
                      Text(
                        teacher.domain,
                        style: const TextStyle(
                          fontFamily: 'Inter',
                          fontSize: 12,
                          color: AppColors.textMuted,
                        ),
                      ),
                      const SizedBox(width: 12),
                      const Icon(Icons.auto_stories, size: 13, color: AppColors.textMuted),
                      const SizedBox(width: 4),
                      Text(
                        '${teacher.postsCount} cards',
                        style: const TextStyle(
                          fontFamily: 'Inter',
                          fontSize: 12,
                          color: AppColors.textMuted,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            // Unfollow
            if (onUnfollow != null)
              IconButton(
                icon: const Icon(Icons.person_remove_outlined, size: 20),
                color: AppColors.textMuted,
                onPressed: onUnfollow,
                tooltip: 'Unfollow',
              ),
            const Icon(
              Icons.chevron_right,
              color: AppColors.textMuted,
              size: 20,
            ),
          ],
        ),
      ),
    );
  }
}
