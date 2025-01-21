from src.utils.config import Defaults
from src.utils.dashboard import PerformanceMetrics
import streamlit as st

def set_page_config():
    st.set_page_config(
        page_title=f"{Defaults.APP_NAME} Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def main():
    set_page_config()
    PerformanceMetrics()

if __name__ == "__main__":
    main()