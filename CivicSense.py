from src.classes.trulens.cortex_evaluator import CortextEvaluator
from src.classes.snowflake.llm_rag import Predictor
from src.utils.config import Defaults, load_llm_config
from src.utils.chatbot import StreamlitChatBot
import streamlit as st

def set_page_config():
    """Set the Streamlit page configuration"""
    with open("src/images/logo.svg", "r") as f:
        svg_content = f.read()
        
    st.set_page_config(
        page_title=f"{Defaults.APP_NAME}",
        page_icon=svg_content,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def main():
    set_page_config()
    llm_config = load_llm_config()
    rag = Predictor(chunk_size=llm_config['retriever_chunk_size'])
    evaluator = CortextEvaluator().get_evaluator(
        rag, llm_config
    )
    chatbot = StreamlitChatBot(evaluator, rag)
    chatbot.create_bot()

if __name__ == "__main__":
    main()