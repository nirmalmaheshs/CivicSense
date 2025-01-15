import uuid
import streamlit as st
from src.utils.queries import (
    get_feedback_metrics,
    get_cost_metrics,
    get_latency_metrics,
    get_daily_stats, get_model_evaluation_metrics, get_configuration_details
)
import plotly.express as px
import plotly.graph_objects as go

class PerformanceMetrics:
    def __init__(self):
        self.create_dashboard()

    def create_dashboard(self):
        """Create the dashboard page with subtabs"""
        st.title("Performance Analytics and Monitoring 📊")

        # Create metrics KPI cards
        self.display_kpi_metrics()

        # Create tabs for detailed analysis
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Quality Metrics", "💰 Cost Analysis", "⚡ Performance", "🔬 Model Evaluation"])

        with tab1:
            self.create_quality_metrics_tab()

        with tab2:
            self.create_cost_analysis_tab()

        with tab3:
            self.create_performance_metrics_tab()

        with tab4:
            self.create_model_evaluation_tab()

    def display_kpi_metrics(self):
        """Display KPI metrics at the top of the dashboard"""
        try:
            feedback_df = get_feedback_metrics()
            daily_stats = get_daily_stats()
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                # Total Queries with trend indicator
                queries = daily_stats['QUERY_COUNT'].sum() if not daily_stats.empty else 0

                # Calculate delta by comparing the two most recent days
                if not daily_stats.empty and len(daily_stats) >= 2:
                    current_day = daily_stats.iloc[0]['QUERY_COUNT']
                    previous_day = daily_stats.iloc[1]['QUERY_COUNT']
                    delta = current_day - previous_day
                else:
                    delta = None

                st.metric("🔍 Total Queries",
                          f"{queries:,.0f}",
                          delta=f"{delta:+.0f}" if delta is not None else None,
                          delta_color="normal")

            with col2:
                avg_latency = daily_stats['AVG_LATENCY'].mean() if not daily_stats.empty else 0

                # Calculate delta by comparing the two most recent days
                if not daily_stats.empty and len(daily_stats) >= 2:
                    current_latency = daily_stats.iloc[0]['AVG_LATENCY']
                    previous_latency = daily_stats.iloc[1]['AVG_LATENCY']
                    delta_latency = current_latency - previous_latency
                else:
                    delta_latency = None

                # Note: Negative delta is better for latency (faster response time)
                st.metric("⚡ Avg Response Time",
                          f"{avg_latency:.2f}s",
                          delta=f"{delta_latency:+.2f}s" if delta_latency is not None else None,
                          delta_color="inverse")
            with col3:
                    try:
                        groundedness = feedback_df[feedback_df['NAME'] == 'Groundedness']['AVG_SCORE'].iloc[0]
                        groundedness_display = f"{groundedness:.1%}"
                        # Compare with previous period
                        prev_groundedness = feedback_df[feedback_df['NAME'] == 'Groundedness']['MIN_SCORE'].iloc[0]
                        delta_groundedness = groundedness - prev_groundedness
                        st.metric("🎯 Groundedness",
                                  groundedness_display,
                                  delta=f"{delta_groundedness:+.1%}" if delta_groundedness else None)
                    except (KeyError, IndexError):
                        st.metric("🎯 Groundedness", "N/A")

            with col4:
                try:
                    relevance = feedback_df[feedback_df['NAME'] == 'Context Relevance']['AVG_SCORE'].iloc[0]
                    relevance_display = f"{relevance:.1%}"
                    # Compare with previous period
                    prev_relevance = feedback_df[feedback_df['NAME'] == 'Context Relevance']['MIN_SCORE'].iloc[0]
                    delta_relevance = relevance - prev_relevance
                    st.metric("🎖️ Context Relevance",
                              relevance_display,
                              delta=f"{delta_relevance:+.1%}" if delta_relevance else None)
                except (KeyError, IndexError):
                    st.metric("🎖️ Context Relevance", "N/A")

        except Exception as e:
            st.error(f"Error loading metrics: {str(e)}")

    def create_quality_metrics_tab(self):
        """Create the quality metrics tab with enhanced visuals"""
        st.header("📈 Quality Metrics Analysis")

        try:
            feedback_df = get_feedback_metrics()

            # Add a quality score summary card
            st.markdown("""
            <div style='padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6; margin-bottom: 1rem'>
                <h3 style='margin: 0 0 0.5rem 0'>🎯 Quality Score Summary</h3>
                <p style='margin: 0'>Analyzing response quality across multiple dimensions</p>
            </div>
            """, unsafe_allow_html=True)

            # Create bar chart for feedback scores
            fig = px.bar(
                feedback_df,
                x='NAME',
                y='AVG_SCORE',
                error_y=feedback_df['MAX_SCORE'] - feedback_df['AVG_SCORE'],
                error_y_minus=feedback_df['AVG_SCORE'] - feedback_df['MIN_SCORE'],
                title="📊 Feedback Scores Distribution",
                labels={
                    'NAME': 'Metric Type',
                    'AVG_SCORE': 'Score',
                    'QUERY_COUNT': 'Number of Queries'
                },
                color='NAME',
            )
            fig.update_layout(
                title_x=0.5,
                title_font_size=20,
                showlegend=True,
                legend_title_text="Metric Types"
            )
            st.plotly_chart(fig, use_container_width=True, key=f"{uuid.uuid4()}")

            # Show detailed metrics in an expander
            with st.expander("📋 View Detailed Quality Metrics"):
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

    def create_cost_analysis_tab(self):
        """Create the cost analysis tab with enhanced visuals"""
        st.header("💰 Cost Analysis Dashboard")

        try:
            cost_df = get_cost_metrics()

            # Add a cost summary card
            total_cost = cost_df['COST'].sum()
            total_tokens = cost_df['TOKENS'].sum()

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div style='padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6'>
                    <h3 style='margin: 0'>💵 Total Cost</h3>
                    <p style='font-size: 24px; margin: 0.5rem 0'>${total_cost:.2f}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style='padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6'>
                    <h3 style='margin: 0'>🔤 Total Tokens</h3>
                    <p style='font-size: 24px; margin: 0.5rem 0'>{total_tokens:,.0f}</p>
                </div>
                """, unsafe_allow_html=True)

            # Cost trends
            st.subheader("📈 Cost Trends")
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
            fig1.update_layout(title_x=0.5)
            st.plotly_chart(fig1, use_container_width=True)

            # Token usage breakdown
            st.subheader("📊 Token Usage Analysis")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name='🔵 Prompt Tokens',
                x=cost_df['TIME'],
                y=cost_df['PROMPT_TOKENS'],
            ))
            fig2.add_trace(go.Bar(
                name='🟢 Completion Tokens',
                x=cost_df['TIME'],
                y=cost_df['COMPLETION_TOKENS'],
            ))
            fig2.update_layout(
                barmode='stack',
                title='Token Usage Breakdown Over Time',
                title_x=0.5,
                xaxis_title='Time',
                yaxis_title='Number of Tokens'
            )
            st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating cost metrics visualization: {str(e)}")

    def create_performance_metrics_tab(self):
        """Create the performance metrics tab with enhanced visuals"""
        st.header("⚡ Performance Analysis")

        try:
            latency_df = get_latency_metrics()
            if not latency_df.empty:
                # Add performance summary
                avg_latency = latency_df['AVG_LATENCY'].mean()
                max_latency = latency_df['MAX_LATENCY'].max()
                total_requests = latency_df['REQUEST_COUNT'].sum()

                # Create three columns for summary metrics
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
                st.subheader("📈 Response Time Analysis")
                fig = px.area(
                    latency_df,
                    x='TIME',
                    y=["MIN_LATENCY", "AVG_LATENCY", "MAX_LATENCY"],
                    title='Response Time Distribution Over Time',
                    labels={
                        'TIME': 'Time',
                        'value': 'Latency (seconds)',
                        'variable': 'Metric Type'
                    }
                )
                fig.update_layout(title_x=0.5)
                st.plotly_chart(fig, use_container_width=True)

                # Request volume analysis
                st.subheader("📊 Request Volume Analysis")
                fig2 = px.line(
                    latency_df,
                    x='TIME',
                    y='REQUEST_COUNT',
                    title='Request Volume Trends',
                    labels={
                        'TIME': 'Time',
                        'REQUEST_COUNT': 'Number of Requests'
                    }
                )
                fig2.update_layout(title_x=0.5)
                st.plotly_chart(fig2, use_container_width=True)

            else:
                st.info("🔍 No performance data available yet.")

        except Exception as e:
            st.error(f"Error creating performance metrics visualization: {str(e)}")

    def create_model_evaluation_tab(self):
        """Create the model evaluation comparison tab"""
        st.header("🔬 Model Evaluation")

        st.markdown("""
        <div style='padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6; margin-bottom: 1rem'>
            <h3 style='margin: 0 0 0.5rem 0'>🎯 Model Configuration Comparison</h3>
            <p style='margin: 0'>Compare different RAG configurations and their performance metrics</p>
        </div>
        """, unsafe_allow_html=True)

        try:
            eval_df = get_model_evaluation_metrics()
            config_df = get_configuration_details()

            if eval_df.empty:
                st.info(
                    "No evaluation data available yet. Run evaluations with different configurations to see comparison.")
                return

            eval_tab1, eval_tab2, eval_tab3 = st.tabs([
                "📊 Quality Metrics",
                "⚡ Performance Metrics",
                "💰 Cost Analysis"
            ])

            with eval_tab1:
                st.subheader("Quality Metrics by Configuration")

                # Radar chart for quality metrics
                fig = go.Figure()
                for idx, row in eval_df.iterrows():
                    fig.add_trace(go.Scatterpolar(
                        r=[
                            row['AVG_GROUNDEDNESS'] * 100,
                            row['AVG_CONTEXT_RELEVANCE'] * 100,
                            row['AVG_ANSWER_RELEVANCE'] * 100
                        ],
                        theta=['Groundedness', 'Context Relevance', 'Answer Relevance'],
                        name=f"Config {row['APP_ID']}"
                    ))

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=True,
                    title="Quality Metrics Comparison"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Show detailed metrics table
                st.markdown("### Detailed Quality Metrics")
                quality_df = eval_df[
                    ['APP_ID', 'AVG_GROUNDEDNESS', 'AVG_CONTEXT_RELEVANCE', 'AVG_ANSWER_RELEVANCE']].copy()
                quality_df.columns = ['Configuration', 'Groundedness', 'Context Relevance', 'Answer Relevance']

                # Format percentages
                for col in ['Groundedness', 'Context Relevance', 'Answer Relevance']:
                    quality_df[col] = quality_df[col].apply(lambda x: f"{x * 100:.2f}%")

                st.dataframe(quality_df)

            with eval_tab2:
                st.subheader("Response Time Analysis")

                # Performance visualization
                fig = px.bar(
                    eval_df,
                    x='APP_ID',
                    y='AVG_LATENCY',
                    title='Average Response Time by Configuration',
                    labels={
                        'APP_ID': 'Configuration',
                        'AVG_LATENCY': 'Average Response Time (s)'
                    },
                    color='APP_ID'
                )
                st.plotly_chart(fig, use_container_width=True)

                # Query volume visualization
                fig = px.bar(
                    eval_df,
                    x='APP_ID',
                    y='TOTAL_QUERIES',
                    title='Total Queries by Configuration',
                    labels={
                        'APP_ID': 'Configuration',
                        'TOTAL_QUERIES': 'Number of Queries'
                    },
                    color='APP_ID'
                )
                st.plotly_chart(fig, use_container_width=True)

                # Performance metrics table
                st.markdown("### Detailed Performance Metrics")
                perf_df = eval_df[['APP_ID', 'AVG_LATENCY', 'TOTAL_QUERIES']].copy()
                perf_df.columns = ['Configuration', 'Avg Response Time (s)', 'Total Queries']
                perf_df['Avg Response Time (s)'] = perf_df['Avg Response Time (s)'].apply(lambda x: f"{x:.2f}s")
                st.dataframe(perf_df)

            with eval_tab3:
                st.subheader("Cost Analysis")

                # Cost visualization
                fig = px.bar(
                    eval_df,
                    x='APP_ID',
                    y='AVG_COST',
                    title='Average Cost per Query by Configuration',
                    labels={
                        'APP_ID': 'Configuration',
                        'AVG_COST': 'Average Cost per Query ($)'
                    },
                    color='APP_ID'
                )
                st.plotly_chart(fig, use_container_width=True)

                # Cost summary table
                st.markdown("### Cost Summary")
                summary_df = eval_df[['APP_ID', 'TOTAL_QUERIES', 'AVG_COST']].copy()
                summary_df['total_cost'] = summary_df['TOTAL_QUERIES'] * summary_df['AVG_COST']
                summary_df.columns = ['Configuration', 'Total Queries', 'Avg Cost per Query', 'Total Cost']
                st.dataframe(
                    summary_df,
                    column_config={
                        'Total Cost': st.column_config.NumberColumn(
                            'Total Cost',
                            format="$%.2f"
                        ),
                        'Avg Cost per Query': st.column_config.NumberColumn(
                            'Avg Cost per Query',
                            format="$%.4f"
                        )
                    }
                )

            # Configuration Details Section
            st.markdown("### Configuration Details")
            if not config_df.empty:
                with st.expander("View Configuration Details"):
                    st.dataframe(config_df)
            else:
                st.info("No configuration details available in TAGS")

        except Exception as e:
            st.error(f"Error creating model evaluation visualization: {str(e)}")
            st.write("Debug info:")
            if 'eval_df' in locals():
                st.write("Available columns:", eval_df.columns.tolist())
                st.write("Data sample:", eval_df.head())