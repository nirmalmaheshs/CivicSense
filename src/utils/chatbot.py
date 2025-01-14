import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.utils.config import Defaults
from src.utils.dashboard import (
    get_feedback_metrics,
    get_cost_metrics,
    get_latency_metrics,
    get_daily_stats
)


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
        st.title(f"{Defaults.APP_NAME} Dashboard 📊")
        st.markdown("### Performance Analytics and Monitoring")

        # Create metrics KPI cards
        self.display_kpi_metrics()

        # Create tabs for detailed analysis
        tab1, tab2, tab3 = st.tabs(["Quality Metrics", "Cost Analysis", "Performance"])

        with tab1:
            self.create_quality_metrics_tab()

        with tab2:
            self.create_cost_analysis_tab()

        with tab3:
            self.create_performance_metrics_tab()

    def display_kpi_metrics(self):
        """Display KPI metrics at the top of the dashboard"""
        try:
            feedback_df = get_feedback_metrics()
            daily_stats = get_daily_stats()
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                # Get total queries from daily stats
                queries = daily_stats['QUERY_COUNT'].sum() if not daily_stats.empty else 0
                st.metric("Total Queries", f"{queries:,.0f}")

            with col2:
                # Calculate average response time
                avg_latency = daily_stats['AVG_LATENCY'].mean() if not daily_stats.empty else 0
                st.metric("Avg Response Time", f"{avg_latency:.2f}s")

            with col3:
                try:
                    groundedness = feedback_df[feedback_df['name'] == 'Groundedness']['avg_score'].iloc[0]
                    groundedness_display = f"{groundedness:.1%}"
                except (KeyError, IndexError):
                    groundedness_display = "N/A"
                st.metric("Groundedness", groundedness_display)

            with col4:
                try:
                    relevance = feedback_df[feedback_df['name'] == 'Context Relevance']['avg_score'].iloc[0]
                    relevance_display = f"{relevance:.1%}"
                except (KeyError, IndexError):
                    relevance_display = "N/A"
                st.metric("Context Relevance", relevance_display)

        except Exception as e:
            st.error(f"Error loading metrics: {str(e)}")
            st.write("Debug info:")
            if 'daily_stats' in locals():
                st.write("Available columns in daily_stats:", daily_stats.columns.tolist())
            if 'feedback_df' in locals():
                st.write("Available columns in feedback_df:", feedback_df.columns.tolist())

    def create_quality_metrics_tab(self):
        """Create the quality metrics tab"""
        st.header("Quality Metrics")

        try:
            feedback_df = get_feedback_metrics()

            # Create bar chart for feedback scores
            fig = px.bar(
                feedback_df,
                x='NAME',  # Updated to match the query
                y='AVG_SCORE',  # Updated to match the query
                error_y=feedback_df['MAX_SCORE'] - feedback_df['AVG_SCORE'],
                error_y_minus=feedback_df['AVG_SCORE'] - feedback_df['MIN_SCORE'],
                title="Feedback Scores by Type",
                labels={
                    'NAME': 'Metric Type',
                    'AVG_SCORE': 'Score',
                    'QUERY_COUNT': 'Number of Queries'
                },
                color='NAME'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Show detailed metrics table
            st.markdown("### Detailed Metrics")

            # Format the dataframe for display
            display_df = feedback_df.copy()
            for col in ['MIN_SCORE', 'AVG_SCORE', 'MAX_SCORE']:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}")

            st.dataframe(
                display_df,
                column_config={
                    "NAME": "Metric Name",
                    "MIN_SCORE": "Minimum Score",
                    "AVG_SCORE": "Average Score",
                    "MAX_SCORE": "Maximum Score",
                    "QUERY_COUNT": "Number of Queries"
                }
            )

        except Exception as e:
            st.error(f"Error creating quality metrics visualization: {str(e)}")
            st.write("Debug info:")
            if 'feedback_df' in locals():
                st.write("Available columns:", feedback_df.columns.tolist())
                st.write("Data sample:", feedback_df.head())

    def create_cost_analysis_tab(self):
        """Create the cost analysis tab"""
        st.header("Cost Analysis")

        try:
            cost_df = get_cost_metrics()

            # Format the dataframe safely handling None values
            display_df = cost_df.copy()
            display_df['COST'] = display_df['COST'].apply(lambda x: f"${x:.2f}" if pd.notnull(x) else "N/A")
            display_df['TOKENS'] = display_df['TOKENS'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A")

            # Create visualization for cost metrics
            fig1 = px.line(
                cost_df,
                x='TIME',
                y='COST',
                title='Cost Over Time',
                labels={
                    'TIME': 'Time',
                    'COST': 'Cost ($)'
                }
            )
            st.plotly_chart(fig1, use_container_width=True)

            # Rest of your visualizations...

            # Show detailed metrics table
            st.markdown("### Detailed Metrics")
            st.dataframe(
                display_df,
                column_config={
                    "TIME": "Timestamp",
                    "COST": "Total Cost",
                    "TOKENS": "Token Count",
                    "QUERY_COUNT": "Number of Queries"
                }
            )

        except Exception as e:
            st.error(f"Error creating cost analysis visualization: {str(e)}")
            st.write("Debug info:")
            if 'cost_df' in locals():
                st.write("Available columns:", cost_df.columns.tolist())
                st.write("Data sample:", cost_df.head())

    def create_performance_metrics_tab(self):
        """Create the performance metrics tab"""
        st.header("Performance Metrics")

        try:
            latency_df = get_latency_metrics()
            if not latency_df.empty:
                # Create area chart for latency
                fig = px.area(
                    latency_df,
                    x='TIME',  # matches the column name from our SQL query
                    y=["MIN_LATENCY", "AVG_LATENCY", "MAX_LATENCY"],
                    title='Response Time Distribution',
                    labels={
                        'time': 'Time',
                        'value': 'Latency (seconds)',
                        'variable': 'Metric Type'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)

                # Show request volume over time
                fig2 = px.line(
                    latency_df,
                    x='TIME',
                    y='REQUEST_COUNT',
                    title='Request Volume Over Time',
                    labels={
                        'time': 'Time',
                        'request_count': 'Number of Requests'
                    }
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No performance data available yet.")

        except Exception as e:
            st.error(f"Error creating performance metrics visualization: {str(e)}")
            st.write("Debug info:")
            if 'latency_df' in locals():
                st.write("Available columns:", latency_df.columns.tolist())
                st.write("Data sample:", latency_df.head())

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
        page = self.create_sidebar()

        if page == "Chatbot":
            self.create_main_content()
            self.create_chat_interface()
            self.create_chat_input()
        elif page == "Dashboard":
            self.create_dashboard()