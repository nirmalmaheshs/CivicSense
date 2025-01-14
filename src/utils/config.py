# config.py
class Defaults:
    APP_NAME = "CivicSense"
    APP_VERSION = "1.0"
    LLM_MODEL= "mistral-large2"
    SITE_DOMAIN_PREFIX= "https://www.dhs.state.il.us/page.aspx?item="

    # Dashboard refresh settings
    DASHBOARD_REFRESH_RATE = 300  # refresh every 5 minutes
    DASHBOARD_MAX_DATAPOINTS = 1000  # maximum number of datapoints to show