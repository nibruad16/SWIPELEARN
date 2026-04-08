import 'package:flutter/material.dart';
import 'package:swipelearn/core/services/api_service.dart';
import 'package:swipelearn/models/user.dart';

/// AuthProvider — Manages authentication state across the app.
/// Handles login, signup, Google auth, and session persistence.

class AuthProvider extends ChangeNotifier {
  final ApiService _api;

  AppUser? _user;
  bool _isLoading = false;
  bool _isInitialized = false;
  String? _error;

  AuthProvider(this._api);

  // Getters
  AppUser? get user => _user;
  bool get isLoggedIn => _user != null;
  bool get isLoading => _isLoading;
  bool get isInitialized => _isInitialized;
  String? get error => _error;

  /// Check if user has a stored session on app startup.
  Future<void> initialize() async {
    final hasToken = await _api.hasToken();
    if (hasToken) {
      // Token exists — user is "logged in"
      // In production, you'd verify the token here
      _user = AppUser(id: '', email: 'cached');
    }
    _isInitialized = true;
    notifyListeners();
  }

  Future<void> signup(String email, String password, {String? displayName}) async {
    _setLoading(true);
    _error = null;
    try {
      _user = await _api.signup(email, password, displayName: displayName);
      notifyListeners();
    } on ApiException catch (e) {
      _error = e.message;
      notifyListeners();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> login(String email, String password) async {
    _setLoading(true);
    _error = null;
    try {
      _user = await _api.login(email, password);
      notifyListeners();
    } on ApiException catch (e) {
      _error = e.message;
      notifyListeners();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> googleSignIn(String idToken) async {
    _setLoading(true);
    _error = null;
    try {
      _user = await _api.googleSignIn(idToken);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> logout() async {
    await _api.logout();
    _user = null;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
}
