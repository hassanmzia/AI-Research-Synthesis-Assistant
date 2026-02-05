"""Django Admin configuration."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
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


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "username", "email", "institution",
        "tokens_used_this_month", "is_active",
    ]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Research Profile", {
            "fields": ("bio", "institution", "research_interests", "avatar_url"),
        }),
        ("Usage", {
            "fields": ("usage_quota_tokens", "tokens_used_this_month"),
        }),
    )


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "status", "paper_count", "created_at"]
    list_filter = ["status"]
    search_fields = ["name", "description"]


@admin.register(ResearchPaper)
class ResearchPaperAdmin(admin.ModelAdmin):
    list_display = [
        "title", "project", "processing_status",
        "page_count", "chunk_count", "created_at",
    ]
    list_filter = ["processing_status"]
    search_fields = ["title"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "user", "message_count", "created_at"]


@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "question", "model_used", "total_tokens",
        "latency_ms", "created_at",
    ]
    list_filter = ["model_used"]


@admin.register(QueryEvaluation)
class QueryEvaluationAdmin(admin.ModelAdmin):
    list_display = ["eval_type", "score", "evaluator_model", "created_at"]
    list_filter = ["eval_type", "score"]


@admin.register(SynthesisReport)
class SynthesisReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "status", "created_at"]
    list_filter = ["report_type", "status"]


@admin.register(AgentLog)
class AgentLogAdmin(admin.ModelAdmin):
    list_display = [
        "agent_name", "status", "duration_ms",
        "tokens_used", "created_at",
    ]
    list_filter = ["agent_name", "status"]


@admin.register(AgentInteraction)
class AgentInteractionAdmin(admin.ModelAdmin):
    list_display = [
        "source_agent", "target_agent", "protocol",
        "status", "duration_ms", "created_at",
    ]
    list_filter = ["protocol", "status"]


admin.site.register(PaperChunk)
admin.site.register(ProjectCollaborator)
admin.site.register(SynthesisSection)
admin.site.register(Message)
admin.site.register(APIKeyConfig)
admin.site.register(ExportJob)
admin.site.register(Annotation)
admin.site.register(Bookmark)

admin.site.site_header = "AI Research Synthesis Assistant"
admin.site.site_title = "ARSA Admin"
