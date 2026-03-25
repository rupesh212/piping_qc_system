import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, {this.statusCode});

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class ApiService {
  final String baseUrl;
  String? _token;

  ApiService({required this.baseUrl});

  /// Expose the current token so AuthProvider can persist it.
  String? get token => _token;

  void setToken(String token) {
    _token = token;
  }

  void clearToken() {
    _token = null;
  }

  Map<String, String> get _headers {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (_token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    return headers;
  }

  Future<http.Response> _get(String path) async {
    final uri = Uri.parse('$baseUrl$path');
    try {
      final response = await http
          .get(uri, headers: _headers)
          .timeout(const Duration(seconds: 30));
      _checkResponse(response);
      return response;
    } on SocketException {
      throw ApiException('Network error: unable to reach server');
    } on http.ClientException catch (e) {
      throw ApiException('HTTP client error: ${e.message}');
    }
  }

  Future<http.Response> _post(String path, Map<String, dynamic> body) async {
    final uri = Uri.parse('$baseUrl$path');
    try {
      final response = await http
          .post(uri, headers: _headers, body: jsonEncode(body))
          .timeout(const Duration(seconds: 30));
      _checkResponse(response);
      return response;
    } on SocketException {
      throw ApiException('Network error: unable to reach server');
    } on http.ClientException catch (e) {
      throw ApiException('HTTP client error: ${e.message}');
    }
  }

  void _checkResponse(http.Response response) {
    if (response.statusCode >= 400) {
      String message = 'Request failed';
      try {
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        message = body['detail']?.toString() ??
            body['message']?.toString() ??
            message;
      } catch (_) {
        message = response.body.isNotEmpty ? response.body : message;
      }
      throw ApiException(message, statusCode: response.statusCode);
    }
  }

  /// Authenticate and return true on success. Stores the received token.
  Future<bool> login(String username, String password) async {
    final uri = Uri.parse('$baseUrl/api/v1/auth/login');
    try {
      // OAuth2 password flow expects form-encoded body
      final response = await http
          .post(
            uri,
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
              'Accept': 'application/json',
            },
            body: {
              'username': username,
              'password': password,
              'grant_type': 'password',
            },
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final token = data['access_token']?.toString();
        if (token != null) {
          setToken(token);
          return true;
        }
      }
      return false;
    } on SocketException {
      throw ApiException('Network error: unable to reach server');
    } on http.ClientException catch (e) {
      throw ApiException('HTTP client error: ${e.message}');
    }
  }

  /// Fetch dashboard summary statistics.
  Future<Map<String, dynamic>> getDashboardSummary() async {
    final response = await _get('/api/v1/dashboard/summary');
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  /// Fetch paginated list of ISO drawings.
  Future<Map<String, dynamic>> getISOList({
    int skip = 0,
    int limit = 20,
    String? search,
  }) async {
    final queryParams = {
      'skip': skip.toString(),
      'limit': limit.toString(),
      if (search != null && search.isNotEmpty) 'search': search,
    };
    final uri = Uri.parse('$baseUrl/api/v1/iso')
        .replace(queryParameters: queryParams);
    try {
      final response = await http
          .get(uri, headers: _headers)
          .timeout(const Duration(seconds: 30));
      _checkResponse(response);
      return jsonDecode(response.body) as Map<String, dynamic>;
    } on SocketException {
      throw ApiException('Network error: unable to reach server');
    } on http.ClientException catch (e) {
      throw ApiException('HTTP client error: ${e.message}');
    }
  }

  /// Trigger validation for a specific ISO drawing.
  Future<Map<String, dynamic>> validateISO(String isoId) async {
    final response = await _post('/api/v1/iso/$isoId/validate', {});
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  /// Fetch anomaly detection report.
  Future<Map<String, dynamic>> getAnomalyReport() async {
    final response = await _get('/api/v1/dashboard/anomaly-report');
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  /// Fetch recent validation errors list.
  Future<List<dynamic>> getRecentErrors() async {
    final response = await _get('/api/v1/dashboard/errors');
    return jsonDecode(response.body) as List<dynamic>;
  }

  /// Check server health. Returns the parsed JSON body on success.
  Future<Map<String, dynamic>> checkHealth() async {
    final uri = Uri.parse('$baseUrl/health');
    try {
      final response = await http
          .get(uri, headers: {'Accept': 'application/json'})
          .timeout(const Duration(seconds: 10));
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
      throw ApiException('Health check failed', statusCode: response.statusCode);
    } on SocketException {
      throw ApiException('Network error: unable to reach server');
    } on http.ClientException catch (e) {
      throw ApiException('HTTP client error: ${e.message}');
    }
  }

  /// Upload an ISO image file and return the parsed response.
  Future<Map<String, dynamic>> uploadISO(File file) async {
    final uri = Uri.parse('$baseUrl/api/v1/iso/upload');
    final request = http.MultipartRequest('POST', uri);
    if (_token != null) {
      request.headers['Authorization'] = 'Bearer $_token';
    }
    request.files.add(await http.MultipartFile.fromPath('file', file.path));
    try {
      final streamedResponse =
          await request.send().timeout(const Duration(seconds: 120));
      final response = await http.Response.fromStream(streamedResponse);
      _checkResponse(response);
      return jsonDecode(response.body) as Map<String, dynamic>;
    } on SocketException {
      throw ApiException('Network error: unable to reach server');
    } on http.ClientException catch (e) {
      throw ApiException('HTTP client error: ${e.message}');
    }
  }
}
