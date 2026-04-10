import 'package:flutter/material.dart';
import 'package:swipelearn/core/services/api_service.dart';
import 'package:swipelearn/models/knowledge_card.dart';

/// FeedProvider — Manages the Knowledge Card feed state.
/// Handles pagination, save/unsave, and mark as seen.

class FeedProvider extends ChangeNotifier {
  final ApiService _api;

  List<KnowledgeCard> _cards = [];
  List<KnowledgeCard> _savedCards = [];
  bool _isLoading = false;
  bool _isSavedLoading = false;
  bool _hasMore = true;
  bool _hasSavedMore = true;
  int _currentPage = 1;
  int _savedPage = 1;
  String? _error;

  FeedProvider(this._api);

  // Getters
  List<KnowledgeCard> get cards => _cards;
  List<KnowledgeCard> get savedCards => _savedCards;
  bool get isLoading => _isLoading;
  bool get isSavedLoading => _isSavedLoading;
  bool get hasMore => _hasMore;
  String? get error => _error;

  /// Load feed cards (initial load or refresh).
  Future<void> loadFeed({bool refresh = false}) async {
    if (_isLoading) return;

    if (refresh) {
      _currentPage = 1;
      _hasMore = true;
    }

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final newCards = await _api.getFeed(page: _currentPage);
      
      if (refresh) {
        _cards = newCards;
      } else {
        _cards.addAll(newCards);
      }

      _hasMore = newCards.length >= 20;
      _currentPage++;
    } on AuthException {
      _error = 'Session expired';
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Load next page of cards.
  Future<void> loadMore() async {
    if (!_hasMore || _isLoading) return;
    await loadFeed();
  }

  /// Load saved cards.
  Future<void> loadSavedCards({bool refresh = false}) async {
    if (_isSavedLoading) return;

    if (refresh) {
      _savedPage = 1;
      _hasSavedMore = true;
    }

    _isSavedLoading = true;
    notifyListeners();

    try {
      final newCards = await _api.getSavedCards(page: _savedPage);
      
      if (refresh) {
        _savedCards = newCards;
      } else {
        _savedCards.addAll(newCards);
      }

      _hasSavedMore = newCards.length >= 20;
      _savedPage++;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isSavedLoading = false;
      notifyListeners();
    }
  }

  /// Toggle save/unsave a card.
  Future<void> toggleSave(KnowledgeCard card) async {
    try {
      if (card.isSaved) {
        await _api.unsaveCard(card.id);
      } else {
        await _api.saveCard(card.id);
      }

      // Update the card in the feed list
      final index = _cards.indexWhere((c) => c.id == card.id);
      if (index != -1) {
        _cards[index] = _cards[index].copyWith(isSaved: !card.isSaved);
      }

      // Update in saved list
      if (card.isSaved) {
        _savedCards.removeWhere((c) => c.id == card.id);
      } else {
        _savedCards.insert(0, card.copyWith(isSaved: true));
      }

      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  /// Mark a card as seen.
  Future<void> markSeen(String cardId) async {
    try {
      await _api.markCardSeen(cardId);
    } catch (_) {
      // Silent fail — non-critical
    }
  }

  /// Summarize a new URL and add to feed.
  Future<KnowledgeCard?> summarizeUrl(String url, {bool saveTeacher = false}) async {
    try {
      final data = await _api.summarizeUrl(url, saveTeacher: saveTeacher);
      final cardData = data['card'] as Map<String, dynamic>;
      final card = KnowledgeCard.fromJson(cardData);
      
      // Add to top of feed
      _cards.insert(0, card);
      notifyListeners();
      
      return card;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
