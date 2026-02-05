"""URL configuration for AI Research Synthesis Assistant."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("research_assistant.api.urls")),
    path("mcp/", include("research_assistant.mcp.urls")),
    path("a2a/", include("research_assistant.a2a.urls")),
]
