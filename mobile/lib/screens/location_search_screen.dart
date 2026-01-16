import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/weather_provider.dart';
import '../models/weather_models.dart';

/// Screen for searching and selecting locations.
class LocationSearchScreen extends StatefulWidget {
  const LocationSearchScreen({super.key});

  @override
  State<LocationSearchScreen> createState() => _LocationSearchScreenState();
}

class _LocationSearchScreenState extends State<LocationSearchScreen> {
  final TextEditingController _controller = TextEditingController();
  List<GeocodedLocation> _searchResults = [];
  bool _isSearching = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _search(String query) async {
    if (query.trim().isEmpty) {
      setState(() {
        _searchResults = [];
      });
      return;
    }

    setState(() {
      _isSearching = true;
    });

    final results =
        await context.read<WeatherProvider>().searchLocation(query);

    setState(() {
      _searchResults = results;
      _isSearching = false;
    });
  }

  void _selectLocation(GeocodedLocation location) {
    context.read<WeatherProvider>().setLocation(location);
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final weatherProvider = context.watch<WeatherProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Search Location'),
      ),
      body: Column(
        children: [
          // Search input
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _controller,
              decoration: InputDecoration(
                hintText: 'Search city or address...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _controller.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _controller.clear();
                          setState(() {
                            _searchResults = [];
                          });
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              onChanged: _search,
            ),
          ),

          // Loading indicator
          if (_isSearching)
            const LinearProgressIndicator(),

          // Favorites section (when not searching)
          if (_searchResults.isEmpty &&
              weatherProvider.favoriteLocations.isNotEmpty) ...[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  const Icon(Icons.star, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'Favorite Locations',
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
            ...weatherProvider.favoriteLocations.map(
              (location) => _buildLocationTile(
                context,
                location,
                isFavorite: true,
              ),
            ),
            const Divider(height: 32),
          ],

          // Search results
          Expanded(
            child: _searchResults.isEmpty
                ? _buildEmptyState(context)
                : ListView.builder(
                    itemCount: _searchResults.length,
                    itemBuilder: (context, index) {
                      final location = _searchResults[index];
                      final isFavorite = weatherProvider.favoriteLocations.any(
                        (fav) =>
                            fav.latitude == location.latitude &&
                            fav.longitude == location.longitude,
                      );
                      return _buildLocationTile(
                        context,
                        location,
                        isFavorite: isFavorite,
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.search,
            size: 64,
            color: Theme.of(context).colorScheme.secondary.withOpacity(0.5),
          ),
          const SizedBox(height: 16),
          Text(
            'Search for a city or address',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildLocationTile(
    BuildContext context,
    GeocodedLocation location, {
    bool isFavorite = false,
  }) {
    final weatherProvider = context.read<WeatherProvider>();

    return ListTile(
      leading: CircleAvatar(
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
        child: Icon(
          Icons.location_on,
          color: Theme.of(context).colorScheme.primary,
        ),
      ),
      title: Text(location.shortName),
      subtitle: Text(
        location.displayName,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      trailing: IconButton(
        icon: Icon(
          isFavorite ? Icons.star : Icons.star_border,
          color: isFavorite
              ? Theme.of(context).colorScheme.primary
              : Theme.of(context).colorScheme.onSurfaceVariant,
        ),
        onPressed: () {
          if (isFavorite) {
            weatherProvider.removeFavoriteLocation(location);
          } else {
            weatherProvider.addFavoriteLocation(location);
          }
          setState(() {});
        },
      ),
      onTap: () => _selectLocation(location),
    );
  }
}
