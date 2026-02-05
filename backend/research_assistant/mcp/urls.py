"""MCP (Model Context Protocol) URL configuration.

Exposes agent capabilities as MCP-compatible tool endpoints.
"""
from django.urls import path

from . import views

app_name = "mcp"

urlpatterns = [
    # MCP Discovery
    path("", views.mcp_manifest, name="manifest"),
    path("tools/", views.mcp_list_tools, name="list-tools"),
    path("tools/<str:tool_name>/execute/", views.mcp_execute_tool, name="execute-tool"),
    path("resources/", views.mcp_list_resources, name="list-resources"),
    path("resources/<str:resource_id>/", views.mcp_get_resource, name="get-resource"),
]
