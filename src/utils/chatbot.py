import streamlit as st
from src.utils.config import Defaults


class StreamlitChatBot:
    def __init__(self, evaluator, rag):
        self.evaluator = evaluator
        self.rag = rag

    def create_sidebar(self):
        """Create and populate the sidebar"""
        with st.sidebar:
            st.markdown("### Navigation")
            page = st.radio(
                "Select Page",
                ["Chatbot", "Dashboard"],
                index=0,
            )
        return page

    def create_main_content(self):
        """Create the main chatbot content"""
        st.title(f"{Defaults.APP_NAME} 🏛️")
        st.markdown(
            """
            Ask questions about government policies and benefits.
            I'll provide accurate information with references to official documents.
            """
        )

    def create_chat_interface(self):
        """Create the chat interface"""
        chat_container = st.container()
        if "messages" not in st.session_state:
            st.session_state.messages = []

        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    def display_messages(self, prompt: str):
        """Display user and assistant messages"""
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching policy documents..."):
                with self.evaluator as recording:
                    response = self.rag.query(prompt)

                message = {"role": "assistant", "content": response}
                st.markdown(message["content"])
                st.session_state.messages.append(message)

    def create_chat_input(self):
        """Create the chat input area"""
        if prompt := st.chat_input("Ask about government policies..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            self.display_messages(prompt)

    def set_page_config(self):
        """Set the Streamlit page configuration"""
        st.set_page_config(
            page_title=f"{Defaults.APP_NAME}",
            page_icon="🏛️",
            layout="wide",
            initial_sidebar_state="expanded",
        )

    def create_bot(self):
        """Create the chatbot app"""
        self.set_page_config()
        # page = self.create_sidebar()
        self.create_main_content()
        self.create_chat_interface()
        self.create_chat_input()