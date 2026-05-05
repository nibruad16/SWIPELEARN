import 'package:flutter/material.dart';
import 'package:swipelearn/core/services/api_service.dart';
import 'package:swipelearn/models/progress.dart';

/// ProgressProvider — Manages XP, streak, badges, and leaderboard state.

class ProgressProvider extends ChangeNotifier {
  final ApiService _api;

  UserProgress? _progress;
  List<LeaderboardEntry> _leaderboard = [];
  int? _myRank;
  bool _isLoading = false;
  bool _isLeaderboardLoading = false;
  String? _error;

  ProgressProvider(this._api);

  // ── Getters ──
  UserProgress? get progress => _progress;
  List<LeaderboardEntry> get leaderboard => _leaderboard;
  int? get myRank => _myRank;
  bool get isLoading => _isLoading;
  bool get isLeaderboardLoading => _isLeaderboardLoading;
  String? get error => _error;

  /// Load the current user's full progress snapshot.
  Future<void> loadProgress() async {
    if (_isLoading) return;
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final data = await _api.getProgress();
      _progress = UserProgress.fromJson(data);
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Record a card swipe and update progress optimistically.
  Future<List<Badge>> recordSwipe({String? cardId}) async {
    try {
      final result = await _api.recordSwipe(cardId: cardId);
      final newBadges = (result['new_badges'] as List<dynamic>)
          .map((b) => Badge.fromJson(b as Map<String, dynamic>))
          .toList();

      // Refresh full progress snapshot to keep state consistent
      await loadProgress();
      return newBadges;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return [];
    }
  }

  /// Record a card save and add the XP bonus.
  Future<void> recordSave() async {
    try {
      await _api.recordSave();
      // Refresh progress to reflect new XP
      await loadProgress();
    } catch (_) {
      // Non-critical — silent fail
    }
  }

  /// Load the leaderboard.
  Future<void> loadLeaderboard({int limit = 10}) async {
    if (_isLeaderboardLoading) return;
    _isLeaderboardLoading = true;
    notifyListeners();

    try {
      final data = await _api.getLeaderboard(limit: limit);
      _leaderboard = (data['leaderboard'] as List<dynamic>)
          .map((e) => LeaderboardEntry.fromJson(e as Map<String, dynamic>))
          .toList();
      _myRank = data['my_rank'] as int?;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLeaderboardLoading = false;
      notifyListeners();
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
