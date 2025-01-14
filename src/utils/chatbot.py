import streamlit as st
from src.utils.session import session
from src.utils.config import Defaults


class StreamlitChatBot:

    def __init__(self, evaluator, rag):
        self.evaluator = evaluator
        self.rag = rag

    def create_sidebar(self):
        """Create and populate the sidebar"""
        with st.sidebar:
            st.markdown("### About")
            st.markdown(
                f"""
            Welcome to the {Defaults.APP_NAME}! This AI-powered chatbot helps you:
            - Find information about government policies
            - Understand available benefits
            - Access official policy documents
            - Get accurate information from verified sources
            """
            )

            st.markdown("### Tips for Better Results")
            st.markdown(
                """
            - Be specific in your questions
            - Ask about one topic at a time
            - Include relevant context or details
            - Review source documents for complete information
            """
            )

            st.markdown("### ℹ️ How It Works")
            st.markdown(
                """
            1. Your question is analyzed
            2. Relevant policy documents are retrieved
            3. AI processes the information
            4. Response is generated with source references
            5. Original documents are available for download
            """
            )

            st.markdown("---")
            st.caption("*Powered by Snowflake & Mistral AI*")

    def create_main_content(self):
        # Main content area
        st.title(f"{Defaults.APP_NAME} 🏛️")
        st.markdown(
            """
            Ask questions about government policies and benefits.
            I'll provide accurate information with references to official documents.
            """
        )

    def create_chat_interface(self):
        chat_container = st.container()
        if "messages" not in st.session_state:
            st.session_state.messages = []
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    def set_page_config(self):
        st.set_page_config(
            page_title=f"{Defaults.APP_NAME}",
            page_icon="🏛️",
            layout="wide",
            initial_sidebar_state="expanded",
        )

    def display_messages(self, prompt: str):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Searching policy documents..."):

                with self.evaluator as recording:
                    response = self.rag.query(prompt)

                print(session.tru_session.get_leaderboard())

                # Display the message and add to history
                message = {"role": "assistant", "content": response}
                st.markdown(message["content"])
                st.session_state.messages.append(message)

    def create_chat_input(self):
        # Chat input
        if prompt := st.chat_input("Ask about government policies..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            self.display_messages(prompt)

    def create_bot(self):
        self.set_page_config()
        self.create_sidebar()
        self.create_main_content()
        self.create_chat_interface()
        self.create_chat_input()
