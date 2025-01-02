import logging
import re
import secrets
from datetime import date
from datetime import datetime
from datetime import timedelta
from pathlib import Path

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import ChatVertexAI
from pydantic import BaseModel
from pydantic import Field
from vertexai.generative_models import Part
from vertexai.generative_models._generative_models import Content

from app.bot_ai.bot_multi_model import VertexAImultimodel
from app.common.models import ErrorLogModel

vx_model = VertexAImultimodel()
logger = logging.getLogger(__name__)


def extract_text_after_folders(text):
    # Buscar el texto que sigue de "folders/"
    match = re.search(r"folders/(.*)", text)
    if match:
        return match.group(1)
    return None


def get_file_divition(file_path):
    """Obtiene el tamaño del archivo en bytes."""
    try:
        size = Path(file_path).stat().st_size
        max_file_size = 75000000

        if size % max_file_size != 0:
            return size // max_file_size + 1
        elif size < max_file_size:  # noqa: RET505
            return 1
        else:
            return int(size / max_file_size)

    except FileNotFoundError as e:
        ErrorLogModel.objects.create(
            app="bot_ai",
            function="get_file_divition",
            error=f"Error: {e}",
        )
        return None


def generate_user_response_class(prompt):
    return Content(
        role="user",
        parts=[
            Part.from_text(prompt),
        ],
    )


def generate_bot_response_class(response):
    return Content(
        role="model",
        parts=[
            Part.from_text(response),
        ],
    )


def onboarding_process_name(prompt):
    max_output_tokens = 100
    instruction = "get_name_instruction.txt"

    response = vx_model.generate_message_without_history_and_files(
        prompt.encode("utf-8", "replace").decode("utf-8"),
        instruction,
        max_output_tokens,
    )

    return structure_response(response)


correct_description = """
    Estamos evaluando nombres de personas en spanish.
    Si el nombre es correcto responde true, si no
    es correcto responde false, en formato booleano.
"""

respuesta_description = """
    Devuelme el nombre que se ha dado en formato string
    de manera correcta si se puede, sino la descripción
    porque no es correcto.
"""


class Information(BaseModel):
    correct: bool = Field(description=correct_description)
    respuesta: str = Field(description=respuesta_description)


def onboarding_process_name_v2(prompt):
    template = """
      dando el siguiente nombre dime si es correcto o no: {name}. {format_instructions}
    """
    output_parser = JsonOutputParser(pydantic_object=Information)
    template_prompt = PromptTemplate(
        input_variables=["name"],
        template=template,
        partial_variables={
            "format_instructions": output_parser.get_format_instructions(),
        },
    )

    llm = ChatVertexAI(
        model="gemini-1.5-pro-001",
        temperature=0,
        max_tokens=None,
        max_retries=6,
        stop=None,
    )
    chain = template_prompt | llm | output_parser
    return chain.invoke(input={"name": prompt})


def onboarding_process_date(prompt):
    max_output_tokens = 100
    instruction = "get_date_instruction.txt"

    response = vx_model.generate_message_without_history_and_files(
        prompt.encode("utf-8", "replace").decode("utf-8"),
        instruction,
        max_output_tokens,
    )

    return structure_response(response, "date")


class BirthdateInformation(BaseModel):
    complete: bool = Field(description="Indica si la fecha es válida o no")
    value: date | None = Field(
        description="Fecha de nacimiento en formato date de python",
    )


def onboarding_process_date_2(prompt):
    template = """
        dada la siguiente fecha en cualquier formato,
        diga si es correcto o no: {prompt}. {format_instructions}
    """
    output_parser = JsonOutputParser(pydantic_object=BirthdateInformation)
    template_prompt = PromptTemplate(
        input_variables=["prompt"],
        template=template,
        partial_variables={
            "format_instructions": output_parser.get_format_instructions(),
        },
    )

    llm = ChatVertexAI(
        model="gemini-1.5-pro-001",
        temperature=0,
        max_tokens=None,
        max_retries=6,
        stop=None,
    )
    chain = template_prompt | llm | output_parser
    return chain.invoke(input={"prompt": prompt})


def onboarding_process_city(prompt):
    max_output_tokens = 100
    instruction = "get_city_instruction.txt"

    response = vx_model.generate_message_without_history_and_files(
        prompt.encode("utf-8", "replace").decode("utf-8"),
        instruction,
        max_output_tokens,
    )

    return structure_response(response)


def onboarding_process_name_retry(prompt):
    max_output_tokens = 100
    instruction = "get_name_retry_instruction.txt"

    response = vx_model.generate_message_without_history_and_files(
        prompt.encode("utf-8", "replace").decode("utf-8"),
        instruction,
        max_output_tokens,
    )

    return structure_response(response)


def onboarding_process_name_confirmation(prompt):
    max_output_tokens = 100
    instruction = "get_name_check_instruction.txt"

    response = vx_model.generate_message_without_history_and_files(
        prompt.encode("utf-8", "replace").decode("utf-8"),
        instruction,
        max_output_tokens,
    )
    """
    if re.search(response.strip(), "True"):
        return True
    return False """

    return bool(re.search(response.strip(), "True"))


def structure_response(response, onboarding_status="NAT"):
    response = response.strip()
    condition, value = False, ""  # Default condition and value
    if bool(re.search(response, "False")):
        condition, value = False, ""
    elif onboarding_status != "date":
        condition, value = True, response

    if onboarding_status == "date":
        condition, value = date_processor(response)

    return {
        "complete": condition,
        "value": value,
    }


