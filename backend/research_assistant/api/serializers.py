"""REST API Serializers."""
from rest_framework import serializers

from ..models import (
    AgentInteraction,
    AgentLog,
    Annotation,
    APIKeyConfig,
    Bookmark,
    Conversation,
    ExportJob,
    Message,
    PaperChunk,
    ProjectCollaborator,
    QueryEvaluation,
    QueryHistory,
    ResearchPaper,
    ResearchProject,
    SynthesisReport,
    SynthesisSection,
    User,
)


# ── Auth ────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "password",
            "first_name", "last_name", "institution", "bio",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    quota_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "bio", "institution", "research_interests", "avatar_url",
            "usage_quota_tokens", "tokens_used_this_month",
            "quota_remaining", "created_at",
        ]
        read_only_fields = [
            "id", "username", "usage_quota_tokens",
            "tokens_used_this_month", "created_at",
        ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


# ── Projects ────────────────────────────────────
class ProjectCollaboratorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = ProjectCollaborator
        fields = ["id", "user", "username", "email", "role", "created_at"]


class ResearchProjectSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.username", read_only=True)
    collaborators = ProjectCollaboratorSerializer(many=True, read_only=True)

    class Meta:
        model = ResearchProject
        fields = [
            "id", "name", "description", "tags", "is_public",
            "status", "paper_count", "total_chunks",
            "owner", "owner_name", "collaborators",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "owner", "paper_count", "total_chunks",
            "status", "created_at", "updated_at",
        ]


class ResearchProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchProject
        fields = ["name", "description", "tags", "is_public"]


# ── Papers ──────────────────────────────────────
class PaperChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperChunk
        fields = [
            "id", "chunk_index", "content", "page_number",
            "token_count", "metadata",
        ]


class ResearchPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchPaper
        fields = [
            "id", "project", "title", "authors", "abstract",
            "publication_date", "journal", "doi", "file_name",
            "file_size", "page_count", "chunk_count",
            "processing_status", "processing_error",
            "metadata", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "page_count", "chunk_count",
            "processing_status", "processing_error",
            "created_at", "updated_at",
        ]


class PaperUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    title = serializers.CharField(required=False, default="")
    project_id = serializers.UUIDField()


# ── Conversations ───────────────────────────────
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id", "role", "content", "sources",
            "agent_name", "token_count", "latency_ms",
            "metadata", "created_at",
        ]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id", "project", "title", "is_pinned",
            "message_count", "messages", "last_message",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "message_count", "created_at", "updated_at"]

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        return MessageSerializer(msg).data if msg else None


class ConversationListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id", "project", "title", "is_pinned",
            "message_count", "last_message",
            "created_at", "updated_at",
        ]

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if msg:
            return {"role": msg.role, "content": msg.content[:200], "created_at": msg.created_at}
        return None


class QueryRequestSerializer(serializers.Serializer):
    question = serializers.CharField()
    project_id = serializers.UUIDField()
    conversation_id = serializers.UUIDField(required=False)
    run_evaluation = serializers.BooleanField(default=True)


# ── Query History & Evaluation ──────────────────
class QueryEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryEvaluation
        fields = [
            "id", "eval_type", "score", "explanation",
            "evaluator_model", "created_at",
        ]


class QueryHistorySerializer(serializers.ModelSerializer):
    evaluations = QueryEvaluationSerializer(many=True, read_only=True)

    class Meta:
        model = QueryHistory
        fields = [
            "id", "question", "answer", "context_chunks",
            "model_used", "prompt_tokens", "completion_tokens",
            "total_tokens", "latency_ms", "agents_involved",
            "evaluations", "created_at",
        ]


# ── Synthesis Reports ───────────────────────────
class SynthesisSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SynthesisSection
        fields = ["id", "title", "content", "order", "source_papers", "citations"]


class SynthesisReportSerializer(serializers.ModelSerializer):
    sections = SynthesisSectionSerializer(many=True, read_only=True)

    class Meta:
        model = SynthesisReport
        fields = [
            "id", "project", "title", "description",
            "report_type", "content_markdown", "papers_included",
            "status", "output_format", "total_tokens_used",
            "generation_time_ms", "sections",
            "created_at", "updated_at",
        ]


class SynthesisReportCreateSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    report_type = serializers.ChoiceField(
        choices=[
            "literature_review",
            "comparative_analysis",
            "research_gap",
            "trend_analysis",
            "executive_summary",
        ]
    )
    title = serializers.CharField(required=False, default="")


