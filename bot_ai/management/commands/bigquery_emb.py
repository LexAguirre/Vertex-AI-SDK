from django.core.management import BaseCommand

from app.bot_ai.bigquery import GCPBigQuery


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

        files = [
            "gs://dev_lumi_company_files/medias-lumi/companys/avatars/None/Collage.png",
            "gs://dev_lumi_company_files/medias-lumi/companys/avatars/None/Logo.jpg",
            "gs://dev_lumi_company_files/RamonAguirre_ID_1/temporary/contexto_personal.txt",
            "gs://demo-rag-lumi/CATLOGO_03_2024 - Blen.xlsx",
            "gs://prod_lumi_company_files/01_Blen/permanent/Cápsulas Mentex-C.pdf",
            "gs://prod_lumi_company_files/01_Blen/permanent/Aviso de privacidad.pdf",
            "gs://prod_lumi_company_files/01_Blen/permanent/Sistema de Comisiones.pdf",
            "gs://prod_lumi_company_files/01_Blen/permanent/Sobre Blen.pdf",
        ]

        dataset_name = "test_dataset"
        gc_bigquery.create_a_dataset(dataset_name)

        gc_bigquery.create_a_model_in_dataset(dataset_name)
        files_table_name = gc_bigquery.create_external_table(
            dataset_name,
            files,
            dataset_name,
        )
        embb_table_name = gc_bigquery.generate_embeddings(  # noqa: F841
            dataset_name,
            files_table_name,
            dataset_name,
        )
