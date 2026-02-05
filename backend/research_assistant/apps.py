from django.apps import AppConfig


class ResearchAssistantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "research_assistant"
    verbose_name = "AI Research Synthesis Assistant"

    def ready(self):
        import research_assistant.signals  # noqa: F401
