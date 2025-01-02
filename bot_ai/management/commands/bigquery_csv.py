from django.core.management import BaseCommand

from app.bot_ai.bigquery import GCPBigQuery
from app.bot_ai.tasks import tasks_in_vertex


class Command(BaseCommand):
    """
    ...
    """

    help = "Ejecuta el asistente para el manejo del bucket en Google Cloud Storage"

    def handle(self, *args, **options):
        """
        ...
        """

        gc_bigquery = GCPBigQuery()
        gc_bigquery.create_a_dataset("test_dataset")

        tasks_in_vertex("test_dataset", 1)
