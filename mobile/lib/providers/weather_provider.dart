import 'package:flutter/foundation.dart';
import '../models/weather_models.dart';
import '../services/api_service.dart';

/// Provider for weather data state management.
class WeatherProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  CurrentWeather? _currentWeather;
  WeatherForecast? _forecast;
  GeocodedLocation? _currentLocation;
  List<GeocodedLocation> _favoriteLocations = [];
  String _temperatureUnit = 'fahrenheit';
  bool _isLoading = false;
  String? _error;

  // Getters
  CurrentWeather? get currentWeather => _currentWeather;
  WeatherForecast? get forecast => _forecast;
  GeocodedLocation? get currentLocation => _currentLocation;
  List<GeocodedLocation> get favoriteLocations => _favoriteLocations;
  String get temperatureUnit => _temperatureUnit;
  bool get isLoading => _isLoading;
  String? get error => _error;

  /// Set the current location and fetch weather.
  Future<void> setLocation(GeocodedLocation location) async {
    _currentLocation = location;
    notifyListeners();
    await refreshWeather();
  }

  /// Search for a location by name.
  Future<List<GeocodedLocation>> searchLocation(String query) async {
    try {
      return await _apiService.geocodeLocation(query);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return [];
    }
  }

  /// Fetch current weather for the current location.
  Future<void> fetchCurrentWeather() async {
    if (_currentLocation == null) return;

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _currentWeather = await _apiService.getCurrentWeather(
        latitude: _currentLocation!.latitude,
        longitude: _currentLocation!.longitude,
        temperatureUnit: _temperatureUnit,
      );
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Fetch weather forecast for the current location.
  Future<void> fetchForecast({int days = 7}) async {
    if (_currentLocation == null) return;

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _forecast = await _apiService.getWeatherForecast(
        latitude: _currentLocation!.latitude,
        longitude: _currentLocation!.longitude,
        days: days,
        temperatureUnit: _temperatureUnit,
      );
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Refresh all weather data.
  Future<void> refreshWeather() async {
    await Future.wait([
      fetchCurrentWeather(),
      fetchForecast(),
    ]);
  }

  /// Toggle temperature unit between Fahrenheit and Celsius.
  void toggleTemperatureUnit() {
    _temperatureUnit =
        _temperatureUnit == 'fahrenheit' ? 'celsius' : 'fahrenheit';
    notifyListeners();
    refreshWeather();
  }

  /// Add a location to favorites.
  void addFavoriteLocation(GeocodedLocation location) {
    if (!_favoriteLocations.any((loc) =>
        loc.latitude == location.latitude &&
        loc.longitude == location.longitude)) {
      _favoriteLocations.add(location);
      notifyListeners();
    }
  }

  /// Remove a location from favorites.
  void removeFavoriteLocation(GeocodedLocation location) {
    _favoriteLocations.removeWhere((loc) =>
        loc.latitude == location.latitude &&
        loc.longitude == location.longitude);
    notifyListeners();
  }

  /// Clear any error state.
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
