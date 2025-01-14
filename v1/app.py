from src.classes.trulens.cortex_evaluator import CortextEvaluator
from src.classes.snowflake.llm_rag import Predictor
from src.utils.config import Defaults
from src.utils.chatbot import StreamlitChatBot


def main():
    rag = Predictor()
    evaluator = CortextEvaluator().get_evaluator(
        rag, Defaults.APP_NAME, Defaults.APP_VERSION
    )
    chatbot = StreamlitChatBot(evaluator, rag)
    chatbot.create_bot()


if __name__ == "__main__":
    main()
