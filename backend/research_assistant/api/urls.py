"""REST API URL configuration."""
from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    # ── Auth ────────────────────────────────────
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/me/", views.CurrentUserView.as_view(), name="current-user"),
    path("auth/refresh/", views.RefreshTokenView.as_view(), name="refresh-token"),

    # ── Projects ────────────────────────────────
    path("projects/", views.ProjectListCreateView.as_view(), name="project-list"),
    path("projects/<uuid:pk>/", views.ProjectDetailView.as_view(), name="project-detail"),
    path(
        "projects/<uuid:pk>/collaborators/",
        views.ProjectCollaboratorView.as_view(),
        name="project-collaborators",
    ),

    # ── Papers ──────────────────────────────────
    path("papers/", views.PaperListView.as_view(), name="paper-list"),
    path("papers/upload/", views.PaperUploadView.as_view(), name="paper-upload"),
    path("papers/<uuid:pk>/", views.PaperDetailView.as_view(), name="paper-detail"),
    path("papers/<uuid:pk>/chunks/", views.PaperChunksView.as_view(), name="paper-chunks"),
    path("papers/<uuid:pk>/summary/", views.PaperSummaryView.as_view(), name="paper-summary"),
    path("papers/<uuid:pk>/citations/", views.PaperCitationsView.as_view(), name="paper-citations"),

    # ── Conversations ───────────────────────────
    path("conversations/", views.ConversationListCreateView.as_view(), name="conversation-list"),
    path(
        "conversations/<uuid:pk>/",
        views.ConversationDetailView.as_view(),
        name="conversation-detail",
    ),

    # ── RAG Query ───────────────────────────────
    path("query/", views.QueryView.as_view(), name="query"),
    path("query/history/", views.QueryHistoryView.as_view(), name="query-history"),
    path("query/<uuid:pk>/evaluate/", views.QueryEvaluateView.as_view(), name="query-evaluate"),

    # ── Synthesis Reports ───────────────────────
    path("reports/", views.SynthesisReportListView.as_view(), name="report-list"),
    path("reports/generate/", views.SynthesisReportGenerateView.as_view(), name="report-generate"),
    path("reports/<uuid:pk>/", views.SynthesisReportDetailView.as_view(), name="report-detail"),

    # ── Agent Monitoring ────────────────────────
    path("agents/", views.AgentListView.as_view(), name="agent-list"),
    path("agents/logs/", views.AgentLogListView.as_view(), name="agent-log-list"),
    path("agents/interactions/", views.AgentInteractionListView.as_view(), name="agent-interactions"),

    # ── API Keys ────────────────────────────────
    path("settings/api-keys/", views.APIKeyListCreateView.as_view(), name="apikey-list"),
    path("settings/api-keys/<uuid:pk>/", views.APIKeyDetailView.as_view(), name="apikey-detail"),

    # ── Exports ─────────────────────────────────
    path("exports/", views.ExportListCreateView.as_view(), name="export-list"),
    path("exports/<uuid:pk>/", views.ExportDetailView.as_view(), name="export-detail"),
    path("exports/<uuid:pk>/download/", views.ExportDownloadView.as_view(), name="export-download"),

    # ── Annotations & Bookmarks ─────────────────
    path("annotations/", views.AnnotationListCreateView.as_view(), name="annotation-list"),
    path("annotations/<uuid:pk>/", views.AnnotationDetailView.as_view(), name="annotation-detail"),
    path("bookmarks/", views.BookmarkListCreateView.as_view(), name="bookmark-list"),
    path("bookmarks/<uuid:pk>/", views.BookmarkDetailView.as_view(), name="bookmark-detail"),

    # ── Analytics Dashboard ─────────────────────
    path("analytics/dashboard/", views.AnalyticsDashboardView.as_view(), name="analytics-dashboard"),
    path("analytics/usage/", views.UsageAnalyticsView.as_view(), name="analytics-usage"),

    # ── Health Check ────────────────────────────
    path("health/", views.health_check, name="health"),
]
