import 'package:flutter/material.dart';
import 'package:swipelearn/core/services/api_service.dart';
import 'package:swipelearn/models/teacher.dart';
import 'package:swipelearn/models/knowledge_card.dart';

/// TeacherProvider — Manages teacher (creator) state.
/// Handles follow/unfollow and teacher card retrieval.

class TeacherProvider extends ChangeNotifier {
  final ApiService _api;

  List<Teacher> _teachers = [];
  bool _isLoading = false;
  String? _error;

  TeacherProvider(this._api);

  // Getters
  List<Teacher> get teachers => _teachers;
  bool get isLoading => _isLoading;
  String? get error => _error;

  /// Load all followed teachers.
  Future<void> loadTeachers() async {
    if (_isLoading) return;

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _teachers = await _api.getTeachers();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Follow a new teacher.
  Future<Teacher?> followTeacher({
    required String name,
    required String websiteUrl,
    String? avatarUrl,
  }) async {
    try {
      final teacher = await _api.followTeacher(
        name: name,
        websiteUrl: websiteUrl,
        avatarUrl: avatarUrl,
      );
      _teachers.insert(0, teacher);
      notifyListeners();
      return teacher;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    }
  }

  /// Unfollow a teacher.
  Future<void> unfollowTeacher(String teacherId) async {
    try {
      await _api.unfollowTeacher(teacherId);
      _teachers.removeWhere((t) => t.id == teacherId);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  /// Get cards from a specific teacher.
  Future<List<KnowledgeCard>> getTeacherCards(String teacherId) async {
    return _api.getTeacherCards(teacherId);
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
