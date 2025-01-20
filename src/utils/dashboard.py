import uuid
import streamlit as st
from src.utils.queries import (
    get_feedback_metrics,
    get_cost_metrics,
    get_latency_metrics,
    get_daily_stats,
    get_model_evaluation_metrics,
    get_configuration_details
)
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


class PerformanceMetrics:
    def __init__(self):
        try:
            self.create_dashboard()
        except Exception as e:
            st.error(f"Failed to initialize dashboard: {str(e)}")

    def format_version_label(self, row):
        """Helper function to format version labels"""
        try:
            return f"{row['APP_NAME']} v{row['APP_VERSION']}"
        except KeyError as e:
            st.warning(f"Missing required field for version label: {str(e)}")
            return "Unknown Version"

    def create_dashboard(self):
        """Create the dashboard page with subtabs"""
        try:
            st.title("Performance Analytics and Monitoring 📊")

            # Create metrics KPI cards
            self.display_kpi_metrics()

            # Create tabs for detailed analysis
            tab1, tab2, tab3, tab4 = st.tabs([
                "📈 Quality Metrics",
                "💰 Cost Analysis",
                "⚡ Performance",
                "🔬 Model Evaluation"
            ])

            with tab1:
                self.create_quality_metrics_tab()
            with tab2:
                self.create_cost_analysis_tab()
            with tab3:
                self.create_performance_metrics_tab()
            with tab4:
                self.create_model_evaluation_tab()

        except Exception as e:
            st.error(f"Error creating dashboard: {str(e)}")

    def display_kpi_metrics(self):
        """Display KPI metrics at the top of the dashboard"""
        feedback_df = pd.DataFrame()
        daily_stats = pd.DataFrame()

        try:
            feedback_df = get_feedback_metrics()
            daily_stats = get_daily_stats()

            col1, col2, col3, col4 = st.columns(4)

            # Get latest version safely
            latest_version = daily_stats['APP_VERSION'].iloc[0] if not daily_stats.empty else 'N/A'

            with col1:
                # Total Queries
                if not daily_stats.empty:
                    latest_data = daily_stats[daily_stats['APP_VERSION'] == latest_version]
                    queries = latest_data['QUERY_COUNT'].sum() if not latest_data.empty else 0

                    # Calculate delta only if we have enough data
                    if len(latest_data) >= 2:
                        current_day = latest_data.iloc[0]['QUERY_COUNT']
                        previous_day = latest_data.iloc[1]['QUERY_COUNT']
                        delta = current_day - previous_day
                    else:
                        delta = None
                else:
                    queries = 0
                    delta = None

                st.metric(
                    "🔍 Total Queries (Latest Version)",
                    f"{queries:,.0f}",
                    delta=f"{delta:+.0f}" if delta is not None else None,
                    delta_color="normal",
                    help=f"Latest Version: v{latest_version}"
                )

            with col2:
                # Average Latency
                if not daily_stats.empty:
                    latest_data = daily_stats[daily_stats['APP_VERSION'] == latest_version]
                    avg_latency = latest_data['AVG_LATENCY'].mean() if not latest_data.empty else 0

                    # Calculate delta only if we have enough data
                    if len(latest_data) >= 2:
                        current_latency = latest_data.iloc[0]['AVG_LATENCY']
                        previous_latency = latest_data.iloc[1]['AVG_LATENCY']
                        delta_latency = current_latency - previous_latency
                    else:
                        delta_latency = None
                else:
                    avg_latency = 0
                    delta_latency = None

                st.metric(
                    "⚡ Avg Response Time",
                    f"{avg_latency:.2f}s",
                    delta=f"{delta_latency:+.2f}s" if delta_latency is not None else None,
                    delta_color="inverse",
                    help=f"For Version: v{latest_version}"
                )

            with col3:
                # Groundedness
                if not feedback_df.empty:
                    latest_feedback = feedback_df[feedback_df['APP_VERSION'] == latest_version]
                    groundedness_data = latest_feedback[latest_feedback['NAME'] == 'Groundedness']

                    if not groundedness_data.empty:
                        groundedness = groundedness_data['AVG_SCORE'].iloc[0]
                        groundedness_display = f"{groundedness:.1%}"

                        # Get previous groundedness if available
                        prev_data = feedback_df[
                            (feedback_df['NAME'] == 'Groundedness') &
                            (feedback_df['APP_VERSION'] != latest_version)
                            ]
                        if not prev_data.empty:
                            prev_groundedness = prev_data['AVG_SCORE'].iloc[0]
                            delta_groundedness = groundedness - prev_groundedness
                        else:
                            delta_groundedness = None
                    else:
                        groundedness_display = "N/A"
                        delta_groundedness = None
                else:
                    groundedness_display = "N/A"
                    delta_groundedness = None

                st.metric(
                    "🎯 Groundedness",
                    groundedness_display,
                    delta=f"{delta_groundedness:+.1%}" if delta_groundedness is not None else None,
                    help=f"For Version: v{latest_version}"
                )

            with col4:
                # Context Relevance
                if not feedback_df.empty:
                    latest_feedback = feedback_df[feedback_df['APP_VERSION'] == latest_version]
                    relevance_data = latest_feedback[latest_feedback['NAME'] == 'Context Relevance']

                    if not relevance_data.empty:
                        relevance = relevance_data['AVG_SCORE'].iloc[0]
                        relevance_display = f"{relevance:.1%}"

                        # Get previous relevance if available
                        prev_data = feedback_df[
                            (feedback_df['NAME'] == 'Context Relevance') &
                            (feedback_df['APP_VERSION'] != latest_version)
                            ]
                        if not prev_data.empty:
                            prev_relevance = prev_data['AVG_SCORE'].iloc[0]
                            delta_relevance = relevance - prev_relevance
                        else:
                            delta_relevance = None
                    else:
                        relevance_display = "N/A"
                        delta_relevance = None
                else:
                    relevance_display = "N/A"
                    delta_relevance = None

                st.metric(
                    "🎖️ Context Relevance",
                    relevance_display,
                    delta=f"{delta_relevance:+.1%}" if delta_relevance is not None else None,
                    help=f"For Version: v{latest_version}"
                )

        except pd.io.sql.DatabaseError as e:
            st.error(f"Database error while fetching metrics: {str(e)}")
        except pd.errors.EmptyDataError:
            st.warning("No data available for metrics")
        except Exception as e:
            st.error(f"Unexpected error loading metrics: {str(e)}")
            # Add debug information
            st.write("Debug info:")
            st.write("Daily stats shape:", daily_stats.shape if not daily_stats.empty else "Empty")
            st.write("Feedback shape:", feedback_df.shape if not feedback_df.empty else "Empty")
        finally:
            del feedback_df
            del daily_stats

    def create_quality_metrics_tab(self):
        """Create the quality metrics tab with enhanced visuals"""
        feedback_df = pd.DataFrame()
        try:
            st.header("📈 Quality Metrics Analysis")
            feedback_df = get_feedback_metrics()

            if feedback_df.empty:
                st.warning("No quality metrics data available")
                return

            versions = feedback_df['APP_VERSION'].unique()
            selected_version = st.selectbox(
                "Select Version to Analyze",
                versions,
                index=0,
                format_func=lambda x: f"v{x}"
            )

            version_data = feedback_df[feedback_df['APP_VERSION'] == selected_version]

            # Create bar chart for feedback scores
            fig = px.bar(
                version_data,
                x='NAME',
                y='AVG_SCORE',
                error_y=version_data['MAX_SCORE'] - version_data['AVG_SCORE'],
                error_y_minus=version_data['AVG_SCORE'] - version_data['MIN_SCORE'],
                title=f"📊 Feedback Scores Distribution (v{selected_version})",
                labels={
                    'NAME': 'Metric Type',
                    'AVG_SCORE': 'Score',
                    'QUERY_COUNT': 'Number of Queries'
                },
                color='NAME'
            )
            fig.update_layout(
                title_x=0.5,
                title_font_size=20,
                showlegend=True,
                legend_title_text="Metric Types"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Version comparison
            with st.expander("📊 Version Comparison"):
                comparison_df = feedback_df.pivot(
                    index='NAME',
                    columns='APP_VERSION',
                    values='AVG_SCORE'
                )
                comparison_df = comparison_df.round(4)
                comparison_df = comparison_df.applymap(
                    lambda x: f"{x:.2%}" if pd.notnull(x) else "N/A"
                )
                st.dataframe(comparison_df, use_container_width=True)

        except pd.io.sql.DatabaseError as e:
            st.error(f"Database error in quality metrics: {str(e)}")
        except ValueError as e:
            st.error(f"Error processing quality metrics: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error in quality metrics: {str(e)}")
        finally:
            del feedback_df

    def create_performance_metrics_tab(self):
        """Create the performance metrics tab with enhanced visuals"""
        latency_df = pd.DataFrame()
        try:
            st.header("⚡ Performance Analysis")
            latency_df = get_latency_metrics()

            if latency_df.empty:
                st.warning("No performance data available")
                return

            versions = latency_df['APP_VERSION'].unique()
            selected_version = st.selectbox(
                "Select Version for Performance Analysis",
                versions,
                index=0,
                format_func=lambda x: f"v{x}"
            )

            version_data = latency_df[latency_df['APP_VERSION'] == selected_version]

            # Performance metrics summary
            avg_latency = version_data['AVG_LATENCY'].mean()
            max_latency = version_data['MAX_LATENCY'].max()
            total_requests = version_data['REQUEST_COUNT'].sum()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div style='padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6'>
                    <h3 style='margin: 0'>⚡ Average Latency</h3>
                    <p style='font-size: 24px; margin: 0.5rem 0'>{avg_latency:.2f}s</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style='padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6'>
                    <h3 style='margin: 0'>⏱️ Peak Latency</h3>
                    <p style='font-size: 24px; margin: 0.5rem 0'>{max_latency:.2f}s</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div style='padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6'>
                    <h3 style='margin: 0'>📊 Total Requests</h3>
                    <p style='font-size: 24px; margin: 0.5rem 0'>{total_requests:,}</p>
                </div>
                """, unsafe_allow_html=True)

            # Latency distribution over time
            fig = px.area(
                version_data,
                x='TIME',
                y=['MIN_LATENCY', 'AVG_LATENCY', 'MAX_LATENCY'],
                title=f'Response Time Distribution Over Time (v{selected_version})',
                labels={
                    'time': 'Time',
                    'value': 'Latency (seconds)',
                    'variable': 'Metric Type'
                }
            )
            fig.update_layout(title_x=0.5)
            st.plotly_chart(fig, use_container_width=True)

            # Version comparison
            with st.expander("⚡ Version Performance Comparison"):
                version_summary = latency_df.groupby('APP_VERSION').agg({
                    'AVG_LATENCY': 'mean',
                    'MAX_LATENCY': 'max',
                    'REQUEST_COUNT': 'sum'
                }).reset_index()

                version_summary.columns = ['Version', 'Avg Latency', 'Max Latency', 'Total Requests']
                version_summary = version_summary.round(3)
                st.dataframe(version_summary, use_container_width=True)

        except pd.io.sql.DatabaseError as e:
            st.error(f"Database error in performance metrics: {str(e)}")
        except ValueError as e:
            st.error(f"Error processing performance data: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error in performance metrics: {str(e)}")
        finally:
            del latency_df

    def create_cost_analysis_tab(self):
        """Create the cost analysis tab with version tracking"""
        cost_df = pd.DataFrame()
        try:
            st.header("💰 Cost Analysis Dashboard")
            cost_df = get_cost_metrics()

            if cost_df.empty:
                st.warning("No cost analysis data available")
                return

            versions = cost_df['APP_VERSION'].unique()
            selected_version = st.selectbox(
                "Select Version for Cost Analysis",
                versions,
                index=0,
                format_func=lambda x: f"v{x}"
            )

            version_data = cost_df[cost_df['APP_VERSION'] == selected_version]

            total_cost = version_data['COST'].sum()
            total_tokens = version_data['TOKENS'].sum()

            # Cost summary cards
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div style='padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6'>
                    <h3 style='margin: 0'>💵 Total Cost (v{selected_version})</h3>
                    <p style='font-size: 24px; margin: 0.5rem 0'>${total_cost:.2f}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style='padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6'>
                    <h3 style='margin: 0'>🔤 Total Tokens (v{selected_version})</h3>
                    <p style='font-size: 24px; margin: 0.5rem 0'>{total_tokens:,.0f}</p>
                </div>
                """, unsafe_allow_html=True)

            # Cost trends
            fig1 = px.line(
                version_data,
                x='TIME',
                y='COST',
                title=f'Cost Over Time (v{selected_version})',
                labels={
                    'TIME': 'Time',
                    'COST': f'Cost ({version_data["CURRENCY"].iloc[0]})'
                }
            )
            fig1.update_layout(title_x=0.5)
            st.plotly_chart(fig1, use_container_width=True)

            # Token usage breakdown
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name='🔵 Prompt Tokens',
                x=version_data['TIME'],
                y=version_data['PROMPT_TOKENS'],
            ))
            fig2.add_trace(go.Bar(
                name='🟢 Completion Tokens',
                x=version_data['TIME'],
                y=version_data['COMPLETION_TOKENS'],
            ))
            fig2.update_layout(
                barmode='stack',
                title=f'Token Usage Breakdown Over Time (v{selected_version})',
                title_x=0.5,
                xaxis_title='Time',
                yaxis_title='Number of Tokens'
            )
            st.plotly_chart(fig2, use_container_width=True)

            # Version cost comparison
            with st.expander("💰 Version Cost Comparison"):
                version_summary = cost_df.groupby('APP_VERSION').agg({
                    'COST': 'sum',
                    'TOKENS': 'sum',
                    'QUERY_COUNT': 'sum'
                }).reset_index()

                version_summary['Cost per Query'] = version_summary['COST'] / version_summary['QUERY_COUNT']
                version_summary['Tokens per Query'] = version_summary['TOKENS'] / version_summary['QUERY_COUNT']

                st.dataframe(
                    version_summary.round(4),
                    column_config={
                        'APP_VERSION': 'Version',
                        'COST': st.column_config.NumberColumn('Total Cost', format="$%.2f"),
                        'Cost per Query': st.column_config.NumberColumn('Cost per Query', format="$%.4f"),
                        'Tokens per Query': st.column_config.NumberColumn('Tokens per Query', format="%.1f"),
                    }
                )

        except pd.io.sql.DatabaseError as e:
            st.error(f"Database error in cost analysis: {str(e)}")
        except ValueError as e:
            st.error(f"Error processing cost data: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error in cost analysis: {str(e)}")
        finally:
            del cost_df

    def create_model_evaluation_tab(self):
        """Create the model evaluation comparison tab"""
        eval_df = pd.DataFrame()
        config_df = pd.DataFrame()
        try:
            st.header("🔬 Model Evaluation")
            eval_df = get_model_evaluation_metrics()
            config_df = get_configuration_details()

            if eval_df.empty:
                st.warning("No model evaluation data available")
                return

            # Version selector
            versions = eval_df['APP_VERSION'].unique()
            if len(versions) > 1:
                selected_versions = st.multiselect(
                    "Select Versions to Compare",
                    versions,
                    default=versions[-2:],  # Select last two versions by default
                    format_func=lambda x: f"v{x}"
                )
                filtered_df = eval_df[eval_df['APP_VERSION'].isin(selected_versions)]
            else:
                filtered_df = eval_df
                st.info("Only one version available for comparison")

            # Radar chart for quality metrics
            fig = go.Figure()
            for _, row in filtered_df.iterrows():
                version_label = f"{row['APP_NAME']} v{row['APP_VERSION']}"
                fig.add_trace(go.Scatterpolar(
                    r=[
                        row['AVG_GROUNDEDNESS'] * 100,
                        row['AVG_CONTEXT_RELEVANCE'] * 100,
                        row['AVG_ANSWER_RELEVANCE'] * 100
                    ],
                    theta=['Groundedness', 'Context Relevance', 'Answer Relevance'],
                    name=version_label
                ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                title="Quality Metrics Comparison Across Versions",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

            # Configuration comparison table
            st.markdown("### Metrics Comparison")

            # Prepare a clean comparison dataframe
            comparison_df = filtered_df[[
                'APP_NAME', 'APP_VERSION',
                'AVG_GROUNDEDNESS', 'AVG_CONTEXT_RELEVANCE', 'AVG_ANSWER_RELEVANCE',
                'AVG_LATENCY', 'TOTAL_QUERIES', 'AVG_COST'
            ]].copy()

            # Format the metrics
            for col in ['AVG_GROUNDEDNESS', 'AVG_CONTEXT_RELEVANCE', 'AVG_ANSWER_RELEVANCE']:
                comparison_df[col] = comparison_df[col].apply(lambda x: f"{x * 100:.2f}%")

            comparison_df['AVG_LATENCY'] = comparison_df['AVG_LATENCY'].apply(lambda x: f"{x:.2f}s")
            comparison_df['AVG_COST'] = comparison_df['AVG_COST'].apply(lambda x: f"${x:.4f}")

            # Rename columns for display
            comparison_df.columns = [
                'App Name', 'Version',
                'Groundedness', 'Context Relevance', 'Answer Relevance',
                'Avg Response Time', 'Total Queries', 'Avg Cost per Query'
            ]

            st.dataframe(
                comparison_df,
                use_container_width=True,
                hide_index=True
            )

            # Show configuration details
            if not config_df.empty:
                st.markdown("### Configuration Details")
                for _, config in config_df.iterrows():
                    if config['APP_VERSION'] in selected_versions:
                        with st.expander(f"Configuration: {config['APP_NAME']} v{config['APP_VERSION']}"):
                            # Display tags
                            st.markdown("#### Tags")
                            try:
                                tags = eval(config['TAGS'])
                                if tags:
                                    st.json(tags)
                                else:
                                    st.info("No tags available")
                            except:
                                st.warning("Invalid tag format")

                            # Display configuration details
                            st.markdown("#### Config Details")
                            try:
                                if isinstance(config['CONFIG_DETAILS'], (dict, str)):
                                    st.json(config['CONFIG_DETAILS'])
                                else:
                                    st.info("No configuration details available")
                            except:
                                st.warning("Invalid configuration format")

        except pd.io.sql.DatabaseError as e:
            st.error(f"Database error in model evaluation: {str(e)}")
        except ValueError as e:
            st.error(f"Error processing evaluation data: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error in model evaluation: {str(e)}")
            st.write("Debug info:")
            if 'eval_df' in locals():
                st.write("Available columns:", eval_df.columns.tolist())
                st.write("Data sample:", eval_df.head())
        finally:
            del eval_df
            del config_df