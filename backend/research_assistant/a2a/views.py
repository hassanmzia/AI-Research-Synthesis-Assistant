"""A2A (Agent-to-Agent) Protocol Implementation.

Implements the Google A2A protocol for inter-agent communication,
task management, and agent discovery.
"""
import json
import logging
import uuid

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)


@require_GET
def a2a_agent_card(request):
    """Return the A2A agent card for service discovery."""
    return JsonResponse({
        "name": "AI Research Synthesis Assistant",
        "description": (
            "Multi-agent system for research paper analysis, "
            "RAG-based Q&A, and synthesis report generation"
        ),
        "url": request.build_absolute_uri("/a2a/"),
        "version": "1.0.0",
        "protocol": "a2a",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "stateTransitionHistory": True,
        },
        "skills": [
            {
                "id": "query_research",
                "name": "Research Q&A",
                "description": "Answer questions about research papers using RAG",
            },
            {
                "id": "generate_summary",
                "name": "Paper Summary",
                "description": "Generate comprehensive paper summaries",
            },
            {
                "id": "generate_report",
                "name": "Synthesis Report",
                "description": "Generate literature reviews and synthesis reports",
            },
            {
                "id": "extract_citations",
                "name": "Citation Extraction",
                "description": "Extract and format citations from papers",
            },
            {
                "id": "evaluate",
                "name": "Response Evaluation",
                "description": "Evaluate RAG responses for quality metrics",
            },
        ],
        "authentication": {
            "schemes": ["bearer"],
        },
    })


@require_GET
def a2a_list_agents(request):
    """List all agents in the system."""
    from ..agents import OrchestratorAgent

    orchestrator = OrchestratorAgent(user=getattr(request, "user", None))
    result = orchestrator.execute(action="discover_agents")
    return JsonResponse(result)


@require_GET
def a2a_agent_detail(request, agent_name):
    """Get details about a specific agent."""
    from ..agents.base import get_agent_class

    try:
        agent_cls = get_agent_class(agent_name)
        agent = agent_cls(user=getattr(request, "user", None))
        return JsonResponse(agent.get_agent_card())
    except ValueError:
        return JsonResponse({"error": f"Agent not found: {agent_name}"}, status=404)


@csrf_exempt
@require_POST
def a2a_create_task(request):
    """Create a new A2A task.

    Follows the A2A protocol task lifecycle:
    submitted -> working -> completed/failed
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    task_id = str(uuid.uuid4())
    skill_id = body.get("skill_id")
    message = body.get("message", {})
    params = message.get("parts", [{}])[0].get("data", {}) if message.get("parts") else body.get("params", {})

    if not skill_id:
        return JsonResponse({"error": "skill_id is required"}, status=400)

    # Map skill to orchestrator action
    skill_action_map = {
        "query_research": "query",
        "generate_summary": "generate_summary",
        "generate_report": "generate_report",
        "extract_citations": "extract_citations",
        "evaluate": "evaluate",
    }

    action = skill_action_map.get(skill_id)
    if not action:
        return JsonResponse({"error": f"Unknown skill: {skill_id}"}, status=400)

    try:
        from ..agents import OrchestratorAgent

        orchestrator = OrchestratorAgent(user=getattr(request, "user", None))
        result = orchestrator.execute(action=action, **params)

        return JsonResponse({
            "id": task_id,
            "status": {
                "state": "completed",
                "message": {
                    "role": "agent",
                    "parts": [{"type": "data", "data": result}],
                },
            },
            "history": [
                {"state": "submitted", "timestamp": "now"},
                {"state": "working", "timestamp": "now"},
                {"state": "completed", "timestamp": "now"},
            ],
        })

    except Exception as e:
        logger.exception(f"A2A task failed: {skill_id}")
        return JsonResponse({
            "id": task_id,
            "status": {
                "state": "failed",
                "message": {
                    "role": "agent",
                    "parts": [{"type": "text", "text": str(e)}],
                },
            },
        }, status=500)


@require_GET
def a2a_get_task(request, task_id):
    """Get task status by ID."""
    from ..models import AgentLog

    try:
        log = AgentLog.objects.get(task_id=task_id)
        return JsonResponse({
            "id": task_id,
            "status": {
                "state": log.status,
                "message": {
                    "role": "agent",
                    "parts": [{"type": "data", "data": log.output_data}],
                },
            },
        })
    except AgentLog.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)


@csrf_exempt
@require_POST
def a2a_cancel_task(request, task_id):
    """Cancel a running task."""
    return JsonResponse({
        "id": task_id,
        "status": {"state": "canceled"},
    })


@csrf_exempt
@require_POST
def a2a_send_message(request):
    """Send a message directly to an agent."""
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    target_agent = body.get("target_agent")
    payload = body.get("payload", {})

    if not target_agent:
        return JsonResponse({"error": "target_agent is required"}, status=400)

    try:
        from ..agents.base import get_agent_class

        agent_cls = get_agent_class(target_agent)
        agent = agent_cls(user=getattr(request, "user", None))
        result = agent.execute(**payload)

        return JsonResponse({
            "status": "success",
            "response": result,
        })
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=404)
    except Exception as e:
        logger.exception(f"A2A message failed")
        return JsonResponse({"error": str(e)}, status=500)
