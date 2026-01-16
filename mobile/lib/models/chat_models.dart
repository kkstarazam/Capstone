/// Chat models for agent conversations.

class ChatMessage {
  final String id;
  final String role;
  final String content;
  final DateTime timestamp;
  final bool isLoading;

  ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    required this.timestamp,
    this.isLoading = false,
  });

  bool get isUser => role == 'user';
  bool get isAssistant => role == 'assistant';

  ChatMessage copyWith({
    String? id,
    String? role,
    String? content,
    DateTime? timestamp,
    bool? isLoading,
  }) {
    return ChatMessage(
      id: id ?? this.id,
      role: role ?? this.role,
      content: content ?? this.content,
      timestamp: timestamp ?? this.timestamp,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class ChatResponse {
  final String response;
  final List<Map<String, dynamic>>? toolCalls;
  final String agentId;

  ChatResponse({
    required this.response,
    this.toolCalls,
    required this.agentId,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      response: json['response'] ?? '',
      toolCalls: json['tool_calls'] != null
          ? List<Map<String, dynamic>>.from(json['tool_calls'])
          : null,
      agentId: json['agent_id'] ?? '',
    );
  }
}
