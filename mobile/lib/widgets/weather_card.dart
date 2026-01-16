import 'package:flutter/material.dart';
import '../models/weather_models.dart';

/// Card displaying current weather conditions.
class WeatherCard extends StatelessWidget {
  final CurrentWeather weather;

  const WeatherCard({super.key, required this.weather});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      color: Theme.of(context).colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // Weather icon and temperature
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  _getWeatherIcon(weather.weatherDescription),
                  size: 64,
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                ),
                const SizedBox(width: 16),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      weather.temperatureDisplay,
                      style: Theme.of(context).textTheme.displayMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Theme.of(context).colorScheme.onPrimaryContainer,
                          ),
                    ),
                    Text(
                      weather.weatherDescription,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: Theme.of(context).colorScheme.onPrimaryContainer,
                          ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Weather details grid
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildDetailItem(
                  context,
                  Icons.thermostat,
                  'Feels like',
                  '${weather.feelsLike.round()}°',
                ),
                _buildDetailItem(
                  context,
                  Icons.water_drop,
                  'Humidity',
                  '${weather.humidity}%',
                ),
                _buildDetailItem(
                  context,
                  Icons.air,
                  'Wind',
                  '${weather.windSpeed.round()} mph',
                ),
              ],
            ),

            if (weather.precipitation > 0) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.umbrella, size: 18),
                    const SizedBox(width: 8),
                    Text(
                      'Precipitation: ${weather.precipitation}" today',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDetailItem(
    BuildContext context,
    IconData icon,
    String label,
    String value,
  ) {
    return Column(
      children: [
        Icon(
          icon,
          size: 24,
          color: Theme.of(context).colorScheme.onPrimaryContainer.withOpacity(0.7),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: Theme.of(context).colorScheme.onPrimaryContainer,
              ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onPrimaryContainer.withOpacity(0.7),
              ),
        ),
      ],
    );
  }

  IconData _getWeatherIcon(String description) {
    final desc = description.toLowerCase();
    if (desc.contains('clear') || desc.contains('sunny')) {
      return Icons.wb_sunny;
    } else if (desc.contains('cloud') || desc.contains('overcast')) {
      return Icons.cloud;
    } else if (desc.contains('rain') || desc.contains('drizzle')) {
      return Icons.water_drop;
    } else if (desc.contains('snow')) {
      return Icons.ac_unit;
    } else if (desc.contains('thunder')) {
      return Icons.bolt;
    } else if (desc.contains('fog') || desc.contains('mist')) {
      return Icons.foggy;
    }
    return Icons.cloud;
  }
}
