import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/weather_provider.dart';
import '../providers/chat_provider.dart';
import '../widgets/weather_card.dart';
import '../widgets/forecast_list.dart';
import 'chat_screen.dart';
import 'location_search_screen.dart';

/// Main home screen showing weather overview and quick actions.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    // Initialize with a default user ID
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ChatProvider>().initialize('default_user');
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Weather Intelligence'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => _openLocationSearch(context),
            tooltip: 'Search location',
          ),
          Consumer<WeatherProvider>(
            builder: (context, provider, _) => IconButton(
              icon: Text(
                provider.temperatureUnit == 'fahrenheit' ? '°F' : '°C',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              onPressed: () => provider.toggleTemperatureUnit(),
              tooltip: 'Toggle temperature unit',
            ),
          ),
        ],
      ),
      body: Consumer<WeatherProvider>(
        builder: (context, weatherProvider, _) {
          if (weatherProvider.currentLocation == null) {
            return _buildNoLocationView(context);
          }

          return RefreshIndicator(
            onRefresh: () => weatherProvider.refreshWeather(),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Location header
                  _buildLocationHeader(context, weatherProvider),
                  const SizedBox(height: 16),

                  // Current weather card
                  if (weatherProvider.currentWeather != null)
                    WeatherCard(weather: weatherProvider.currentWeather!),

                  if (weatherProvider.isLoading)
                    const Center(
                      child: Padding(
                        padding: EdgeInsets.all(32),
                        child: CircularProgressIndicator(),
                      ),
                    ),

                  if (weatherProvider.error != null)
                    _buildErrorCard(context, weatherProvider),

                  const SizedBox(height: 24),

                  // Forecast section
                  if (weatherProvider.forecast != null) ...[
                    Text(
                      '7-Day Forecast',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 12),
                    ForecastList(forecast: weatherProvider.forecast!),
                  ],

                  const SizedBox(height: 24),

                  // Quick actions
                  _buildQuickActions(context),
                ],
              ),
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _openChat(context),
        icon: const Icon(Icons.chat_bubble_outline),
        label: const Text('Ask Weather AI'),
      ),
    );
  }

  Widget _buildNoLocationView(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.location_off,
              size: 80,
              color: Theme.of(context).colorScheme.secondary,
            ),
            const SizedBox(height: 24),
            Text(
              'No Location Set',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 12),
            Text(
              'Search for a location to see weather information',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: () => _openLocationSearch(context),
              icon: const Icon(Icons.search),
              label: const Text('Search Location'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLocationHeader(
      BuildContext context, WeatherProvider provider) {
    return Row(
      children: [
        Icon(
          Icons.location_on,
          color: Theme.of(context).colorScheme.primary,
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            provider.currentLocation?.shortName ?? 'Unknown',
            style: Theme.of(context).textTheme.titleMedium,
          ),
        ),
        TextButton(
          onPressed: () => _openLocationSearch(context),
          child: const Text('Change'),
        ),
      ],
    );
  }

  Widget _buildErrorCard(BuildContext context, WeatherProvider provider) {
    return Card(
      color: Theme.of(context).colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              Icons.error_outline,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                provider.error ?? 'An error occurred',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onErrorContainer,
                ),
              ),
            ),
            IconButton(
              icon: const Icon(Icons.close),
              onPressed: () => provider.clearError(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Questions',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            _buildQuickActionChip(context, "What's my day looking like?"),
            _buildQuickActionChip(context, 'When should I go running?'),
            _buildQuickActionChip(context, 'Will it rain today?'),
            _buildQuickActionChip(context, 'What should I wear?'),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickActionChip(BuildContext context, String question) {
    return ActionChip(
      label: Text(question),
      onPressed: () {
        final chatProvider = context.read<ChatProvider>();
        chatProvider.sendMessage(question);
        _openChat(context);
      },
    );
  }

  void _openLocationSearch(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const LocationSearchScreen()),
    );
  }

  void _openChat(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const ChatScreen()),
    );
  }
}