def date_processor(date):
    # Parse the input date
    date_f = datetime.strptime(date, "%d-%m-%Y")  # noqa: DTZ007

    # Define the limit for 18 years and 100 years ago
    limit_18_years = datetime.now() - timedelta(  # noqa: DTZ005
        days=365.25 * 18,
    )  # 6574 days ≈ 18 years
    limit_100_years = datetime.now() - timedelta(  # noqa: DTZ005
        days=365.25 * 100,
    )  # 100 years ago

    # Check if the date is older than 100 years
    if (date_f > limit_18_years) or (date_f < limit_100_years):
        condition = False
        age = round((datetime.now() - date_f).days / 365.25)  # noqa: DTZ005
        value = f"Age is not valid ({age})"  # Return a message with the invalid age
    else:
        # If the date is valid and older than 18 but less than 100 years
        condition = True
        value = date_f.strftime("%d/%m/%Y")  # Return the formatted date

    return condition, value


def get_random_name_quote():
    name_phrases = [
        "Por favor, indícame tu nombre completo.",
        "¿Me puedes proporcionar tu nombre completo?",
        "Necesito tu nombre completo para continuar. ¿Podrías escribirlo?",
        "¿Cuál es tu nombre completo?",
        "Para registrar tus datos correctamente, ¿me podrías dar tu nombre y apellidos?",  # noqa: E501
        "¿Me podrías compartir tu nombre completo?",
        "Por favor, escribe tu nombre completo.",
        "Para continuar, por favor proporciona tu nombre y apellido(s).",
        "Para ingresar, ¿puedes darme tu nombre completo?",
        "¿Cuál es tu nombre y tu(s) apellido(s)?",
    ]

    return secrets.choice(name_phrases)


def get_random_date_quote():
    date_phrases = [
        "¿Cuál es tu fecha de nacimiento?"
        "Por favor, indícame tu fecha de nacimiento.",
        "¿Me podrías decir tu fecha de nacimiento?",
        "¿En qué fecha naciste?",
        "Para continuar, necesito saber tu fecha de nacimiento. ¿Podrías escribirla, por favor?",  # noqa: E501
        "¿Me podrías compartir tu fecha de nacimiento?",
        "Escribe tu día, mes y año de nacimiento",
        "Por favor, escribe tu fecha de nacimiento (día, mes y año).",
        "¿Me puedes proporcionar tu fecha de nacimiento, por favor?",
        "¿Cuándo naciste? Escribe la fecha",
        "Para registrar tus datos correctamente, ¿puedes indicarme tu fecha de nacimiento?",  # noqa: E501
    ]

    return secrets.choice(date_phrases)


def get_random_city_quote():
    city_phrases = [
        "¿En qué ciudad vives?",
        "Por favor, indícame la ciudad donde resides.",
        "¿Me podrías decir en qué ciudad vives actualmente?",
        "¿Cuál es tu ciudad de residencia?",
        "Por favor, escribe el nombre de la ciudad donde vives.",
        "¿En qué ciudad te encuentras viviendo en este momento?",
        "Para continuar, necesito saber en qué ciudad resides. ¿Podrías escribirla, por favor?",  # noqa: E501
        "¿Cuál es el nombre de la ciudad en la que vives?",
        "¿Puedes proporcionarme el nombre de tu ciudad de residencia?",
        "¿En qué ciudad estás viviendo actualmente?",
    ]

    return secrets.choice(city_phrases)


def get_random_name_retry_quote():
    retry_phrases = [
        "¿Podrías decirme nuevamente tu nombre completo?",
        "¿Me puedes recordar tu nombre completo, por favor?",
        "¿Podrías escribirme tu nombre completo otra vez?",
        "¿Te importaría volver a darme tu nombre completo?",
        "¿Me repites tu nombre completo, por favor?",
        "¿Podrías proporcionarme de nuevo tu nombre completo?",
        "¿Me puedes compartir otra vez tu nombre completo?",
        "¿Podrías indicarme nuevamente tu nombre completo?",
        "¿Me puedes confirmar tu nombre completo otra vez?",
        "¿Podrías recordarme tu nombre completo, por favor?",
    ]

    return secrets.choice(retry_phrases)


def get_random_name_confirmation_quote():
    validate_name_phrases = [
        "¿El nombre está bien escrito?",
        "¿Es este el nombre correcto?",
        "¿Este es el nombre adecuado?",
        "¿El nombre es correcto?",
        "¿Está bien este nombre?",
        "¿Es este el nombre correcto?",
        "¿Está bien escrito tu nombre?",
        "¿Este nombre es el apropiado?",
        "¿Este es el nombre correcto?",
        "¿Este nombre está bien?",
    ]

    return secrets.choice(validate_name_phrases)


class BotOnboardingV1:
    """Encapsulate all the functions for the onboarding process"""

    @staticmethod
    def _convert_output(input_data):
        """Convert the input data to the expected format"""
        return input_data["complete"], input_data["value"]

    @classmethod
    def process_name(cls, name) -> tuple[bool, str]:
        """Process the name"""
        process = onboarding_process_name_v2(name)
        return process["correct"], process["respuesta"]

    @classmethod
    def process_birthdate(cls, birthdate) -> tuple[bool, str]:
        """Process the birthdate"""
        """
        process = onboarding_process_date(birthdate)
        return cls._convert_output(process)
        """
        process = onboarding_process_date_2(birthdate)
        return process["complete"], process["value"]

    @classmethod
    def get_name_quote(cls) -> str:
        """Get a random quote for the name"""
        return get_random_name_quote()

    @classmethod
    def get_birthdate_quote(cls) -> str:
        """Get a random quote for the birthdate"""
        return get_random_date_quote()

    @classmethod
    def get_city_quote(cls) -> str:
        """Get a random quote for the city"""
        return get_random_city_quote()
