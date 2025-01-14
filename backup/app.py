import streamlit as st
import requests
import mimetypes
from src.chatbot import PolicyChatbot
from src.evaluator import Evaluator
from src.utils import get_snowpark_session


def initialize_app():
    """Initialize the application state"""
    # Initialize chatbot first
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = PolicyChatbot()

    if "truapp" not in st.session_state:
        st.session_state.truapp = Evaluator().tru_app
        st.session_state.trusession = Evaluator().session

    if "messages" not in st.session_state:
        st.session_state.messages = []

    return st.session_state.chatbot


def get_mime_type(filename: str) -> str:
    """Get MIME type based on file extension"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


def fetch_file_content(signed_url: str) -> bytes:
    """Fetch file content from Snowflake signed URL"""
    try:
        response = requests.get(
            signed_url, headers={"Accept": "*/*"}, allow_redirects=True
        )
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error("Unable to fetch the file content.")
        st.error(str(e))
        return None


def handle_file_actions(signed_url: str, filename: str):
    """Handle file download action"""
    try:
        # Fetch content
        content = fetch_file_content(signed_url)
        if content:
            mime_type = get_mime_type(filename)
            st.download_button(
                label="📥",
                key=filename,
                data=content,
                file_name=filename,
                mime=mime_type,
                help=f"Download {filename}",
            )
    except Exception as e:
        st.error(f"Unable to process {filename}")


def display_message_with_references(message):
    """Display a message with its references and source documents"""
    # Display the message content
    st.markdown(message["content"])

    # Handle references for assistant messages
    if (
        message["role"] == "assistant"
        and "references" in message
        and message["references"]
    ):
        st.markdown("### Source Documents 📚")

        # Group references by source file
        sources_dict = {}
        for ref in message["references"]:
            source_file = ref.get("source", "Unknown Source")
            if source_file not in sources_dict:
                sources_dict[source_file] = {"signed_url": ref.get("signed_url", "")}

        # Display source documents in a more compact layout
        for source_file, data in sources_dict.items():
            col1, col2 = st.columns([1.9, 0.1])
            with col1:
                st.markdown(
                    f"📄 {source_file}",
                    help="Click download button to access this document",
                )
            with col2:
                if data["signed_url"]:
                    handle_file_actions(data["signed_url"], source_file.split("/")[-1])


def create_sidebar():
    """Create and populate the sidebar"""
    with st.sidebar:
        st.markdown("### About")
        st.markdown(
            """
        Welcome to the CivicSense! This AI-powered chatbot helps you:
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


def display_message_with_references(message):
    """Display a message with its references and source documents"""
    # Display the message content
    st.markdown(message["content"])

    # Handle references for assistant messages
    if (
        message["role"] == "assistant"
        and "references" in message
        and message["references"]
    ):
        st.markdown("### 📚 Source Documents")

        # Group references by source file
        sources_dict = {}
        for ref in message["references"]:
            source_file = ref.get("source", "Unknown Source")
            if source_file not in sources_dict:
                sources_dict[source_file] = {
                    "chunks": [],
                    "signed_url": ref.get("signed_url", ""),
                }
            sources_dict[source_file]["chunks"].append(ref["chunk"])

        # Display each source and its content
        for source_file, data in sources_dict.items():
            st.markdown("---")

            # Display source filename
            st.markdown(f"#### 📄 {source_file}")

            # Handle file actions
            if data["signed_url"]:
                handle_file_actions(data["signed_url"], source_file.split("/")[-1])


def main():
    st.set_page_config(
        page_title="CivicSense",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize app components
    initialize_app()
    create_sidebar()

    # Main content area
    st.title("CivicSense 🏛️")
    st.markdown(
        """
    Ask questions about government policies and benefits.
    I'll provide accurate information with references to official documents.
    """
    )

    # Chat interface
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                display_message_with_references(message)

    # Chat input
    if prompt := st.chat_input("Ask about government policies..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Searching policy documents..."):

                with st.session_state.truapp as recording:
                    response, references = st.session_state.chatbot.query(prompt)

                print(st.session_state.trusession.get_leaderboard())

                # Create message with response and references
                message = {
                    "role": "assistant",
                    "content": response,
                    "references": references,
                }

                # Display the message and add to history
                display_message_with_references(message)
                st.session_state.messages.append(message)


if __name__ == "__main__":
    main()
