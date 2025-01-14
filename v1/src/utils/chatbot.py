import streamlit as st
from src.utils.config import Defaults
from src.utils.dashboard import (
    get_feedback_metrics,
    get_cost_metrics,
    get_latency_metrics,
)
import pandas as pd
import plotly.express as px


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

    def create_dashboard(self):
        """Create the dashboard page with subtabs"""
        st.title("Dashboard 📊")
        st.markdown("Analyze the chatbot's performance and user interactions.")

        tab1, tab2, tab3 = st.tabs(["Usage Stats", "Cost Analysis", "Performance"])

        self.create_usage_stats(tab1)
        self.create_cost_analysis(tab2)
        self.create_performance_metrics(tab3)

    def create_usage_stats(self, tab):
        """Create the usage stats tab"""
        with tab:
            st.title("Feedback Relevance Metrics")
            df = get_feedback_metrics()
            self.display_feedback_metrics(df)

    def display_feedback_metrics(self, df):
        """Display feedback metrics as a bar chart"""
        fig = px.bar(
            df.melt(id_vars="NAME", var_name="Metric", value_name="Value"),
            x="NAME",
            y="Value",
            color="Metric",
            barmode="group",
            title="Feedback Relevance Metrics",
            labels={
                "NAME": "Category",
                "Value": "Score",
                "Metric": "Feedback Type",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    def create_cost_analysis(self, tab):
        """Create the cost analysis tab"""
        with tab:
            st.header("Cost Analysis")
            st.markdown("### Data Overview")
            cost_df = get_cost_metrics()
            cost_df["COST"] = pd.to_numeric(cost_df["COST"], errors="coerce")

            # Display cost metrics
            self.display_cost_metrics(cost_df)

            # Plot cost distribution
            self.display_cost_distribution(cost_df)

            # Scatter plot for Cost vs. Tokens
            self.display_cost_vs_tokens(cost_df)

    def display_cost_metrics(self, cost_df):
        """Display the cost metrics"""
        avg_cost = cost_df["COST"].mean()
        max_cost = cost_df["COST"].max()
        min_cost = cost_df["COST"].min()

        st.markdown(f"**Average Cost:** {avg_cost:.2f}")
        st.markdown(f"**Maximum Cost:** {max_cost:.2f}")
        st.markdown(f"**Minimum Cost:** {min_cost:.2f}")

    def display_cost_distribution(self, cost_df):
        """Display the cost distribution as a bar chart"""
        fig = px.bar(
            cost_df,
            x=cost_df.index,
            y="COST",
            title="Cost per Record",
            labels={"index": "Record Index", "COST": "Cost"},
            color="COST",
        )
        st.plotly_chart(fig, use_container_width=True)

    def display_cost_vs_tokens(self, cost_df):
        """Display a scatter plot for cost vs. tokens"""
        scatter_fig = px.scatter(
            cost_df,
            x="TOKENS",
            y="COST",
            size="COST",
            title="Cost vs Tokens",
            labels={"TOKENS": "Tokens", "COST": "Cost"},
        )
        st.plotly_chart(scatter_fig, use_container_width=True)

    def create_performance_metrics(self, tab):
        """Create the performance metrics tab"""
        with tab:
            performance_df = get_latency_metrics()
            self.display_performance_metrics(performance_df)

    def display_performance_metrics(self, performance_df):
        """Display performance metrics as a bar chart"""
        st.markdown("### Latency Distribution")
        fig = px.bar(
            performance_df,
            x=performance_df.index,
            y="LATENCY",
            title="LATENCY per Record",
            labels={"index": "Record Index", "LATENCY": "Latency"},
            color="LATENCY",
        )
        st.plotly_chart(fig, use_container_width=True)

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

    def set_page_config(self):
        st.set_page_config(
            page_title=f"{Defaults.APP_NAME}",
            page_icon="🏛️",
            layout="wide",
            initial_sidebar_state="expanded",
        )

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

    def create_bot(self):
        """Create the chatbot app"""
        self.set_page_config()
        page = self.create_sidebar()

        if page == "Chatbot":
            self.create_main_content()
            self.create_chat_interface()
            self.create_chat_input()
        elif page == "Dashboard":
            self.create_dashboard()
