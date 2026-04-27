import 'package:flutter/material.dart';
import 'package:swipelearn/core/theme/app_theme.dart';
import 'package:swipelearn/models/knowledge_card.dart';
import 'package:swipelearn/widgets/shared_widgets.dart';

/// SavedScreen — Displays user's saved/bookmarked Knowledge Cards.

class SavedScreen extends StatefulWidget {
  const SavedScreen({super.key});

  @override
  State<SavedScreen> createState() => _SavedScreenState();
}

class _SavedScreenState extends State<SavedScreen> {
  // Mock saved cards
  final List<KnowledgeCard> _savedCards = [
    KnowledgeCard(
      id: '1',
      sourceUrl: 'https://overreacted.io/a-complete-guide-to-useeffect/',
      title: 'A Complete Guide to useEffect',
      author: 'Dan Abramov',
      tlDr: 'useEffect lets you synchronize things outside React with your component state.',
      keyPoints: ['Effects are synchronizers, not lifecycle hooks'],
      stealInsight: 'Think "synchronize this data" instead of "run on mount".',
      createdAt: DateTime.now().subtract(const Duration(hours: 2)),
      isSaved: true,
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
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Saved',
                style: TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textPrimary,
                  letterSpacing: -0.5,
                ),
              ),
              Text(
                '${_savedCards.length} cards saved',
                style: const TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 13,
                  color: AppColors.textMuted,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Card list
        Expanded(
          child: _savedCards.isEmpty
              ? const EmptyState(
                  icon: Icons.bookmark_outline,
                  title: 'No saved cards',
                  subtitle: 'Tap the bookmark icon on any Knowledge Card to save it for later.',
                )
              : ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: _savedCards.length,
                  itemBuilder: (context, index) {
                    final card = _savedCards[index];
                    return _SavedCardTile(
                      card: card,
                      onRemove: () {
                        setState(() => _savedCards.removeAt(index));
                      },
                    );
                  },
                ),
        ),
      ],
    );
  }
}

class _SavedCardTile extends StatelessWidget {
  final KnowledgeCard card;
  final VoidCallback? onRemove;

  const _SavedCardTile({
    required this.card,
    this.onRemove,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.surfaceBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Domain
                    Text(
                      _extractDomain(card.sourceUrl).toUpperCase(),
                      style: TextStyle(
                        fontFamily: 'Inter',
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                        color: AppColors.primaryLight,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 6),
                    // Title
                    Text(
                      card.title,
                      style: const TextStyle(
                        fontFamily: 'Inter',
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                        height: 1.3,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: const Icon(Icons.bookmark, color: AppColors.primary, size: 22),
                onPressed: onRemove,
              ),
            ],
          ),
          const SizedBox(height: 8),
          // TL;DR
          Text(
            card.tlDr,
            style: const TextStyle(
              fontFamily: 'Inter',
              fontSize: 13,
              color: AppColors.textSecondary,
              height: 1.4,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 10),
          // Author & Date
          Row(
            children: [
              if (card.author != null) ...[
                const Icon(Icons.person_outline, size: 14, color: AppColors.textMuted),
                const SizedBox(width: 4),
                Text(
                  card.author!,
                  style: const TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 12,
                    color: AppColors.textMuted,
                  ),
                ),
                const SizedBox(width: 12),
              ],
              const Icon(Icons.access_time, size: 14, color: AppColors.textMuted),
              const SizedBox(width: 4),
              Text(
                _timeAgo(card.createdAt),
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
    );
  }

  String _extractDomain(String url) {
    try {
      final uri = Uri.parse(url);
      return uri.host.replaceFirst('www.', '');
    } catch (_) {
      return 'blog';
    }
  }

  String _timeAgo(DateTime dateTime) {
    final diff = DateTime.now().difference(dateTime);
    if (diff.inDays > 0) return '${diff.inDays}d ago';
    if (diff.inHours > 0) return '${diff.inHours}h ago';
    if (diff.inMinutes > 0) return '${diff.inMinutes}m ago';
    return 'just now';
  }
}
