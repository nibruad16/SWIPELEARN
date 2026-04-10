/// Data model for a Knowledge Card.
/// Maps directly to the backend KnowledgeCard schema.

class KnowledgeCard {
  final String id;
  final String sourceUrl;
  final String title;
  final String? author;
  final String? teacherId;
  final String tlDr;
  final List<String> keyPoints;
  final String stealInsight;
  final DateTime createdAt;
  final bool isSaved;

  KnowledgeCard({
    required this.id,
    required this.sourceUrl,
    required this.title,
    this.author,
    this.teacherId,
    required this.tlDr,
    required this.keyPoints,
    required this.stealInsight,
    required this.createdAt,
    this.isSaved = false,
  });

  factory KnowledgeCard.fromJson(Map<String, dynamic> json) {
    return KnowledgeCard(
      id: json['id'] as String,
      sourceUrl: json['source_url'] as String,
      title: json['title'] as String,
      author: json['author'] as String?,
      teacherId: json['teacher_id'] as String?,
      tlDr: json['tl_dr'] as String,
      keyPoints: (json['key_points'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      stealInsight: json['steal_insight'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      isSaved: json['is_saved'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'source_url': sourceUrl,
    'title': title,
    'author': author,
    'teacher_id': teacherId,
    'tl_dr': tlDr,
    'key_points': keyPoints,
    'steal_insight': stealInsight,
    'created_at': createdAt.toIso8601String(),
    'is_saved': isSaved,
  };

  KnowledgeCard copyWith({bool? isSaved}) {
    return KnowledgeCard(
      id: id,
      sourceUrl: sourceUrl,
      title: title,
      author: author,
      teacherId: teacherId,
      tlDr: tlDr,
      keyPoints: keyPoints,
      stealInsight: stealInsight,
      createdAt: createdAt,
      isSaved: isSaved ?? this.isSaved,
    );
  }
}
