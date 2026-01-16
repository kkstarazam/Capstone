import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/weather_models.dart';
import '../models/chat_models.dart';

/// Service for communicating with the Weather Intelligence Agent API.
class ApiService {
  // Configure this to your backend URL
  static const String baseUrl = 'http://localhost:8000/api/v1';

  final http.Client _client;

  ApiService({http.Client? client}) : _client = client ?? http.Client();

  /// Send a chat message to the weather agent.
  Future<ChatResponse> sendMessage(String userId, String message) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/chat'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'message': message,
      }),
    );

    if (response.statusCode == 200) {
      return ChatResponse.fromJson(jsonDecode(response.body));
    } else {
      throw ApiException('Failed to send message: ${response.body}');
    }
  }

  /// Get current weather for a location.
  Future<CurrentWeather> getCurrentWeather({
    required double latitude,
    required double longitude,
    String temperatureUnit = 'fahrenheit',
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/weather/current?temperature_unit=$temperatureUnit'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'latitude': latitude,
        'longitude': longitude,
      }),
    );

    if (response.statusCode == 200) {
      return CurrentWeather.fromJson(jsonDecode(response.body));
    } else {
      throw ApiException('Failed to fetch weather: ${response.body}');
    }
  }

  /// Get weather forecast for a location.
  Future<WeatherForecast> getWeatherForecast({
    required double latitude,
    required double longitude,
    int days = 7,
    String temperatureUnit = 'fahrenheit',
  }) async {
    final response = await _client.post(
      Uri.parse(
          '$baseUrl/weather/forecast?days=$days&temperature_unit=$temperatureUnit'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'latitude': latitude,
        'longitude': longitude,
      }),
    );

    if (response.statusCode == 200) {
      return WeatherForecast.fromJson(jsonDecode(response.body));
    } else {
      throw ApiException('Failed to fetch forecast: ${response.body}');
    }
  }

  /// Geocode a location name to coordinates.
  Future<List<GeocodedLocation>> geocodeLocation(String query) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/geocode'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'query': query,
        'limit': 5,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['locations'] as List)
          .map((loc) => GeocodedLocation.fromJson(loc))
          .toList();
    } else {
      throw ApiException('Failed to geocode: ${response.body}');
    }
  }

  /// Create or get an agent for a user.
  Future<String> createAgent(String userId) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/agent/create'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['agent_id'];
    } else {
      throw ApiException('Failed to create agent: ${response.body}');
    }
  }

  /// Check API health status.
  Future<bool> healthCheck() async {
    try {
      final response = await _client.get(Uri.parse('$baseUrl/health'));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}
