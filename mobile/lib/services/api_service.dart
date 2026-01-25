import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;
import '../models/weather_models.dart';
import '../models/chat_models.dart';

/// Configuration for the API service.
class ApiConfig {
  /// Base URL for the API.
  /// For physical devices, use your machine's IP address (e.g., 'http://192.168.1.100:8000/api/v1')
  /// For Android emulator, use 'http://10.0.2.2:8000/api/v1'
  /// For iOS simulator, use 'http://localhost:8000/api/v1'
  static String baseUrl = const String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );

  /// HTTP timeout duration
  static const Duration timeout = Duration(seconds: 30);

  /// Set the base URL programmatically
  static void setBaseUrl(String url) {
    baseUrl = url;
  }
}

/// Service for communicating with the Weather Intelligence Agent API.
///
/// This is a singleton class - use [ApiService.instance] to access it.
class ApiService {
  // Singleton instance
  static final ApiService _instance = ApiService._internal();
  static ApiService get instance => _instance;

  final http.Client _client;

  // Private constructor for singleton
  ApiService._internal() : _client = http.Client();

  // Factory constructor returns the singleton
  factory ApiService({http.Client? client}) {
    // Allow custom client for testing
    if (client != null) {
      return ApiService._withClient(client);
    }
    return _instance;
  }

  // Constructor for testing with custom client
  ApiService._withClient(this._client);

  String get baseUrl => ApiConfig.baseUrl;

  /// Send a chat message to the weather agent.
  Future<ChatResponse> sendMessage(String userId, String message) async {
    try {
      final response = await _client
          .post(
            Uri.parse('$baseUrl/chat'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'user_id': userId,
              'message': message,
            }),
          )
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        return ChatResponse.fromJson(jsonDecode(response.body));
      } else {
        throw ApiException(_parseErrorMessage(response));
      }
    } on TimeoutException {
      throw ApiException('Request timed out. Please check your connection.');
    }
  }

  /// Get current weather for a location.
  Future<CurrentWeather> getCurrentWeather({
    required double latitude,
    required double longitude,
    String temperatureUnit = 'fahrenheit',
  }) async {
    try {
      final response = await _client
          .post(
            Uri.parse('$baseUrl/weather/current?temperature_unit=$temperatureUnit'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'latitude': latitude,
              'longitude': longitude,
            }),
          )
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        return CurrentWeather.fromJson(jsonDecode(response.body));
      } else {
        throw ApiException(_parseErrorMessage(response));
      }
    } on TimeoutException {
      throw ApiException('Request timed out. Please check your connection.');
    }
  }

  /// Get weather forecast for a location.
  Future<WeatherForecast> getWeatherForecast({
    required double latitude,
    required double longitude,
    int days = 7,
    String temperatureUnit = 'fahrenheit',
  }) async {
    try {
      final response = await _client
          .post(
            Uri.parse(
                '$baseUrl/weather/forecast?days=$days&temperature_unit=$temperatureUnit'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'latitude': latitude,
              'longitude': longitude,
            }),
          )
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        return WeatherForecast.fromJson(jsonDecode(response.body));
      } else {
        throw ApiException(_parseErrorMessage(response));
      }
    } on TimeoutException {
      throw ApiException('Request timed out. Please check your connection.');
    }
  }

  /// Geocode a location name to coordinates.
  Future<List<GeocodedLocation>> geocodeLocation(String query) async {
    try {
      final response = await _client
          .post(
            Uri.parse('$baseUrl/geocode'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'query': query,
              'limit': 5,
            }),
          )
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return (data['locations'] as List)
            .map((loc) => GeocodedLocation.fromJson(loc))
            .toList();
      } else {
        throw ApiException(_parseErrorMessage(response));
      }
    } on TimeoutException {
      throw ApiException('Request timed out. Please check your connection.');
    }
  }

  /// Create or get an agent for a user.
  Future<String> createAgent(String userId) async {
    try {
      final response = await _client
          .post(
            Uri.parse('$baseUrl/agent/create'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'user_id': userId}),
          )
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['agent_id'];
      } else {
        throw ApiException(_parseErrorMessage(response));
      }
    } on TimeoutException {
      throw ApiException('Request timed out. Please check your connection.');
    }
  }

  /// Check API health status.
  Future<bool> healthCheck() async {
    try {
      final response = await _client
          .get(Uri.parse('$baseUrl/health'))
          .timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Parse error message from response, handling JSON and plain text.
  String _parseErrorMessage(http.Response response) {
    try {
      final data = jsonDecode(response.body);
      if (data is Map && data.containsKey('detail')) {
        return data['detail'].toString();
      }
      return 'Request failed with status ${response.statusCode}';
    } catch (e) {
      // Not JSON, return generic error
      return 'Request failed with status ${response.statusCode}';
    }
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}
