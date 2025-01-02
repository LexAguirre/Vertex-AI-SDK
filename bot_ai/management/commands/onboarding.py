# Import necessary components from LangChain

from django.core.management import BaseCommand

from app.bot_ai.utils import get_random_city_quote
from app.bot_ai.utils import get_random_date_quote
from app.bot_ai.utils import get_random_name_confirmation_quote
from app.bot_ai.utils import get_random_name_quote
from app.bot_ai.utils import get_random_name_retry_quote
from app.bot_ai.utils import onboarding_process_city
from app.bot_ai.utils import onboarding_process_date
from app.bot_ai.utils import onboarding_process_name
from app.bot_ai.utils import onboarding_process_name_confirmation
from app.bot_ai.utils import onboarding_process_name_retry


class Command(BaseCommand):
    """
    ...
    """

    help = "Ejecuta el asistente para el manejo del bucket en Google Cloud Storage"

    def handle(self, *args, **options):
        print(get_random_name_quote())  # noqa: T201
        name = onboarding_process_name("mi nombre es Ramon Aguirre")
        print(name)  # noqa: T201
        retry_phrase = get_random_name_confirmation_quote()
        response = input(f"{retry_phrase}: ")
        status = onboarding_process_name_confirmation(response)
        print(status)  # noqa: T201
        while status is False:
            print(get_random_name_retry_quote())  # noqa: T201
            name = onboarding_process_name_retry("mi nombre es Ramon Alejandro Aguirre")
            print(name)  # noqa: T201
            retry_phrase = get_random_name_confirmation_quote()
            response = input(f"{retry_phrase}: ")
            status = onboarding_process_name_confirmation(response)
            print(status)  # noqa: T201

        print(get_random_date_quote())  # noqa: T201
        date = onboarding_process_date(
            "mi fecha de nacimiento es el 29 de enero del 2002",
        )
        print(date)  # noqa: T201
        print(get_random_city_quote())  # noqa: T201
        city = onboarding_process_city(
            "la ciudad donde estoy es tecoman aunque naci en Glendale",
        )
        print(city)  # noqa: T201
