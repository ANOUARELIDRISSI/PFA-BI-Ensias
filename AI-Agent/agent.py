"""Minimal conversational agent powered by Mistral AI."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_mistralai import ChatMistralAI

from tools import REAL_ESTATE_TOOLS


SYSTEM_PROMPT = """
Tu es un assistant specialise dans l'immobilier au Maroc.
Tu reponds en francais, de maniere concise, claire et factuelle.
Tu utilises obligatoirement les outils pour les estimations, comparables,
comparaisons, recommandations, anomalies et statistiques. Tu ne dois jamais
inventer un prix ou une annonce.
Pour une question de suivi sur le meme bien, reutilise exactement les
caracteristiques deja fournies. Si le statut meuble n'est pas indique, utilise
NO. Distingue les donnees observees des estimations et conserve les
avertissements retournes par les outils.
""".strip()


class RealEstateAgent:
    """A small stateful chat wrapper around Mistral."""

    def __init__(self, model: str = "mistral-small-latest") -> None:
        env_path = Path(__file__).resolve().parent / ".env"
        load_dotenv(dotenv_path=env_path, override=True)
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
        self.tools = REAL_ESTATE_TOOLS
        self.tool_map = {item.name: item for item in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.messages: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]

    def chat(self, user_message: str) -> str:
        """Send one message and retain the conversation history."""
        message = user_message.strip()
        if not message:
            raise ValueError("Le message ne peut pas etre vide.")

        self.messages.append(HumanMessage(content=message))
        for _ in range(5):
            response = self.llm_with_tools.invoke(self.messages)
            self.messages.append(response)
            if not response.tool_calls:
                return str(response.content) if isinstance(response, AIMessage) else str(response)
            for call in response.tool_calls:
                selected = self.tool_map.get(call["name"])
                try:
                    result = selected.invoke(call["args"]) if selected else f"Outil inconnu: {call['name']}"
                except Exception as error:
                    result = f"Erreur outil: {error}"
                self.messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
        raise RuntimeError("L'agent a depasse le nombre maximal d'appels outils.")

    def reset(self) -> None:
        """Clear conversation history while retaining the system prompt."""
        self.messages = [SystemMessage(content=SYSTEM_PROMPT)]
