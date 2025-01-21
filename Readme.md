# CivicSense: AI-Powered Government Policy Assistant

## 🏆 Snowflake x Mistral Hackathon Project

CivicSense is an intelligent chatbot that helps citizens understand government policies and benefits using Retrieval Augmented Generation (RAG) with Snowflake Cortex Search and Mistral LLM.

## 🌟 Features

- **Smart Policy Search**: Uses RAG to provide accurate information from official government documents
- **Source References**: Every response includes links to original policy documents
- **Real-time Performance Monitoring**: Comprehensive analytics dashboard powered by TruLens
- **Quality Assurance**: Automated evaluation of response accuracy and relevance
- **Secure Data Handling**: All data stays within Snowflake's governance framework

## 🛠️ Technology Stack

- **Snowflake Cortex Search**: For efficient document retrieval
- **Mistral LLM (mistral-large2)**: For natural language understanding and generation
- **Streamlit**: For the user interface and dashboard
- **TruLens**: For LLM observability and evaluation
- **Python**: Core application development

## 📊 Performance Metrics

The application is evaluated on multiple dimensions using TruLens:
- Groundedness: Ensuring responses align with source documents
- Context Relevance: Measuring the relevance of retrieved information
- Answer Relevance: Evaluating response quality
- Latency: Monitoring response times
- Cost Analysis: Tracking token usage and associated costs

## 🚀 Getting Started

### Prerequisites
- Snowflake Account with appropriate permissions
- Python 3.11
- Access to Mistral LLM via Snowflake Cortex

### Environment Setup

1. Clone the repository:
```bash
git https://github.com/nirmalmaheshs/CivicSense/
cd CivicSense
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install snowflake-snowpark-python
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file with:
```
SNOWFLAKE_USER=
SNOWFLAKE_USER_PASSWORD=
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_DATABASE=
SNOWFLAKE_SCHEMA=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_ROLE=
SNOWFLAKE_CORTEX_SEARCH_SERVICE=
```

### Running the Application

1. Start the chatbot:
```bash
streamlit run CivicSense.py
```

2. Access the analytics dashboard:
```bash
streamlit run Performance_Metrics.py
```

## 📁 Project Structure

```
civicsense/
├── src/
│   ├── classes/
│   │   ├── base/           # Abstract base classes
│   │   ├── snowflake/      # Snowflake implementations
│   │   └── trulens/        # TruLens evaluators
│   ├── utils/              # Utility functions
│   └── images/             # UI assets
├── CivicSense.py          # Main chatbot application
├── Performance_Metrics.py  # Analytics dashboard
└── requirements.txt       # Project dependencies
```

## 🔍 Key Components

1. **RAG Implementation**
   - Uses Snowflake Cortex Search for document retrieval
   - Implements context-aware response generation
   - Maintains source tracking for references

2. **TruLens Integration**
   - Real-time evaluation of response quality
   - Performance monitoring and metrics collection
   - Cost tracking and optimization

3. **Analytics Dashboard**
   - Real-time performance metrics
   - Quality metrics visualization
   - Cost analysis and tracking
   - Version comparison tools

## 🤝 Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## 🏗️ Built With

- [Snowflake Cortex](https://docs.snowflake.com/en/developer-guide/cortex/index)
- [Streamlit](https://streamlit.io/)
- [TruLens](https://github.com/truera/trulens)
- [Mistral LLM](https://mistral.ai/)

## ✨ Acknowledgments

- Snowflake and Mistral AI for providing the core technologies
- The TruLens team for the evaluation framework
- The Streamlit team for the excellent UI framework