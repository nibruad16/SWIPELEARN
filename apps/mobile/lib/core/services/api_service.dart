import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:swipelearn/models/knowledge_card.dart';
import 'package:swipelearn/models/teacher.dart';
import 'package:swipelearn/models/user.dart';

/// API Service — Communication layer with FastAPI backend.
/// Handles all HTTP requests, JWT management, and JSON parsing.

class ApiService {
  // Change this to your deployed backend URL in production
  static const String _baseUrl = 'http://10.0.2.2:8000'; // Android emulator → localhost
  
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  String? _accessToken;

  // ─────────────────────────────────────────────
  //  Token Management
  // ─────────────────────────────────────────────

  Future<void> _loadToken() async {
    _accessToken ??= await _storage.read(key: 'access_token');
  }

  Future<void> saveTokens(String accessToken, String refreshToken) async {
    _accessToken = accessToken;
    await _storage.write(key: 'access_token', value: accessToken);
    await _storage.write(key: 'refresh_token', value: refreshToken);
  }

  Future<void> clearTokens() async {
    _accessToken = null;
    await _storage.deleteAll();
  }

  Future<bool> hasToken() async {
    final token = await _storage.read(key: 'access_token');
    return token != null && token.isNotEmpty;
  }

  Map<String, String> get _authHeaders => {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $_accessToken',
  };

  Map<String, String> get _jsonHeaders => {
    'Content-Type': 'application/json',
  };

  // ─────────────────────────────────────────────
  //  HTTP Helpers
  // ─────────────────────────────────────────────

  Future<Map<String, dynamic>> _get(String path) async {
    await _loadToken();
    final response = await http.get(
      Uri.parse('$_baseUrl$path'),
      headers: _authHeaders,
    );
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> _post(String path, {Map<String, dynamic>? body}) async {
    await _loadToken();
    final response = await http.post(
      Uri.parse('$_baseUrl$path'),
      headers: _authHeaders,
      body: body != null ? jsonEncode(body) : null,
    );
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> _delete(String path) async {
    await _loadToken();
    final response = await http.delete(
      Uri.parse('$_baseUrl$path'),
      headers: _authHeaders,
    );
    return _handleResponse(response);
  }

  Map<String, dynamic> _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else if (response.statusCode == 401) {
      throw AuthException('Session expired. Please login again.');
    } else {
      final body = jsonDecode(response.body);
      throw ApiException(
        body['detail'] ?? 'Something went wrong',
        response.statusCode,
      );
    }
  }

  // ─────────────────────────────────────────────
  //  Auth Endpoints
  // ─────────────────────────────────────────────

  Future<AppUser> signup(String email, String password, {String? displayName}) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/auth/signup'),
      headers: _jsonHeaders,
      body: jsonEncode({
        'email': email,
        'password': password,
        if (displayName != null) 'display_name': displayName,
      }),
    );
    final data = _handleResponse(response);

    if (data['access_token'] != null) {
      await saveTokens(data['access_token'], data['refresh_token']);
    }

    return AppUser(
      id: data['user_id'],
      email: email,
      displayName: displayName,
    );
  }

  Future<AppUser> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/auth/login'),
      headers: _jsonHeaders,
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );
    final data = _handleResponse(response);

    await saveTokens(data['access_token'], data['refresh_token']);

    final userData = data['user'] as Map<String, dynamic>;
    return AppUser(
      id: userData['id'],
      email: userData['email'],
    );
  }

  Future<AppUser> googleSignIn(String idToken) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/auth/google'),
      headers: _jsonHeaders,
      body: jsonEncode({'id_token': idToken}),
    );
    final data = _handleResponse(response);

    await saveTokens(data['access_token'], data['refresh_token']);

    final userData = data['user'] as Map<String, dynamic>;
    return AppUser(
      id: userData['id'],
      email: userData['email'],
      displayName: userData['display_name'],
    );
  }

  Future<void> logout() async {
    await clearTokens();
  }

  // ─────────────────────────────────────────────
  //  Feed Endpoints
  // ─────────────────────────────────────────────

  Future<List<KnowledgeCard>> getFeed({int page = 1, int pageSize = 20}) async {
    final data = await _get('/feed?page=$page&page_size=$pageSize');
    final cards = (data['cards'] as List)
        .map((c) => KnowledgeCard.fromJson(c as Map<String, dynamic>))
        .toList();
    return cards;
  }

  Future<List<KnowledgeCard>> getSavedCards({int page = 1, int pageSize = 20}) async {
    final data = await _get('/feed/saved?page=$page&page_size=$pageSize');
    final cards = (data['cards'] as List)
        .map((c) => KnowledgeCard.fromJson(c as Map<String, dynamic>))
        .toList();
    return cards;
  }

  Future<void> markCardSeen(String cardId) async {
    await _post('/feed/seen/$cardId');
  }

  // ─────────────────────────────────────────────
  //  Cards Endpoints
  // ─────────────────────────────────────────────

  Future<Map<String, dynamic>> summarizeUrl(String url, {bool saveTeacher = false}) async {
    return _post('/cards/summarize', body: {
      'url': url,
      'save_teacher': saveTeacher,
    });
  }

  Future<KnowledgeCard> getCard(String cardId) async {
    final data = await _get('/cards/$cardId');
    return KnowledgeCard.fromJson(data);
  }

  Future<void> saveCard(String cardId) async {
    await _post('/cards/$cardId/save');
  }

  Future<void> unsaveCard(String cardId) async {
    await _delete('/cards/$cardId/save');
  }

  // ─────────────────────────────────────────────
  //  Teachers Endpoints
  // ─────────────────────────────────────────────

  Future<List<Teacher>> getTeachers() async {
    final data = await _get('/teachers');
    final teachers = (data['teachers'] as List)
        .map((t) => Teacher.fromJson(t as Map<String, dynamic>))
        .toList();
    return teachers;
  }

  Future<Teacher> followTeacher({
    required String name,
    required String websiteUrl,
    String? avatarUrl,
  }) async {
    final data = await _post('/teachers', body: {
      'name': name,
      'website_url': websiteUrl,
      if (avatarUrl != null) 'avatar_url': avatarUrl,
    });
    return Teacher.fromJson(data['teacher'] as Map<String, dynamic>);
  }

  Future<void> unfollowTeacher(String teacherId) async {
    await _delete('/teachers/$teacherId');
  }

  Future<List<KnowledgeCard>> getTeacherCards(String teacherId, {int page = 1}) async {
    final data = await _get('/teachers/$teacherId/cards?page=$page');
    final cards = (data['cards'] as List)
        .map((c) => KnowledgeCard.fromJson(c as Map<String, dynamic>))
        .toList();
    return cards;
  }
}

// ─────────────────────────────────────────────
//  Custom Exceptions
// ─────────────────────────────────────────────

class ApiException implements Exception {
  final String message;
  final int statusCode;
  
  ApiException(this.message, this.statusCode);
  
  @override
  String toString() => message;
}

class AuthException implements Exception {
  final String message;
  
  AuthException(this.message);
  
  @override
  String toString() => message;
}
