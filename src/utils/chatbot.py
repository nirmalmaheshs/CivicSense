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
        container = st.container()
        container.markdown('<style>div[data-testid="stImage"] img {max-height: 50px; width: auto;}</style>', unsafe_allow_html=True)
        with container:
            st.image("src/images/logofull.png")
        st.markdown(
            """
            Ask questions about government policies and benefits.
            I'll provide accurate information with references to official documents.
            """
        )

    def format_source_link(self, source: str) -> str:
        """Format source filename as a clickable link"""
        base_url = Defaults.SITE_DOMAIN_PREFIX
        # Extract filename without extension
        filename = source.split('.')[0]
        return f"[{base_url}{filename}]({base_url}{filename})"

    def display_messages(self, prompt: str):
        """Display user and assistant messages with references"""
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching policy documents..."):
                with self.evaluator as recording:
                    response = self.rag.query(prompt)

                # Display the main answer
                st.markdown(response["answer"])

                # Display sources in an expander if available
                if response.get("sources"):
                    with st.expander("View References"):
                        st.markdown("Sources:")
                        for source in response["sources"]:
                            st.markdown(f"- {self.format_source_link(source)}")

                # Store both answer and sources in session state
                message = {
                    "role": "assistant",
                    "content": response["answer"],
                    "sources": response.get("sources", [])
                }
                st.session_state.messages.append(message)

    def create_chat_interface(self):
        """Create the chat interface with reference support"""
        chat_container = st.container()
        if "messages" not in st.session_state:
            st.session_state.messages = []

        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if message["role"] == "assistant" and message.get("sources"):
                        with st.expander("View References"):
                            for source in message["sources"]:
                                st.markdown(f"- {self.format_source_link(source)}")

    def create_chat_input(self):
        """Create the chat input area"""
        if prompt := st.chat_input("Ask about government policies..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            self.display_messages(prompt)

    def create_bot(self):
        """Create the chatbot app"""
        # page = self.create_sidebar()
        self.create_main_content()
        self.create_chat_interface()
        self.create_chat_input()