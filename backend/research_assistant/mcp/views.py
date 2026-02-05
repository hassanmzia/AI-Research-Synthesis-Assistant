"""MCP (Model Context Protocol) Server Implementation.

Exposes the multi-agent system capabilities as MCP tools that can be
consumed by external AI clients (e.g., Claude, ChatGPT plugins).
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)

# MCP Tool Definitions
MCP_TOOLS = {
    "query_research": {
        "name": "query_research",
        "description": "Ask a question about research papers in a project using RAG",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The research question to answer",
                },
                "project_id": {
                    "type": "string",
                    "description": "UUID of the research project",
                },
            },
            "required": ["question", "project_id"],
        },
    },
    "summarize_paper": {
        "name": "summarize_paper",
        "description": "Generate a comprehensive summary of a research paper",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "UUID of the research paper",
                },
            },
            "required": ["paper_id"],
        },
    },
    "generate_report": {
        "name": "generate_report",
        "description": "Generate a synthesis report (literature review, comparative analysis, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "UUID of the research project",
                },
                "report_type": {
                    "type": "string",
                    "enum": [
                        "literature_review",
                        "comparative_analysis",
                        "research_gap",
                        "trend_analysis",
                        "executive_summary",
                    ],
                    "description": "Type of synthesis report to generate",
                },
            },
            "required": ["project_id", "report_type"],
        },
    },
    "extract_citations": {
        "name": "extract_citations",
        "description": "Extract and format citations from a research paper",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "UUID of the research paper",
                },
                "format_style": {
                    "type": "string",
                    "enum": ["apa", "mla", "bibtex"],
                    "description": "Citation format style",
                    "default": "apa",
                },
            },
            "required": ["paper_id"],
        },
    },
    "evaluate_response": {
        "name": "evaluate_response",
        "description": "Evaluate a RAG response for groundedness, relevance, and other quality metrics",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "answer": {"type": "string"},
                "context": {"type": "string"},
                "eval_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Types of evaluation to run",
                    "default": ["groundedness", "relevance"],
                },
            },
            "required": ["question", "answer", "context"],
        },
    },
    "list_papers": {
        "name": "list_papers",
        "description": "List all research papers in a project",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "UUID of the research project",
                },
            },
            "required": ["project_id"],
        },
    },
    "discover_agents": {
        "name": "discover_agents",
        "description": "Discover all available AI agents and their capabilities",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
}


@require_GET
def mcp_manifest(request):
    """Return the MCP server manifest."""
    return JsonResponse({
        "name": "AI Research Synthesis Assistant",
        "version": "1.0.0",
        "description": (
            "Multi-agent AI system for research paper analysis, "
            "RAG-based Q&A, synthesis reports, and evaluation"
        ),
        "protocol": "mcp",
        "capabilities": {
            "tools": True,
            "resources": True,
        },
    })


@require_GET
def mcp_list_tools(request):
    """List all available MCP tools."""
    return JsonResponse({
        "tools": list(MCP_TOOLS.values()),
    })


@csrf_exempt
@require_POST
def mcp_execute_tool(request, tool_name):
    """Execute an MCP tool."""
    if tool_name not in MCP_TOOLS:
        return JsonResponse(
            {"error": f"Unknown tool: {tool_name}"}, status=404
        )

    try:
        body = json.loads(request.body)
        arguments = body.get("arguments", {})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    try:
        from ..agents import OrchestratorAgent

        # Map MCP tool to orchestrator action
        action_map = {
            "query_research": "query",
            "summarize_paper": "generate_summary",
            "generate_report": "generate_report",
            "extract_citations": "extract_citations",
            "evaluate_response": "evaluate",
            "list_papers": "list_papers",
            "discover_agents": "discover_agents",
        }

        action = action_map.get(tool_name)
        if not action:
            return JsonResponse(
                {"error": f"No action mapped for tool: {tool_name}"}, status=400
            )

        if action == "list_papers":
            from ..models import ResearchPaper

            papers = ResearchPaper.objects.filter(
                project_id=arguments["project_id"]
            ).values("id", "title", "authors", "processing_status", "created_at")
            return JsonResponse({
                "content": [
                    {"type": "text", "text": json.dumps(list(papers), default=str)}
                ]
            })

        orchestrator = OrchestratorAgent(user=getattr(request, "user", None))
        result = orchestrator.execute(action=action, **arguments)

        return JsonResponse({
            "content": [
                {"type": "text", "text": json.dumps(result, default=str)}
            ]
        })

    except Exception as e:
        logger.exception(f"MCP tool execution failed: {tool_name}")
        return JsonResponse({
            "error": str(e),
            "isError": True,
        }, status=500)


@require_GET
def mcp_list_resources(request):
    """List available MCP resources."""
    from ..models import ResearchProject

    projects = ResearchProject.objects.all()[:50]
    resources = []
    for p in projects:
        resources.append({
            "uri": f"research://projects/{p.id}",
            "name": p.name,
            "description": p.description,
            "mimeType": "application/json",
        })

    return JsonResponse({"resources": resources})


@require_GET
def mcp_get_resource(request, resource_id):
    """Get a specific MCP resource."""
    from ..models import ResearchPaper, ResearchProject

    try:
        project = ResearchProject.objects.get(id=resource_id)
        papers = ResearchPaper.objects.filter(project=project).values(
            "id", "title", "authors", "abstract", "processing_status"
        )
        return JsonResponse({
            "contents": [{
                "uri": f"research://projects/{project.id}",
                "mimeType": "application/json",
                "text": json.dumps({
                    "project": {
                        "id": str(project.id),
                        "name": project.name,
                        "description": project.description,
                        "paper_count": project.paper_count,
                    },
                    "papers": list(papers),
                }, default=str),
            }],
        })
    except ResearchProject.DoesNotExist:
        return JsonResponse({"error": "Resource not found"}, status=404)
