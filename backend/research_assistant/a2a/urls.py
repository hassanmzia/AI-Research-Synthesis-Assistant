"""A2A (Agent-to-Agent) Protocol URL configuration.

Implements the A2A protocol for inter-agent communication and discovery.
"""
from django.urls import path

from . import views

app_name = "a2a"

urlpatterns = [
    # A2A Discovery
    path("", views.a2a_agent_card, name="agent-card"),
    path("agents/", views.a2a_list_agents, name="list-agents"),
    path("agents/<str:agent_name>/", views.a2a_agent_detail, name="agent-detail"),

    # A2A Task Management
    path("tasks/", views.a2a_create_task, name="create-task"),
    path("tasks/<str:task_id>/", views.a2a_get_task, name="get-task"),
    path("tasks/<str:task_id>/cancel/", views.a2a_cancel_task, name="cancel-task"),

    # A2A Messaging
    path("message/", views.a2a_send_message, name="send-message"),
]
