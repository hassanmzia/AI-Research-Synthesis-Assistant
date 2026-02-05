"""Management command to set up initial data."""
from django.core.management.base import BaseCommand

from research_assistant.models import User


class Command(BaseCommand):
    help = "Set up initial data for the application"

    def handle(self, *args, **options):
        # Create superuser if not exists
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@arsa.local",
                password="admin123",
                first_name="Admin",
                last_name="User",
                institution="AI Research Synthesis Assistant",
            )
            self.stdout.write(self.style.SUCCESS("Created admin user (admin/admin123)"))
        else:
            self.stdout.write("Admin user already exists")

        # Create demo user
        if not User.objects.filter(username="researcher").exists():
            User.objects.create_user(
                username="researcher",
                email="researcher@arsa.local",
                password="research123",
                first_name="Demo",
                last_name="Researcher",
                institution="Johns Hopkins University",
            )
            self.stdout.write(
                self.style.SUCCESS("Created demo user (researcher/research123)")
            )
        else:
            self.stdout.write("Demo user already exists")

        self.stdout.write(self.style.SUCCESS("Initial data setup complete!"))
