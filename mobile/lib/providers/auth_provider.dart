import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../services/api_service.dart';

class AuthProvider extends ChangeNotifier {
  static const _tokenKey = 'auth_token';
  static const _userKey = 'auth_user';
  static const _defaultBaseUrl = 'http://10.0.2.2:8000';

  final _storage = const FlutterSecureStorage();

  bool _isAuthenticated = false;
  Map<String, dynamic>? _user;
  String? _token;
  ApiService? _apiService;

  bool get isAuthenticated => _isAuthenticated;
  Map<String, dynamic>? get user => _user;
  String? get token => _token;

  ApiService get apiService {
    _apiService ??= ApiService(baseUrl: _defaultBaseUrl);
    return _apiService!;
  }

  /// Called once at app start to restore persisted session.
  Future<void> init() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedUrl = prefs.getString('api_url') ?? _defaultBaseUrl;
      _apiService = ApiService(baseUrl: savedUrl);

      final storedToken = await _storage.read(key: _tokenKey);
      final storedUserJson = await _storage.read(key: _userKey);

      if (storedToken != null && storedToken.isNotEmpty) {
        _token = storedToken;
        _apiService!.setToken(storedToken);

        if (storedUserJson != null) {
          _user = jsonDecode(storedUserJson) as Map<String, dynamic>;
        }

        // Validate the token is still accepted by calling the health check.
        // If the server is unreachable we keep the session alive optimistically.
        try {
          await _apiService!.checkHealth();
          _isAuthenticated = true;
        } on ApiException catch (e) {
          if (e.statusCode == 401) {
            await _clearStoredSession();
          } else {
            // Server error or network error — keep session; user can retry.
            _isAuthenticated = true;
          }
        } catch (_) {
          _isAuthenticated = true;
        }
      }
    } catch (_) {
      // Silently fail; app starts unauthenticated.
    }
    notifyListeners();
  }

  /// Authenticate with username / password.
  ///
  /// Throws [ApiException] on network/server errors.
  /// Returns `false` if credentials were wrong but request succeeded.
  Future<bool> login(String username, String password, {String? baseUrl}) async {
    final url = baseUrl ?? _defaultBaseUrl;
    _apiService = ApiService(baseUrl: url);

    // Save the URL so it persists across restarts.
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('api_url', url);

    final success = await _apiService!.login(username, password);
    if (success) {
      _token = _apiService!.token;
      _user = {'username': username, 'role': 'user'};
      _isAuthenticated = true;

      if (_token != null) {
        await _storage.write(key: _tokenKey, value: _token);
        await _storage.write(
            key: _userKey, value: jsonEncode(_user));
      }
      notifyListeners();
    }
    return success;
  }

  /// Clear session state and secure storage.
  Future<void> logout() async {
    _apiService?.clearToken();
    await _clearStoredSession();
    _isAuthenticated = false;
    _user = null;
    _token = null;
    notifyListeners();
  }

  Future<void> _clearStoredSession() async {
    await _storage.delete(key: _tokenKey);
    await _storage.delete(key: _userKey);
  }
}
