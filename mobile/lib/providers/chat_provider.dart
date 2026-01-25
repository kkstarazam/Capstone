import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import '../models/chat_models.dart';
import '../services/api_service.dart';

/// Provider for chat state management with the weather agent.
class ChatProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService.instance;
  final Uuid _uuid = const Uuid();

  List<ChatMessage> _messages = [];
  String? _userId;
  String? _agentId;
  bool _isTyping = false;
  String? _error;

  // Getters
  List<ChatMessage> get messages => _messages;
  String? get userId => _userId;
  String? get agentId => _agentId;
  bool get isTyping => _isTyping;
  String? get error => _error;

  /// Initialize the chat with a user ID.
  Future<void> initialize(String userId) async {
    _userId = userId;
    _messages = [];

    try {
      _agentId = await _apiService.createAgent(userId);

      // Add welcome message
      _messages.add(ChatMessage(
        id: _uuid.v4(),
        role: 'assistant',
        content:
            "Hello! I'm your Weather Intelligence Assistant. I can help you with weather forecasts, activity planning, and keeping you prepared for any weather conditions. What would you like to know?",
        timestamp: DateTime.now(),
      ));
    } catch (e) {
      _error = e.toString();
    }

    notifyListeners();
  }

  /// Send a message to the weather agent.
  Future<void> sendMessage(String content) async {
    if (_userId == null || content.trim().isEmpty) return;

    // Add user message
    final userMessage = ChatMessage(
      id: _uuid.v4(),
      role: 'user',
      content: content,
      timestamp: DateTime.now(),
    );
    _messages.add(userMessage);

    // Add loading indicator
    final loadingId = _uuid.v4();
    _messages.add(ChatMessage(
      id: loadingId,
      role: 'assistant',
      content: '',
      timestamp: DateTime.now(),
      isLoading: true,
    ));

    _isTyping = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.sendMessage(_userId!, content);

      // Remove loading indicator and add response
      _messages.removeWhere((m) => m.id == loadingId);
      _messages.add(ChatMessage(
        id: _uuid.v4(),
        role: 'assistant',
        content: response.response,
        timestamp: DateTime.now(),
      ));

      _agentId = response.agentId;
    } catch (e) {
      // Remove loading indicator and add error message
      _messages.removeWhere((m) => m.id == loadingId);
      _error = e.toString();

      _messages.add(ChatMessage(
        id: _uuid.v4(),
        role: 'assistant',
        content:
            "I'm sorry, I encountered an error processing your request. Please try again.",
        timestamp: DateTime.now(),
      ));
    } finally {
      _isTyping = false;
      notifyListeners();
    }
  }

  /// Clear the chat history.
  void clearChat() {
    _messages = [];
    _error = null;
    notifyListeners();
  }

  /// Clear any error state.
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
