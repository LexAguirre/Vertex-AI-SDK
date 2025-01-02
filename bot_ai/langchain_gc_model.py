import logging
import os
from collections.abc import Sequence
from typing import Annotated

import vertexai
from django.conf import settings
from google.oauth2 import service_account
from langchain_core.messages import AIMessage
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.bot_whatsapp.utils import render_message_txt

logger = logging.getLogger(__name__)

# Define a dict representing the state of the application.
class State(TypedDict):
    input: str
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    context: str
    answer: str


class AIWorkflow:
    def __init__(self):
        # Initialize the StateGraph with the defined state schema
        self.workflow = StateGraph(state_schema=State)
        self.memory = MemorySaver()  # Initialize memory for state saving
        self.workflow.add_edge(START, "model")  # Define the edges
        self.workflow.add_node("model", self.call_model)  # Add the model node

        # Compile the graph with the checkpointer object
        self.app = self.workflow.compile(checkpointer=self.memory)

        # Initialize the LLM model
        self.llm = ChatVertexAI(
            model=MODEL_VERTEX,
        )  # Replace MODEL_VERTEX with your model identifier

    def model_message(self, prompt, gcb_file_path=None):
        text_message = {
            "type": "text",
            "text": prompt,
        }

        if gcb_file_path is not None:
            image_message = {
                "type": "image_url",
                "image_url": {"url": gcb_file_path},
            }

            return HumanMessage(content=[text_message, image_message])

        return HumanMessage(content=[text_message])

    def call_model(self, state: State, instructions=None):
        # Prepare input for model consumption
        message = "dummy text"

        # Invoke a model response
        output = self.llm.invoke([message])

        if instructions is None:
            instructions = render_message_txt("instruccion.txt")

        # Simulate model invocation and return updated state
        return {
            "chat_history": [
                HumanMessage(state["input"]),
                AIMessage(output.content),
            ],
            "context": instructions,  # Adjust context as necessary
            "answer": output.content,
        }

    def run(self, initial_state: State):
        # Define a configuration for the invocation
        config = {
            "configurable": {
                "thread_id": "thre_4168",  # Replace with a unique identifier
            },
        }
        # Invoke the graph with the initial state and configuration
        return self.app.invoke(initial_state, config=config)


DIR_CREDENTIALS = settings.BASE_DIR / "clave.json"
CREDENTIALS = service_account.Credentials.from_service_account_file(DIR_CREDENTIALS)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = "us-central1"

MODEL_VERTEX = "gemini-1.5-pro-002"
# vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=CREDENTIALS)  # noqa: ERA001,E501
vertexai.init(project=PROJECT_ID, location=LOCATION)
