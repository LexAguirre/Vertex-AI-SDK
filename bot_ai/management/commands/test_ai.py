# Import necessary components from LangChain

from django.core.management import BaseCommand

# Import necessary components from LangChain
from app.bot_ai.bot_multi_model import VertexAImultimodel  # noqa: F401
from app.bot_ai.utils import generate_bot_response_class  # noqa: F401
from app.bot_ai.utils import generate_user_response_class  # noqa: F401
from app.bot_whatsapp.models import ConversationWhatsappModel  # noqa: F401
from app.bot_whatsapp.models import MessageWhatsappModel  # noqa: F401
from app.users.models import CompanyModel  # noqa: F401
from app.users.models import User  # noqa: F401
from app.users.tests.test_models import create_company  # noqa: F401
from app.users.tests.test_models import create_user  # noqa: F401


class Command(BaseCommand):
    help = "Ejecuta el asistente para el manejo del assistant"

    def add_arguments(self, parser):
        parser.add_argument("action", nargs="+")

    def handle(self, *args, **options):
        action = options["action"][0]  # noqa: F841
        """
        initial_state = {
            "input": "Your input here",
            "chat_history": [],
            "context": "",
            "answer": "",
        }

        # Create an instance of the workflow and run it
        ai_workflow = AIWorkflow()
        final_state = ai_workflow.run(initial_state)
        print(final_state)

        """
        """
        @pytest.mark.django_db
        def test_create_user(create_user):
            user = create_user
            assert user.email == "google@example.com"
            assert user.password == "SOmeNice!7jpw"
        user = create_user()
        company = create_company(user)
        print(company)"""
        # Llamar a la función de onboarding
        # start_onboarding()  # noqa: ERA001

        """
        vx_model = VertexAImultimodel()
        conversation = ConversationWhatsappModel.objects.get(id=action)

        history_messages = MessageWhatsappModel.objects.filter(
            conversation=conversation,
        )
        chat, _ = vx_model.start_chat()
        history = []

        if len(history) == 0:
            name = input("¿Cuál es tu nombre y apellido?: ")
            response, history = vx_model.onboarding_process(
                vx_model,
                onboarding_status="name",
                history=history,
                prompt=name,
            )

        else:
            chat, _ = vx_model.start_chat(history)
            list_position = 0
            # Si deseas ver los mensajes filtrados, puedes iterar sobre 'history_messages'
            for message_model in history_messages:
                if message_model.send_by == message_model.OPTION_SEND_BY_USER:
                    user_message = generate_user_response_class(message_model.text)
                    vx_model.insert_chat_history(chat, list_position, user_message)
                    list_position += 1
                if message_model.send_by == message_model.OPTION_SEND_BY_BOT:
                    bot_message = generate_bot_response_class(message_model.text)
                    vx_model.insert_chat_history(chat, list_position, bot_message)
                    list_position += 1

            print(chat.history)  # noqa: T201

        files = [
            "gs://prod_lumi_company_files/01_Blen/permanent/Cápsulas Fenix.pdf",
            "gs://prod_lumi_company_files/01_Blen/permanent/Cápsulas Flex-in.pdf",
            "gs://prod_lumi_company_files/01_Blen/permanent/Cápsulas Holo-Vis.pdf",
            "gs://prod_lumi_company_files/01_Blen/permanent/Cápsulas Juv-Nad.pdf",
            "gs://prod_lumi_company_files/01_Blen/permanent/Cápsulas Mentex-C.pdf",
            "gs://prod_lumi_company_files/01_Blen/permanent/Aviso de privacidad.pdf",
            "gs://prod_lumi_company_files/01_Blen/permanent/Sistema de Comisiones.pdf",
            "gs://prod_lumi_company_files/01_Blen/permanent/Sobre Blen.pdf",
        ]

        while True:
            prompt = input("prompt? ")
            response = vx_model.generate_message_with_documents(chat, prompt, files)

            print(response)  # noqa: T201
            history = chat.history

            chat, _ = vx_model.start_chat(history)
        """  # noqa: E501


MODEL_VERTEX = "gemini-1.5-pro-002"
