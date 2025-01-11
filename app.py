import streamlit as st
from src.utils import initialize_app, display_metrics

def main():
    st.set_page_config(
        page_title="Government Policy Assistant",
        page_icon="🏛️",
        layout="wide"
    )

    initialize_app()

    st.title("Government Policy Assistant 🏛️")
    st.write("Ask questions about government policies and benefits.")

    # Sidebar navigation and controls
    st.sidebar.title("Navigation & Settings")

    # Add navigation instructions
    st.sidebar.markdown("""
    ### 📍 Navigation
    - Current Page: Chat Interface
    - Click on **📊 Evaluation Dashboard** in the sidebar to view metrics
    """)

    st.sidebar.markdown("---")

    # Settings section
    st.sidebar.title("Settings")
    st.sidebar.toggle("Debug Mode", key="debug_mode")

    # Display metrics
    metrics = st.session_state.chatbot.get_metrics()
    display_metrics(metrics)

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about government policies..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get chatbot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.get_response(prompt)
                st.markdown(response)

                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

        # Update metrics display
        metrics = st.session_state.chatbot.get_metrics()
        display_metrics(metrics)


if __name__ == "__main__":
    main()