import uuid
import streamlit as st
from src.utils.config import Defaults
from src.utils.queries import (
    get_feedback_metrics,
    get_cost_metrics,
    get_latency_metrics,
    get_daily_stats
)
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class PerformanceMetrics():
    def __init__(self):
        self.create_dashboard()

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
                    groundedness = feedback_df[feedback_df['NAME'] == 'Groundedness']['AVG_SCORE'].iloc[0]
                    groundedness_display = f"{groundedness:.1%}"
                except (KeyError, IndexError):
                    groundedness_display = "N/A"
                st.metric("Groundedness", groundedness_display)

            with col4:
                try:
                    relevance = feedback_df[feedback_df['NAME'] == 'Context Relevance']['AVG_SCORE'].iloc[0]
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
                color='NAME',
            )
            st.plotly_chart(fig, use_container_width=True, key=f"{uuid.uuid4()}")

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

            # Format the dataframe for display
            display_df = cost_df.copy()
            display_df['COST'] = display_df.apply(
                lambda x: f"${x['COST']:.4f} {x['CURRENCY']}" if pd.notnull(x['COST']) else "N/A",
                axis=1
            )
            display_df['TOTAL_TOKENS'] = display_df['TOKENS'].apply(
                lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A"
            )
            display_df['PROMPT_TOKENS'] = display_df['PROMPT_TOKENS'].apply(
                lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A"
            )
            display_df['COMPLETION_TOKENS'] = display_df['COMPLETION_TOKENS'].apply(
                lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A"
            )

            # Cost over time visualization
            fig1 = px.line(
                cost_df,
                x='TIME',
                y='COST',
                title='Cost Over Time',
                labels={
                    'TIME': 'Time',
                    'COST': f'Cost ({cost_df["CURRENCY"].iloc[0]})'
                }
            )
            st.plotly_chart(fig1, use_container_width=True, key=f"{uuid.uuid4()}")

            # Token usage breakdown
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name='Prompt Tokens',
                x=cost_df['TIME'],
                y=cost_df['PROMPT_TOKENS'],
            ))
            fig2.add_trace(go.Bar(
                name='Completion Tokens',
                x=cost_df['TIME'],
                y=cost_df['COMPLETION_TOKENS'],
            ))
            fig2.update_layout(
                barmode='stack',
                title='Token Usage Breakdown Over Time',
                xaxis_title='Time',
                yaxis_title='Number of Tokens'
            )
            st.plotly_chart(fig2, use_container_width=True, key=f"{uuid.uuid4()}")

            # Query volume visualization
            fig3 = px.line(
                cost_df,
                x='TIME',
                y='QUERY_COUNT',
                title='Query Volume Over Time',
                labels={
                    'TIME': 'Time',
                    'QUERY_COUNT': 'Number of Queries'
                }
            )
            st.plotly_chart(fig3, use_container_width=True, key=f"{uuid.uuid4()}")

            # Detailed metrics table
            st.markdown("### Detailed Metrics")
            st.dataframe(
                display_df,
                column_config={
                    "TIME": "Timestamp",
                    "COST": "Total Cost",
                    "TOTAL_TOKENS": "Total Tokens",
                    "PROMPT_TOKENS": "Prompt Tokens",
                    "COMPLETION_TOKENS": "Completion Tokens",
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
