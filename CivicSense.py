from src.classes.trulens.cortex_evaluator import CortextEvaluator
from src.classes.snowflake.llm_rag import Predictor
from src.utils.config import Defaults
from src.utils.chatbot import StreamlitChatBot
import streamlit as st

def set_page_config():
    """Set the Streamlit page configuration"""
    st.set_page_config(
        page_title=f"{Defaults.APP_NAME}",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def main():
    set_page_config()  # Call this first
    rag = Predictor()
    evaluator = CortextEvaluator().get_evaluator(
        rag, Defaults.APP_NAME, Defaults.APP_VERSION
    )
    chatbot = StreamlitChatBot(evaluator, rag)
    chatbot.create_bot()

if __name__ == "__main__":
    main()