# ── Agent Logs ──────────────────────────────────
class AgentLogSerializer(serializers.ModelSerializer):
    child_logs = serializers.SerializerMethodField()
    outgoing_interactions = serializers.SerializerMethodField()
    parent_log_id = serializers.UUIDField(source="parent_log.id", read_only=True, allow_null=True)
    parent_agent_name = serializers.CharField(source="parent_log.agent_name", read_only=True, allow_null=True)

    class Meta:
        model = AgentLog
        fields = [
            "id", "agent_name", "task_id", "status",
            "input_data", "output_data", "error_message",
            "duration_ms", "tokens_used",
            "parent_log_id", "parent_agent_name",
            "child_logs", "outgoing_interactions",
            "created_at", "updated_at",
        ]

    def get_child_logs(self, obj):
        children = obj.child_logs.all()[:10]
        # Include full details for audit trail visibility
        return [
            {
                "id": str(c.id),
                "agent_name": c.agent_name,
                "task_id": c.task_id,
                "status": c.status,
                "input_data": c.input_data,
                "output_data": c.output_data,
                "error_message": c.error_message,
                "duration_ms": c.duration_ms,
                "tokens_used": c.tokens_used,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in children
        ]

    def get_outgoing_interactions(self, obj):
        interactions = obj.outgoing_interactions.all()[:10]
        return [
            {
                "id": str(i.id),
                "target_agent": i.target_agent,
                "status": i.status,
                "duration_ms": i.duration_ms,
                "request_summary": _summarize_payload(i.request_payload),
                "response_summary": _summarize_payload(i.response_payload),
            }
            for i in interactions
        ]


def _summarize_payload(payload: dict, max_length: int = 200) -> str:
    """Create a brief summary of a payload for display."""
    if not payload:
        return ""
    if "error" in payload:
        return f"Error: {payload['error'][:100]}"
    keys = list(payload.keys())[:5]
    summary = ", ".join(keys)
    if len(keys) < len(payload):
        summary += f" (+{len(payload) - len(keys)} more)"
    return summary


class AgentInteractionSerializer(serializers.ModelSerializer):
    parent_log_id = serializers.UUIDField(source="parent_log.id", read_only=True, allow_null=True)
    child_log_id = serializers.UUIDField(source="child_log.id", read_only=True, allow_null=True)
    parent_agent_name = serializers.CharField(source="parent_log.agent_name", read_only=True, allow_null=True)
    child_agent_status = serializers.CharField(source="child_log.status", read_only=True, allow_null=True)

    class Meta:
        model = AgentInteraction
        fields = [
            "id", "source_agent", "target_agent", "protocol",
            "request_payload", "response_payload", "status",
            "duration_ms",
            "parent_log_id", "child_log_id",
            "parent_agent_name", "child_agent_status",
            "created_at",
        ]


# ── API Key Config ──────────────────────────────
class APIKeyConfigSerializer(serializers.ModelSerializer):
    api_key_masked = serializers.SerializerMethodField()

    class Meta:
        model = APIKeyConfig
        fields = [
            "id", "provider", "base_url", "is_active",
            "api_key_masked", "last_verified", "created_at",
        ]

    def get_api_key_masked(self, obj):
        if obj.api_key:
            return f"{'*' * (len(obj.api_key) - 4)}{obj.api_key[-4:]}"
        return ""


class APIKeyConfigCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKeyConfig
        fields = ["provider", "api_key", "base_url"]


# ── Exports ─────────────────────────────────────
class ExportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportJob
        fields = [
            "id", "export_type", "output_format", "status",
            "file", "error_message", "parameters",
            "created_at", "completed_at",
        ]


class ExportJobCreateSerializer(serializers.Serializer):
    export_type = serializers.ChoiceField(
        choices=[
            "query_history", "synthesis_report",
            "paper_citations", "analytics_data", "conversation",
        ]
    )
    output_format = serializers.ChoiceField(
        choices=["pdf", "docx", "csv", "xlsx", "markdown", "json", "bibtex"]
    )
    parameters = serializers.DictField(required=False, default=dict)


# ── Annotations & Bookmarks ────────────────────
class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = [
            "id", "paper", "chunk", "content",
            "highlight_text", "page_number", "color",
            "created_at", "updated_at",
        ]


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = [
            "id", "paper", "conversation", "note", "created_at",
        ]


# ── Analytics ───────────────────────────────────
class AnalyticsDashboardSerializer(serializers.Serializer):
    total_projects = serializers.IntegerField()
    total_papers = serializers.IntegerField()
    total_queries = serializers.IntegerField()
    total_tokens_used = serializers.IntegerField()
    avg_groundedness_score = serializers.FloatField()
    avg_relevance_score = serializers.FloatField()
    queries_by_day = serializers.ListField()
    top_papers = serializers.ListField()
    agent_performance = serializers.ListField()
