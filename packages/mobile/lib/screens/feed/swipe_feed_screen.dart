import 'package:flutter/material.dart';
import 'package:swipelearn/core/theme/app_theme.dart';
import 'package:swipelearn/models/knowledge_card.dart';
import 'package:swipelearn/widgets/knowledge_card_widget.dart';
import 'package:swipelearn/widgets/shared_widgets.dart';

/// SwipeFeedScreen — TikTok-style vertical swipe feed.
/// Pattern: Iterator — vertical PageView for card-by-card navigation.

class SwipeFeedScreen extends StatefulWidget {
  const SwipeFeedScreen({super.key});

  @override
  State<SwipeFeedScreen> createState() => _SwipeFeedScreenState();
}

class _SwipeFeedScreenState extends State<SwipeFeedScreen> {
  late PageController _pageController;
  int _currentPage = 0;

  // Mock data for development
  final List<KnowledgeCard> _mockCards = [
    KnowledgeCard(
      id: '1',
      sourceUrl: 'https://overreacted.io/a-complete-guide-to-useeffect/',
      title: 'A Complete Guide to useEffect',
      author: 'Dan Abramov',
      tlDr: 'useEffect lets you synchronize things outside React with your component state — think of effects as synchronizers, not lifecycle hooks.',
      keyPoints: [
        'Each render has its own props, state, and effects — they are "frozen" in time',
        'The dependency array tells React when to re-run the effect, not what it uses',
        'Functions inside effects should be defined inside the effect or wrapped in useCallback',
        'The cleanup function runs before the next effect and on unmount',
      ],
      stealInsight: 'Instead of thinking "run this on mount", think "synchronize this data to the DOM" — this mental model eliminates entire categories of bugs.',
      createdAt: DateTime.now().subtract(const Duration(hours: 2)),
    ),
    KnowledgeCard(
      id: '2',
      sourceUrl: 'https://blog.pragmaticengineer.com/the-pragmatic-engineers-guide/',
      title: 'What Makes a Senior Engineer Senior?',
      author: 'Gergely Orosz',
      tlDr: 'Senior engineers own problems end-to-end and multiply the effectiveness of their entire team, not just ship code faster.',
      keyPoints: [
        'Impact over output: Senior engineers are measured by outcomes, not lines of code',
        'They proactively identify and solve the right problems before being asked',
        'Technical decision-making includes weighing business tradeoffs, not just engineering elegance',
        'Mentorship and knowledge sharing are core responsibilities, not side activities',
        'They reduce complexity for the whole team through better abstractions',
      ],
      stealInsight: 'Write a 1-page "technical decision record" for every major architecture choice — it forces clear thinking and becomes invaluable documentation.',
      createdAt: DateTime.now().subtract(const Duration(hours: 5)),
    ),
    KnowledgeCard(
      id: '3',
      sourceUrl: 'https://www.swyx.io/learn-in-public',
      title: 'Learn in Public',
      author: 'swyx',
      tlDr: 'The fastest way to learn is to share what you learn publicly — write blogs, make videos, give talks, even if nobody reads them.',
      keyPoints: [
        'Your "exhaust" (blogs, tweets, notes) becomes searchable & helps others',
        'Teaching forces you to understand deeply — you can\'t explain what you don\'t know',
        'Public learning creates serendipity: people find you and open unexpected doors',
      ],
      stealInsight: 'Create a personal "Today I Learned" repo on GitHub — commit one thing you learned every day. In 6 months, you\'ll have a knowledge base AND a visible track record.',
      createdAt: DateTime.now().subtract(const Duration(days: 1)),
    ),
  ];

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_mockCards.isEmpty) {
      return const EmptyState(
        icon: Icons.style_outlined,
        title: 'No cards yet',
        subtitle: 'Paste a blog URL to create your first Knowledge Card!',
        actionLabel: 'Add URL',
      );
    }

    return Column(
      children: [
        // Header
        _buildHeader(),
        // Cards
        Expanded(
          child: PageView.builder(
            controller: _pageController,
            scrollDirection: Axis.vertical,
            itemCount: _mockCards.length,
            onPageChanged: (index) {
              setState(() => _currentPage = index);
            },
            itemBuilder: (context, index) {
              final card = _mockCards[index];
              return KnowledgeCardWidget(
                card: card,
                cardIndex: index,
                onSave: () {
                  setState(() {
                    _mockCards[index] = card.copyWith(isSaved: !card.isSaved);
                  });
                },
                onShare: () {
                  // Share functionality
                },
                onSourceTap: () {
                  // Open URL in browser
                },
              );
            },
          ),
        ),
        // Progress indicator
        _buildProgress(),
      ],
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'SwipeLearn',
                style: TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textPrimary,
                  letterSpacing: -0.5,
                ),
              ),
              Text(
                '${_mockCards.length} cards to learn',
                style: const TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 13,
                  color: AppColors.textMuted,
                ),
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AppColors.surfaceLight,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.surfaceBorder),
            ),
            child: const Icon(
              Icons.tune_rounded,
              color: AppColors.textSecondary,
              size: 20,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProgress() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: Row(
        children: [
          // Page indicator dots
          ...List.generate(_mockCards.length, (index) {
            return AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              width: index == _currentPage ? 24 : 8,
              height: 4,
              margin: const EdgeInsets.only(right: 4),
              decoration: BoxDecoration(
                color: index == _currentPage
                    ? AppColors.primary
                    : AppColors.surfaceBorder,
                borderRadius: BorderRadius.circular(2),
              ),
            );
          }),
          const Spacer(),
          Text(
            '${_currentPage + 1}/${_mockCards.length}',
            style: const TextStyle(
              fontFamily: 'Inter',
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: AppColors.textMuted,
            ),
          ),
        ],
      ),
    );
  }
}
