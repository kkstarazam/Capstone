import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_core/firebase_core.dart';
import 'api_service.dart';

/// Service for handling push notifications.
class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();
  FirebaseMessaging? _firebaseMessaging;
  String? _deviceToken;
  bool _initialized = false;

  String? get deviceToken => _deviceToken;
  bool get isInitialized => _initialized;

  /// Initialize the notification service.
  Future<void> initialize() async {
    if (_initialized) return;

    // Initialize local notifications
    const androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    // Try to initialize Firebase
    try {
      await Firebase.initializeApp();
      _firebaseMessaging = FirebaseMessaging.instance;

      // Request permission
      final settings = await _firebaseMessaging!.requestPermission(
        alert: true,
        badge: true,
        sound: true,
      );

      if (settings.authorizationStatus == AuthorizationStatus.authorized) {
        // Get device token
        _deviceToken = await _firebaseMessaging!.getToken();
        print('FCM Token: $_deviceToken');

        // Listen for token refresh
        _firebaseMessaging!.onTokenRefresh.listen((token) {
          _deviceToken = token;
          print('FCM Token refreshed: $token');
        });

        // Handle foreground messages
        FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

        // Handle background/terminated messages
        FirebaseMessaging.onMessageOpenedApp.listen(_handleMessageOpenedApp);
      }
    } catch (e) {
      print('Firebase initialization failed: $e');
      // App can still work without Firebase for local notifications
    }

    _initialized = true;
  }

  /// Register device token with the backend.
  Future<bool> registerWithBackend(String userId) async {
    if (_deviceToken == null) return false;

    try {
      final api = ApiService();
      // This would call the backend endpoint
      print('Registering device token for user: $userId');
      return true;
    } catch (e) {
      print('Failed to register device: $e');
      return false;
    }
  }

  /// Show a local notification.
  Future<void> showLocalNotification({
    required String title,
    required String body,
    String? payload,
  }) async {
    const androidDetails = AndroidNotificationDetails(
      'weather_alerts',
      'Weather Alerts',
      channelDescription: 'Notifications for weather alerts and updates',
      importance: Importance.high,
      priority: Priority.high,
      showWhen: true,
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _localNotifications.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title,
      body,
      details,
      payload: payload,
    );
  }

  /// Show a weather alert notification.
  Future<void> showWeatherAlert({
    required String location,
    required String message,
    required String severity,
  }) async {
    final icon = _getSeverityIcon(severity);
    await showLocalNotification(
      title: '$icon Weather Alert - $location',
      body: message,
      payload: 'weather_alert',
    );
  }

  String _getSeverityIcon(String severity) {
    switch (severity) {
      case 'severe':
        return '🚨';
      case 'warning':
        return '⚠️';
      default:
        return 'ℹ️';
    }
  }

  void _onNotificationTapped(NotificationResponse response) {
    print('Notification tapped: ${response.payload}');
    // Handle navigation based on payload
  }

  void _handleForegroundMessage(RemoteMessage message) {
    print('Foreground message: ${message.notification?.title}');

    // Show local notification for foreground messages
    if (message.notification != null) {
      showLocalNotification(
        title: message.notification!.title ?? 'Weather Update',
        body: message.notification!.body ?? '',
        payload: message.data['type'],
      );
    }
  }

  void _handleMessageOpenedApp(RemoteMessage message) {
    print('Message opened app: ${message.data}');
    // Handle navigation when app is opened from notification
  }

  /// Cancel all notifications.
  Future<void> cancelAll() async {
    await _localNotifications.cancelAll();
  }

  /// Cancel a specific notification.
  Future<void> cancel(int id) async {
    await _localNotifications.cancel(id);
  }
}
