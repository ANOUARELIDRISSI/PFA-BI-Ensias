"""Minimal conversational agent powered by Mistral AI."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_mistralai import ChatMistralAI


SYSTEM_PROMPT = """
Tu es un assistant specialise dans l'immobilier au Maroc.
Tu reponds en francais, de maniere concise, claire et factuelle.
Tu aides a comprendre les annonces, les prix, les villes et les predictions
produites par le projet PFA-BI-Ensias.
""".strip()


class RealEstateAgent:
    """A small stateful chat wrapper around Mistral."""

    def __init__(self, model: str = "mistral-small-latest") -> None:
        load_dotenv()
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError(
                "MISTRAL_API_KEY est absente. Copiez .env.example vers .env "
                "et ajoutez votre cle Mistral."
            )

        self.llm = ChatMistralAI(
            model=model,
            api_key=api_key,
            temperature=0.2,
        )
        self.messages: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]

    def chat(self, user_message: str) -> str:
        """Send one message and retain the conversation history."""
        message = user_message.strip()
        if not message:
            raise ValueError("Le message ne peut pas etre vide.")

        self.messages.append(HumanMessage(content=message))
        response = self.llm.invoke(self.messages)
        self.messages.append(response)

        if isinstance(response, AIMessage):
            return str(response.content)
        return str(response)

    def reset(self) -> None:
        """Clear conversation history while retaining the system prompt."""
        self.messages = [SystemMessage(content=SYSTEM_PROMPT)]
