import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:swipelearn/core/theme/app_theme.dart';
import 'package:swipelearn/models/teacher.dart';
import 'package:swipelearn/widgets/teacher_card_widget.dart';
import 'package:swipelearn/widgets/shared_widgets.dart';

/// TeachersScreen — Manage followed creators.
/// Displays followed teachers with post counts and unfollow option.

class TeachersScreen extends StatefulWidget {
  const TeachersScreen({super.key});

  @override
  State<TeachersScreen> createState() => _TeachersScreenState();
}

class _TeachersScreenState extends State<TeachersScreen> {
  // Mock teachers for development
  final List<Teacher> _mockTeachers = [
    Teacher(
      id: '1',
      name: 'Dan Abramov',
      websiteUrl: 'https://overreacted.io',
      blogRssUrl: 'https://overreacted.io/rss.xml',
      createdAt: DateTime.now().subtract(const Duration(days: 30)),
      postsCount: 12,
    ),
    Teacher(
      id: '2',
      name: 'Gergely Orosz',
      websiteUrl: 'https://blog.pragmaticengineer.com',
      createdAt: DateTime.now().subtract(const Duration(days: 14)),
      postsCount: 8,
    ),
    Teacher(
      id: '3',
      name: 'swyx',
      websiteUrl: 'https://www.swyx.io',
      blogRssUrl: 'https://www.swyx.io/rss.xml',
      createdAt: DateTime.now().subtract(const Duration(days: 7)),
      postsCount: 5,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 4),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Teachers',
                    style: TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 28,
                      fontWeight: FontWeight.w800,
                      color: AppColors.textPrimary,
                      letterSpacing: -0.5,
                    ),
                  ),
                  Text(
                    '${_mockTeachers.length} creators followed',
                    style: const TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 13,
                      color: AppColors.textMuted,
                    ),
                  ),
                ],
              ),
              // Add teacher
              GestureDetector(
                onTap: () => _showAddTeacherDialog(context),
                child: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    gradient: AppColors.primaryGradient,
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.primary.withOpacity(0.3),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.person_add,
                    color: Colors.white,
                    size: 20,
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Teacher list
        Expanded(
          child: _mockTeachers.isEmpty
              ? const EmptyState(
                  icon: Icons.school_outlined,
                  title: 'No teachers yet',
                  subtitle: 'Follow your favorite creators to get their blog posts as Knowledge Cards automatically.',
                  actionLabel: 'Add Teacher',
                )
              : ListView.builder(
                  padding: const EdgeInsets.only(bottom: 20),
                  itemCount: _mockTeachers.length,
                  itemBuilder: (context, index) {
                    final teacher = _mockTeachers[index];
                    return TeacherCardWidget(
                      teacher: teacher,
                      onTap: () {
                        // Navigate to teacher detail
                      },
                      onUnfollow: () {
                        HapticFeedback.mediumImpact();
                        _showUnfollowConfirmation(context, teacher, index);
                      },
                    );
                  },
                ),
        ),
      ],
    );
  }

  void _showUnfollowConfirmation(BuildContext context, Teacher teacher, int index) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Text(
          'Unfollow ${teacher.name}?',
          style: const TextStyle(
            fontFamily: 'Inter',
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
          ),
        ),
        content: const Text(
          'Their existing cards will remain, but you won\'t get new ones automatically.',
          style: TextStyle(
            fontFamily: 'Inter',
            color: AppColors.textSecondary,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text(
              'Cancel',
              style: TextStyle(color: AppColors.textMuted),
            ),
          ),
          TextButton(
            onPressed: () {
              setState(() => _mockTeachers.removeAt(index));
              Navigator.pop(ctx);
            },
            child: const Text(
              'Unfollow',
              style: TextStyle(color: AppColors.error, fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }

  void _showAddTeacherDialog(BuildContext context) {
    final nameCtrl = TextEditingController();
    final urlCtrl = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => Padding(
        padding: EdgeInsets.fromLTRB(
          24, 24, 24, MediaQuery.of(ctx).viewInsets.bottom + 24,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Handle bar
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.surfaceBorder,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Follow a Creator',
              style: TextStyle(
                fontFamily: 'Inter',
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 4),
            const Text(
              'We\'ll discover their RSS feed automatically',
              style: TextStyle(
                fontFamily: 'Inter',
                fontSize: 13,
                color: AppColors.textMuted,
              ),
            ),
            const SizedBox(height: 24),
            TextFormField(
              controller: nameCtrl,
              decoration: const InputDecoration(
                hintText: 'Creator name',
                prefixIcon: Icon(Icons.person_outline, color: AppColors.textMuted),
              ),
              style: const TextStyle(fontFamily: 'Inter', color: AppColors.textPrimary),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: urlCtrl,
              keyboardType: TextInputType.url,
              decoration: const InputDecoration(
                hintText: 'Website URL (e.g. overreacted.io)',
                prefixIcon: Icon(Icons.language, color: AppColors.textMuted),
              ),
              style: const TextStyle(fontFamily: 'Inter', color: AppColors.textPrimary),
            ),
            const SizedBox(height: 24),
            GradientButton(
              label: 'Follow',
              icon: Icons.person_add,
              onPressed: () {
                // In production, call TeacherProvider.followTeacher
                Navigator.pop(ctx);
              },
            ),
          ],
        ),
      ),
    );
  }
}
