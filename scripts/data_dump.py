import os
import requests
from lxml import etree
import snowflake.connector
import asyncio
from pyppeteer import launch

# Configuration
SNOWFLAKE_ACCOUNT = ""
SNOWFLAKE_USER = ""
SNOWFLAKE_PASSWORD = ""
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "POLICYVAULT"
SNOWFLAKE_SCHEMA = "CIVICPOLICIES"
STAGE_NAME = "@docs"


def fetch_sitemap_urls(sitemap_url):
    """Fetch URLs from the sitemap."""
    response = requests.get(sitemap_url)
    response.raise_for_status()
    sitemap = etree.fromstring(response.content)
    namespaces = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = sitemap.xpath("//ns:url/ns:loc/text()", namespaces=namespaces)
    return urls


async def generate_pdf(url, pdf_path):
    """Convert a URL to a PDF file."""
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url)
    await page.pdf({"path": pdf_path, "format": "A4"})
    await browser.close()


def upload_file_to_snowflake(file_path, stage_name, conn):
    """Upload a file to a Snowflake stage."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"PUT file://{file_path} {stage_name} OVERWRITE = TRUE AUTO_COMPRESS = FALSE"
        )
    finally:
        cursor.close()


def main(sitemap_url):

    # Step 1: Connect to Snowflake
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
    )

    try:
        # Step 2: Fetch URLs from the sitemap
        urls = fetch_sitemap_urls(sitemap_url)
        print(f"Found {len(urls)} URLs in the sitemap.")

        if not urls:
            print("No URLs found in the sitemap.")
            return

        # Step 3: Process each URL
        for url in urls:
            try:
                # Forming file name based on query param
                file_name = "tmp/" + url.split("=")[-1] + ".pdf"

                # Convert URL to PDF
                print(f"Converting {url} to PDF...")
                asyncio.get_event_loop().run_until_complete(
                    generate_pdf(url, file_name)
                )

                # Upload PDF to Snowflake stage
                print(f"Uploading {file_name} to Snowflake stage...")
                upload_file_to_snowflake(file_name, STAGE_NAME, conn)
                print(f"Uploaded {file_name} successfully.")

            except Exception as e:
                print(f"Failed to process {url}: {e}")
            finally:
                # Clean up the file
                os.remove(file_name)

    finally:
        # Close Snowflake connection
        conn.close()


if __name__ == "__main__":
    SITEMAP_URL = "", "https://www.dhs.state.il.us/sitemap.xml"
    main(SITEMAP_URL)
