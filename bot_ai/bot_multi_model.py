import logging
import os

import vertexai
from django.conf import settings

# from google.auth2 import service_account  # noqa: ERA001
from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import Part
from vertexai.preview import generative_models
from vertexai.preview.vision_models import Image
from vertexai.preview.vision_models import ImageTextModel

from app.bot_whatsapp.utils import render_message_txt

logger = logging.getLogger(__name__)


class VertexAImultimodel:
    """
    A class to interact with Vertex AI's Generative Models for various
    tasks such as chat, content generation, etc.

    Attributes:
        project_id (str): The project ID for Vertex AI.
        location (str): The location of the Vertex AI resources.
        model_id (str): The ID of the generative model to use.
        document_uri (str): The URI of the document to use in generation tasks.
        prompt (str): The prompt to use for content generation.
        generation_config (dict): Configuration settings for content generation.
        safety_settings (dict): Safety settings to block harmful content.

    Methods:
        read_instructions_from_file(file_name):
            Reads instructions from a specified file.
        start_chat(model_name):
            Starts a chat session with the specified model name.
        generate_message(chat, message_text):
            Generates a message in a chat session.
        generate_message_with_documents(chat, message_text, document_list):
            Generates a message in a chat session with documents.
        use_txt_in_bucket(uri):
            Uses a text file from a specified URI.
        delete_chat_history(chat):
            Deletes the chat history.
        insert_chat_history(chat, posicion, message):
            Inserts a message at a specified position in the chat history.
        generate_content():
            Generates content using the specified document and prompt.
    """

    def __init__(self, model_name: str | None = None):
        self.project_id = PROJECT_ID
        self.location = LOCATION
        self.model_name = model_name if model_name else GEMINI_MODEL_ID_1_5
        self.max_output_tokens = 8192
        self.temperature = 1
        self.top_p = 0.95

        # Configuration settings
        self.generation_config = {
            "max_output_tokens": self.max_output_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }

        self.safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,  # noqa: E501
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,  # noqa: E501
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,  # noqa: E501
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,  # noqa: E501
        }

    def read_instructions_from_file(self, file_name="instructions.txt"):
        """
        Reads instructions from a specified file.

        Args:
            file_name (str): The name of the file containing the instructions.

        Returns:
            str: The content of the file.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))  # noqa: PTH120, PTH100
        file_path = os.path.join(current_dir, file_name)  # noqa: PTH118

        with open(file_path, encoding="utf-8") as file:  # noqa: PTH123
            return file.read()

    def file_type(self, file):  # noqa: PLR0911
        if file.endswith(".pdf"):
            return "application/pdf"
        elif file.endswith(".txt"):  # noqa: RET505
            return "text/plain"
        elif file.endswith((".jpg", ".jpeg")):
            return "image/jpeg"
        elif file.endswith(".png"):
            return "image/png"
        elif file.endswith(".gif"):
            return "image/gif"
        elif file.endswith(".mp4"):
            return "video/mp4"
        elif file.endswith(".mp3"):
            return "audio/mpeg"
        return None

    def structure_files_url(self, files_url):
        structured_files_url = []

        for file in files_url:
            file_type_result = self.file_type(file)
            if file_type_result is None:
                structured_files_url.append(file)
            else:
                structured_files_url.append(
                    Part.from_uri(
                        mime_type=file_type_result,
                        uri=file,
                    ),
                )

        return structured_files_url

    def start_chat(
        self,
        history: list | None = None,
        instructions=None,
        max_output_tokens=8192,
    ):
        """
        Starts a chat session with the specified model name.

        Args:
            model_name (str): The name of the model to use for the chat session.

        Returns:
            tuple: The chat session and the model.
        """
        if instructions is None:
            instructions = render_message_txt("instruccion.txt")

        if max_output_tokens is None:
            max_output_tokens = self.max_output_tokens

        model = GenerativeModel(
            self.model_name,
            system_instruction=instructions,
            generation_config={
                "max_output_tokens": self.max_output_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
            },
        )
        chat = model.start_chat(history=history) if history else model.start_chat()

        return chat, self.model_name

    def generate_message(self, chat, message_text):
        """
        Generates a message in a chat session.

        Args:
            chat (object): The chat session.
            message_text (str): The message text to send.

        Returns:
            str: The generated message text.
        """
        message = chat.send_message(
            [message_text],
            safety_settings=self.safety_settings,
        )
        return message.text

    def generate_message_information(self, chat, message_text):
        """
        Generates a message in a chat session.

        Args:
            chat (object): The chat session.
            message_text (str): The message text to send.

        Returns:
            str: The generated message text.
        """
        generated_content = chat.send_message(
            [message_text],
            safety_settings=self.safety_settings,
        )
        return generated_content.text

    def generate_message_with_documents(self, chat, message_text, document_list):
        """
        Generates a message in a chat session with documents.

        Args:
            chat (object): The chat session.
            message_text (str): The message text to send.
            document_list (list): The list of documents to include.

        Returns:
            str: The generated message text.
        """
        documents_and_message = [*document_list, message_text]
        message = chat.send_message(
            documents_and_message,
            safety_settings=self.safety_settings,
        )
        return message.text

    def use_txt_in_bucket(self, uri):
        """
        Uses a text file from a specified URI.

        Args:
            uri (str): The URI of the text file.

        Returns:
            Part: The part object created from the URI.
        """
        return Part.from_uri(
            mime_type="text/plain",
            uri=uri,
        )

    def generate_message_with_video(self, chat, video_uri):
        """
        Generates a message in a chat session with a video.

        Args:
            chat (object): The chat session.
            message_text (str): The message text to send.
            video_uri (str): The URI of the video file.

        Returns:
            str: The generated message text.
        """
        prompt = (
            "Provide a description of the video. And what kind of product do you see"
        )

        video_part = self.use_video_in_bucket(video_uri)
        message = chat.send_message(
            [prompt, video_part],
            safety_settings=self.safety_settings,
            stream=True,
        )
        return message.text

    def use_video_in_bucket(self, uri):
        """
        Uses a video file from a specified URI.

        Args:
            uri (str): The URI of the video file.

        Returns:
            Part: The part object created from the URI.
        """
        return Part.from_uri(
            mime_type="video/mp4",
            uri=uri,
        )

    def delete_chat_history(self, chat):
        """
        Deletes the chat history.

        Args:
            chat (object): The chat session.
        """
        chat.history.clear()

    def insert_chat_history(self, chat, posicion, message):
        """
        Inserts a message at a specified position in the chat history.

        Args:
            chat (object): The chat session.
            posicion (int): The position to insert the message.
            message (str): The message to insert.
        """
        chat.history.insert(posicion, message)

    def generate_message_without_history(self, message_text, document_list: list[str]):
        """
        Generates a message in a chat session with documents.

        Args:
            message_text (str): The message text to send.
            document_list (list): The list of documents to include.

        Returns:
            str: The generated message text.
        """

        if not message_text:
            error = "message_text must not be empty."
            raise ValueError(error)

        instructions = self.read_instructions_from_file("lumi_instructions.txt")

        # Crear lista de archivos
        files = []
        for doc in document_list:
            if doc:  # Verificar que el documento no esté vacío
                document = Part.from_uri(
                    mime_type="text/plain",
                    uri=doc,
                )
                files.append(document)

        # Asegurarse de que la lista de archivos y el texto del mensaje no estén vacíos
        if not files:
            err = "document_list must contain at least one valid document URI."
            raise ValueError(err)

        # Crear el modelo generativo
        model = GenerativeModel(
            self.model_name,
            system_instruction=[instructions],
        )

        responses = model.generate_content(
            [*files, message_text],
            safety_settings=self.safety_settings,
        )

        response_text = ""
        # Check if 'responses' is a single instance or a list
        if isinstance(responses, list):
            # If it's a single object, append the text
            for response in responses:
                response_text += response.text
        else:
            # If it's a list, iterate over the elements
            response_text += responses.text  # type: ignore  # noqa: PGH003
        # Generar el contenido

        return response_text

    def generate_message_without_history_and_files(
        self,
        prompt,
        instruction=None,
        max_output_tokens=None,
    ):
        """
        Generates a response from a generative AI model without considering history or external files.

        Args:
            prompt (str): The main input message or query for the AI model.
            instruction (str, optional): A path to a custom instruction file or raw instructions.
                If not provided, it defaults to instructions loaded from "instruccion.txt".
            max_output_tokens (int, optional): The maximum number of tokens the response can have.
                Defaults to the instance's `max_output_tokens` attribute.

        Returns:
            str: The generated response text.

        Process:
            1. Loads the default or custom instructions using `render_message_txt`.
            2. Configures the generative model with the given instructions and settings.
            3. Generates content based on the provided prompt.
            4. Returns the response text.

        Variables:
            instruction (str): The processed instruction text.
            max_output_tokens (int): The limit for response token length.
            model (GenerativeModel): An instance of the generative AI model initialized with the system instructions.
            response (object): The model's response object containing the generated text.

        Raises:
            Exception: If the generative model fails or if the required components are not properly configured.
        """  # noqa: E501
        if instruction is None:
            instruction = render_message_txt("instruccion.txt")
        else:
            instruction = render_message_txt(instruction)

        if max_output_tokens is None:
            max_output_tokens = self.max_output_tokens

        model = GenerativeModel(
            self.model_name,
            system_instruction=[instruction],
        )

        response = model.generate_content(
            [f"""{prompt}"""],
            generation_config={
                "max_output_tokens": self.max_output_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
            },
            safety_settings=self.safety_settings,
        )

        return response.text


DIR_CREDENTIALS = settings.BASE_DIR / "clave.json"
CREDENTIALS = service_account.Credentials.from_service_account_file(DIR_CREDENTIALS)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = "us-central1"


GEMINI_MODEL_ID_1_5 = "gemini-1.5-flash-001"
MODEL_META = ' "gemini-1.5-pro-001"'
MODEL_VERTEX = "gemini-1.5-pro-001"
# vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=CREDENTIALS)  # noqa: ERA001,E501
vertexai.init(project=PROJECT_ID, location=LOCATION)


class VertexBot:
    """
    A class to interact with Vertex AI's Generative Models for chat generation.

    Attributes:
        model (GenerativeModel): The generative model to use for interactions.

    Methods:
        generate_response(prompt):
            Generates a response for a given prompt.
    """

    def __init__(self, model_name=GEMINI_MODEL_ID_1_5):
        self.model = GenerativeModel(model_name=model_name)

    def generate_response(self, prompt):
        """
        Generates a response for a given prompt.

        Args:
            prompt (str): The prompt to generate a response for.

        Returns:
            str: The generated response.
        """
        response = self.model.generate_content(prompt)
        return response.text  # type: ignore  # noqa: PGH003


def transcribe_chirp_auto_detect_language(
    audio_file: str,
    project_id: str = PROJECT_ID,  # type: ignore  # noqa: PGH003
    region: str = "us-central1",
) -> str:
    """Transcribe an audio file and auto-detect spoken language using Chirp.

    Please see https://cloud.google.com/speech-to-text/v2/docs/encoding for more
    information on which audio encodings are supported.
    """
    # Instantiates a client
    client = SpeechClient(
        client_options=ClientOptions(
            api_endpoint=f"{region}-speech.googleapis.com",
        ),
        credentials=CREDENTIALS,
    )

    # Reads a file as bytes
    with open(audio_file, "rb") as f:  # noqa: PTH123
        content = f.read()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["auto"],  # Set language code to auto to detect language.
        model="chirp",
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{project_id}/locations/{region}/recognizers/_",
        config=config,
        content=content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)
    all_transcripts = ""

    for result in response.results:
        logger.info(f"Transcript: {result.alternatives[0].transcript}")  # noqa: G004
        logger.info(f"Detected Language: {result.language_code}")  # noqa: G004
        all_transcripts += result.alternatives[0].transcript

    return all_transcripts


def get_short_form_image_captions(
    input_file: str,
    project_id: str = PROJECT_ID,  # type: ignore  # noqa: PGH003
    location: str = "us-central1",
) -> list:
    """Get short-form captions for a local image.
    Args:
      project_id: Google Cloud project ID, used to initialize Vertex AI.
      location: Google Cloud region, used to initialize Vertex AI.
      input_file: Local path to the input image file."""

    vertexai.init(project=project_id, location=location, credentials=CREDENTIALS)

    model = ImageTextModel.from_pretrained("imagetext@001")
    source_img = Image.load_from_file(location=input_file)

    return model.get_captions(
        image=source_img,
        # Optional parameters
        language="en",
        number_of_results=1,
    )
