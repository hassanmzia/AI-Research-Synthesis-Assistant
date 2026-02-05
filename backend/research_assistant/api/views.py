"""REST API Views."""
import datetime
import logging

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

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
    User,
)
from .serializers import (
    AgentInteractionSerializer,
    AgentLogSerializer,
    AnnotationSerializer,
    APIKeyConfigCreateSerializer,
    APIKeyConfigSerializer,
    BookmarkSerializer,
    ConversationListSerializer,
    ConversationSerializer,
    ExportJobCreateSerializer,
    ExportJobSerializer,
    LoginSerializer,
    PaperChunkSerializer,
    PaperUploadSerializer,
    QueryEvaluationSerializer,
    QueryHistorySerializer,
    QueryRequestSerializer,
    RegisterSerializer,
    ResearchPaperSerializer,
    ResearchProjectCreateSerializer,
    ResearchProjectSerializer,
    SynthesisReportCreateSerializer,
    SynthesisReportSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


def _generate_token(user):
    payload = {
        "user_id": str(user.id),
        "username": user.username,
        "exp": datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        "iat": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


# ── Auth ────────────────────────────────────────
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = _generate_token(user)
        return Response(
            {"user": UserSerializer(user).data, "token": token},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token = _generate_token(user)
        return Response({"user": UserSerializer(user).data, "token": token})


class CurrentUserView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RefreshTokenView(APIView):
    def post(self, request):
        token = _generate_token(request.user)
        return Response({"token": token})


# ── Projects ────────────────────────────────────
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ResearchProjectSerializer
    filterset_fields = ["status", "is_public"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "updated_at", "name"]

    def get_queryset(self):
        user = self.request.user
        own = ResearchProject.objects.filter(owner=user)
        collab = ResearchProject.objects.filter(
            collaborators__user=user
        )
        return (own | collab).distinct().prefetch_related("collaborators")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ResearchProjectCreateSerializer
        return ResearchProjectSerializer


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResearchProjectSerializer

    def get_queryset(self):
        return ResearchProject.objects.filter(owner=self.request.user)


class ProjectCollaboratorView(APIView):
    def get(self, request, pk):
        collaborators = ProjectCollaborator.objects.filter(project_id=pk)
        from .serializers import ProjectCollaboratorSerializer

        return Response(ProjectCollaboratorSerializer(collaborators, many=True).data)

    def post(self, request, pk):
        project = ResearchProject.objects.get(id=pk, owner=request.user)
        user = User.objects.get(email=request.data.get("email"))
        collab, created = ProjectCollaborator.objects.get_or_create(
            project=project,
            user=user,
            defaults={
                "role": request.data.get("role", "viewer"),
                "invited_by": request.user,
            },
        )
        if not created:
            collab.role = request.data.get("role", collab.role)
            collab.save()
        from .serializers import ProjectCollaboratorSerializer

        return Response(ProjectCollaboratorSerializer(collab).data)


# ── Papers ──────────────────────────────────────
class PaperListView(generics.ListAPIView):
    serializer_class = ResearchPaperSerializer
    filterset_fields = ["project", "processing_status"]
    search_fields = ["title", "authors"]
    ordering_fields = ["created_at", "title"]

    def get_queryset(self):
        qs = ResearchPaper.objects.all()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class PaperUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = PaperUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["file"]
        project = ResearchProject.objects.get(
            id=serializer.validated_data["project_id"]
        )

        paper = ResearchPaper.objects.create(
            project=project,
            title=serializer.validated_data.get("title") or uploaded_file.name,
            file=uploaded_file,
            file_name=uploaded_file.name,
            file_size=uploaded_file.size,
        )

        return Response(
            ResearchPaperSerializer(paper).data,
            status=status.HTTP_201_CREATED,
        )


class PaperDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ResearchPaperSerializer
    queryset = ResearchPaper.objects.all()


class PaperChunksView(generics.ListAPIView):
    serializer_class = PaperChunkSerializer

    def get_queryset(self):
        return PaperChunk.objects.filter(paper_id=self.kwargs["pk"])


class PaperSummaryView(APIView):
    def post(self, request, pk):
        from ..agents import OrchestratorAgent

        orchestrator = OrchestratorAgent(user=request.user)
        result = orchestrator.execute(action="generate_summary", paper_id=str(pk))
        return Response(result)


class PaperCitationsView(APIView):
    def get(self, request, pk):
        from ..agents import OrchestratorAgent

        style = request.query_params.get("style", "apa")
        orchestrator = OrchestratorAgent(user=request.user)
        result = orchestrator.execute(
            action="extract_citations", paper_id=str(pk), format_style=style
        )
        return Response(result)


# ── Conversations ───────────────────────────────
class ConversationListCreateView(generics.ListCreateAPIView):
    filterset_fields = ["project"]
    ordering_fields = ["created_at", "updated_at"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ConversationListSerializer
        return ConversationSerializer

    def get_queryset(self):
        qs = Conversation.objects.filter(user=self.request.user)
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(
            user=self.request.user
        ).prefetch_related("messages")


# ── RAG Query ───────────────────────────────────
class QueryView(APIView):
    def post(self, request):
        serializer = QueryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data["question"]
        project_id = str(serializer.validated_data["project_id"])
        conversation_id = serializer.validated_data.get("conversation_id")
        run_evaluation = serializer.validated_data.get("run_evaluation", True)

        # Save user message if conversation
        if conversation_id:
            conv = Conversation.objects.get(id=conversation_id)
            Message.objects.create(
                conversation=conv,
                role="user",
                content=question,
            )
            # Auto-title conversation from first question
            if conv.message_count <= 1:
                conv.title = question[:100]
                conv.save(update_fields=["title"])

        from ..agents import OrchestratorAgent

        orchestrator = OrchestratorAgent(
            user=request.user,
            api_key=self._get_user_api_key(request.user),
        )
        result = orchestrator.execute(
            action="query",
            question=question,
            project_id=project_id,
            conversation_id=str(conversation_id) if conversation_id else None,
            run_evaluation=run_evaluation,
        )

        return Response(result)

    def _get_user_api_key(self, user):
        """Get user's configured API key, fallback to system key."""
        try:
            config = APIKeyConfig.objects.get(
                user=user, provider="openai", is_active=True
            )
            return config.api_key
        except APIKeyConfig.DoesNotExist:
            return settings.OPENAI_API_KEY


class QueryHistoryView(generics.ListAPIView):
    serializer_class = QueryHistorySerializer
    filterset_fields = ["project"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        return QueryHistory.objects.filter(
            user=self.request.user
        ).prefetch_related("evaluations")


class QueryEvaluateView(APIView):
    def post(self, request, pk):
        """Run evaluation on an existing query."""
        query = QueryHistory.objects.get(id=pk, user=request.user)

        from ..agents import OrchestratorAgent

        orchestrator = OrchestratorAgent(user=request.user)
        result = orchestrator.execute(
            action="evaluate",
            query_id=str(query.id),
            question=query.question,
            answer=query.answer,
            context=". ".join(query.context_chunks[:5]),
            eval_types=request.data.get(
                "eval_types",
                ["groundedness", "relevance", "coherence", "completeness", "faithfulness"],
            ),
        )
        return Response(result)


# ── Synthesis Reports ───────────────────────────
class SynthesisReportListView(generics.ListAPIView):
    serializer_class = SynthesisReportSerializer
    filterset_fields = ["project", "report_type", "status"]

    def get_queryset(self):
        return SynthesisReport.objects.filter(user=self.request.user)


class SynthesisReportGenerateView(APIView):
    def post(self, request):
        serializer = SynthesisReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from ..tasks import generate_synthesis_report_task

        task = generate_synthesis_report_task.delay(
            user_id=str(request.user.id),
            project_id=str(serializer.validated_data["project_id"]),
            report_type=serializer.validated_data["report_type"],
        )

        return Response(
            {"task_id": task.id, "status": "submitted"},
            status=status.HTTP_202_ACCEPTED,
        )


class SynthesisReportDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = SynthesisReportSerializer

    def get_queryset(self):
        return SynthesisReport.objects.filter(
            user=self.request.user
        ).prefetch_related("sections")


# ── Agent Monitoring ────────────────────────────
class AgentListView(APIView):
    def get(self, request):
        from ..agents import OrchestratorAgent

        orchestrator = OrchestratorAgent(user=request.user)
        result = orchestrator.execute(action="discover_agents")
        return Response(result)


class AgentLogListView(generics.ListAPIView):
    serializer_class = AgentLogSerializer
    filterset_fields = ["agent_name", "status"]
    ordering_fields = ["created_at", "duration_ms"]

    def get_queryset(self):
        qs = AgentLog.objects.all()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs[:100]


class AgentInteractionListView(generics.ListAPIView):
    serializer_class = AgentInteractionSerializer
    filterset_fields = ["source_agent", "target_agent", "protocol", "status"]

    def get_queryset(self):
        return AgentInteraction.objects.all()[:100]


# ── API Keys ────────────────────────────────────
class APIKeyListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return APIKeyConfigCreateSerializer
        return APIKeyConfigSerializer

    def get_queryset(self):
        return APIKeyConfig.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = APIKeyConfigSerializer

    def get_queryset(self):
        return APIKeyConfig.objects.filter(user=self.request.user)


# ── Exports ─────────────────────────────────────
class ExportListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return ExportJobCreateSerializer
        return ExportJobSerializer

    def get_queryset(self):
        return ExportJob.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        export = ExportJob.objects.create(
            user=self.request.user,
            **serializer.validated_data,
        )
        from ..tasks import process_export_task

        process_export_task.delay(str(export.id))


class ExportDetailView(generics.RetrieveAPIView):
    serializer_class = ExportJobSerializer

    def get_queryset(self):
        return ExportJob.objects.filter(user=self.request.user)


# ── Annotations & Bookmarks ────────────────────
class AnnotationListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnotationSerializer
    filterset_fields = ["paper"]

    def get_queryset(self):
        return Annotation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnnotationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnnotationSerializer

    def get_queryset(self):
        return Annotation.objects.filter(user=self.request.user)


class BookmarkListCreateView(generics.ListCreateAPIView):
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookmarkDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)


# ── Analytics Dashboard ─────────────────────────
class AnalyticsDashboardView(APIView):
    def get(self, request):
        user = request.user
        now = timezone.now()
        thirty_days_ago = now - datetime.timedelta(days=30)

        # Aggregate statistics
        total_projects = ResearchProject.objects.filter(owner=user).count()
        total_papers = ResearchPaper.objects.filter(project__owner=user).count()
        queries = QueryHistory.objects.filter(user=user)
        total_queries = queries.count()
        total_tokens = queries.aggregate(
            total=Sum("total_tokens")
        )["total"] or 0

        # Average evaluation scores
        evals = QueryEvaluation.objects.filter(query__user=user)
        avg_groundedness = (
            evals.filter(eval_type="groundedness").aggregate(avg=Avg("score"))["avg"]
            or 0
        )
        avg_relevance = (
            evals.filter(eval_type="relevance").aggregate(avg=Avg("score"))["avg"]
            or 0
        )

        # Queries by day (last 30 days)
        queries_by_day = list(
            queries.filter(created_at__gte=thirty_days_ago)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        # Top papers by query references
        top_papers = list(
            ResearchPaper.objects.filter(project__owner=user)
            .annotate(query_count=Count("project__query_history"))
            .order_by("-query_count")[:5]
            .values("id", "title", "query_count")
        )

        # Agent performance
        agent_perf = list(
            AgentLog.objects.filter(user=user)
            .values("agent_name")
            .annotate(
                total_calls=Count("id"),
                avg_duration=Avg("duration_ms"),
                total_tokens=Sum("tokens_used"),
            )
            .order_by("-total_calls")
        )

        return Response({
            "total_projects": total_projects,
            "total_papers": total_papers,
            "total_queries": total_queries,
            "total_tokens_used": total_tokens,
            "avg_groundedness_score": round(avg_groundedness, 2),
            "avg_relevance_score": round(avg_relevance, 2),
            "queries_by_day": queries_by_day,
            "top_papers": top_papers,
            "agent_performance": agent_perf,
        })


class UsageAnalyticsView(APIView):
    def get(self, request):
        user = request.user
        return Response({
            "tokens_used_this_month": user.tokens_used_this_month,
            "quota_total": user.usage_quota_tokens,
            "quota_remaining": user.quota_remaining,
            "percentage_used": round(
                (user.tokens_used_this_month / max(user.usage_quota_tokens, 1)) * 100,
                1,
            ),
        })


# ── Health Check ────────────────────────────────
@require_GET
def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "service": "AI Research Synthesis Assistant",
        "version": "1.0.0",
    })
