# config.py
class Defaults:
    APP_NAME = "CivicSense"
    APP_VERSION = "1.0"
    LLM_MODEL= "mistral-large"
    LLM_RETRIEVE_CHUNK_SIZE=4
    SITE_DOMAIN_PREFIX= "https://www.dhs.state.il.us/page.aspx?item="

    # Dashboard refresh settings
    DASHBOARD_REFRESH_RATE = 300  # refresh every 5 minutes
    DASHBOARD_MAX_DATAPOINTS = 1000  # maximum number of datapoints to show

def load_llm_config():
    llm_config = dict()
    llm_config['retriever_chunk_size'] = Defaults.LLM_RETRIEVE_CHUNK_SIZE
    llm_config['app_name'] = Defaults.APP_NAME
    llm_config['app_version'] = Defaults.APP_VERSION
    llm_config['llm_model'] = Defaults.LLM_MODEL
    return llm_config