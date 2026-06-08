"""Interactive command-line interface for the Mistral real-estate agent."""

from agent import RealEstateAgent


def main() -> None:
    agent = RealEstateAgent()
    print("Agent immobilier IA pret. Ecrivez 'quitter' pour terminer.")

    while True:
        try:
            user_message = input("\nVous : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir.")
            break

        if user_message.lower() in {"quitter", "quit", "exit"}:
            print("Au revoir.")
            break

        if user_message.lower() == "reset":
            agent.reset()
            print("Agent : conversation reinitialisee.")
            continue

        if not user_message:
            continue

        try:
            print(f"Agent : {agent.chat(user_message)}")
        except Exception as error:
            print(f"Erreur : {error}")


if __name__ == "__main__":
    main()
