/// Weather data models for the mobile app.

class CurrentWeather {
  final double temperature;
  final double feelsLike;
  final int humidity;
  final double precipitation;
  final int cloudCover;
  final double windSpeed;
  final int windDirection;
  final String weatherDescription;
  final bool isDay;
  final String temperatureUnit;

  CurrentWeather({
    required this.temperature,
    required this.feelsLike,
    required this.humidity,
    required this.precipitation,
    required this.cloudCover,
    required this.windSpeed,
    required this.windDirection,
    required this.weatherDescription,
    required this.isDay,
    required this.temperatureUnit,
  });

  factory CurrentWeather.fromJson(Map<String, dynamic> json) {
    return CurrentWeather(
      temperature: (json['temperature'] ?? 0).toDouble(),
      feelsLike: (json['feels_like'] ?? 0).toDouble(),
      humidity: json['humidity'] ?? 0,
      precipitation: (json['precipitation'] ?? 0).toDouble(),
      cloudCover: json['cloud_cover'] ?? 0,
      windSpeed: (json['wind_speed'] ?? 0).toDouble(),
      windDirection: json['wind_direction'] ?? 0,
      weatherDescription: json['weather_description'] ?? 'Unknown',
      isDay: json['is_day'] ?? true,
      temperatureUnit: json['temperature_unit'] ?? 'fahrenheit',
    );
  }

  String get temperatureDisplay {
    final unit = temperatureUnit == 'celsius' ? '°C' : '°F';
    return '${temperature.round()}$unit';
  }
}

class DailyForecast {
  final String date;
  final String weatherDescription;
  final double tempHigh;
  final double tempLow;
  final int? precipitationProbability;
  final double? precipitation;
  final double? windSpeedMax;
  final double? uvIndexMax;

  DailyForecast({
    required this.date,
    required this.weatherDescription,
    required this.tempHigh,
    required this.tempLow,
    this.precipitationProbability,
    this.precipitation,
    this.windSpeedMax,
    this.uvIndexMax,
  });

  factory DailyForecast.fromJson(Map<String, dynamic> json) {
    return DailyForecast(
      date: json['date'] ?? '',
      weatherDescription: json['weather_description'] ?? 'Unknown',
      tempHigh: (json['temp_high'] ?? 0).toDouble(),
      tempLow: (json['temp_low'] ?? 0).toDouble(),
      precipitationProbability: json['precipitation_probability'],
      precipitation: json['precipitation']?.toDouble(),
      windSpeedMax: json['wind_speed_max']?.toDouble(),
      uvIndexMax: json['uv_index_max']?.toDouble(),
    );
  }
}

class WeatherForecast {
  final List<DailyForecast> forecasts;
  final String temperatureUnit;
  final String timezone;

  WeatherForecast({
    required this.forecasts,
    required this.temperatureUnit,
    required this.timezone,
  });

  factory WeatherForecast.fromJson(Map<String, dynamic> json) {
    return WeatherForecast(
      forecasts: (json['forecasts'] as List)
          .map((f) => DailyForecast.fromJson(f))
          .toList(),
      temperatureUnit: json['temperature_unit'] ?? 'fahrenheit',
      timezone: json['timezone'] ?? 'UTC',
    );
  }
}

class GeocodedLocation {
  final double latitude;
  final double longitude;
  final String displayName;
  final String? name;
  final String? city;
  final String? state;
  final String? country;

  GeocodedLocation({
    required this.latitude,
    required this.longitude,
    required this.displayName,
    this.name,
    this.city,
    this.state,
    this.country,
  });

  factory GeocodedLocation.fromJson(Map<String, dynamic> json) {
    final address = json['address'] as Map<String, dynamic>?;
    return GeocodedLocation(
      latitude: (json['latitude'] ?? 0).toDouble(),
      longitude: (json['longitude'] ?? 0).toDouble(),
      displayName: json['display_name'] ?? '',
      name: json['name'],
      city: address?['city'],
      state: address?['state'],
      country: address?['country'],
    );
  }

  String get shortName {
    if (city != null && state != null) {
      return '$city, $state';
    } else if (city != null) {
      return city!;
    } else if (name != null) {
      return name!;
    }
    return displayName.split(',').first;
  }
}
