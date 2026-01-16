import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/weather_models.dart';

/// List displaying weather forecast.
class ForecastList extends StatelessWidget {
  final WeatherForecast forecast;

  const ForecastList({super.key, required this.forecast});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: forecast.forecasts.map((day) {
        return _ForecastDayCard(
          forecast: day,
          temperatureUnit: forecast.temperatureUnit,
        );
      }).toList(),
    );
  }
}

class _ForecastDayCard extends StatelessWidget {
  final DailyForecast forecast;
  final String temperatureUnit;

  const _ForecastDayCard({
    required this.forecast,
    required this.temperatureUnit,
  });

  @override
  Widget build(BuildContext context) {
    final date = DateTime.parse(forecast.date);
    final isToday = _isToday(date);
    final isTomorrow = _isTomorrow(date);

    String dayLabel;
    if (isToday) {
      dayLabel = 'Today';
    } else if (isTomorrow) {
      dayLabel = 'Tomorrow';
    } else {
      dayLabel = DateFormat('EEEE').format(date);
    }

    final unit = temperatureUnit == 'celsius' ? '°C' : '°F';

    return Card(
      elevation: 0,
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            // Day and date
            SizedBox(
              width: 100,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    dayLabel,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: isToday ? FontWeight.bold : FontWeight.normal,
                        ),
                  ),
                  Text(
                    DateFormat('MMM d').format(date),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                  ),
                ],
              ),
            ),

            // Weather icon
            Icon(
              _getWeatherIcon(forecast.weatherDescription),
              size: 28,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(width: 12),

            // Weather description
            Expanded(
              child: Text(
                forecast.weatherDescription,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ),

            // Temperature range
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${forecast.tempHigh.round()}$unit',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                Text(
                  '${forecast.tempLow.round()}$unit',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                ),
              ],
            ),

            // Precipitation probability
            if (forecast.precipitationProbability != null &&
                forecast.precipitationProbability! > 0) ...[
              const SizedBox(width: 16),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.secondaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.water_drop,
                      size: 14,
                      color: Theme.of(context).colorScheme.onSecondaryContainer,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${forecast.precipitationProbability}%',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color:
                                Theme.of(context).colorScheme.onSecondaryContainer,
                          ),
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

  bool _isToday(DateTime date) {
    final now = DateTime.now();
    return date.year == now.year &&
        date.month == now.month &&
        date.day == now.day;
  }

  bool _isTomorrow(DateTime date) {
    final tomorrow = DateTime.now().add(const Duration(days: 1));
    return date.year == tomorrow.year &&
        date.month == tomorrow.month &&
        date.day == tomorrow.day;
  }

  IconData _getWeatherIcon(String description) {
    final desc = description.toLowerCase();
    if (desc.contains('clear') || desc.contains('sunny')) {
      return Icons.wb_sunny;
    } else if (desc.contains('partly')) {
      return Icons.cloud_queue;
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
