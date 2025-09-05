import functions_framework
import logging
import sys
import os
import google.generativeai as genai
import requests

# --- Boilerplate and Configuration ---

LOG_LEVEL_MAP = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}

# Get log level from environment variable, default to DEBUG
log_level_str = os.environ.get("LOG_LEVEL", "DEBUG").upper()
log_level = LOG_LEVEL_MAP.get(log_level_str, logging.DEBUG)

logging.basicConfig(level=log_level, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the generative AI library
GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"), project=GCP_PROJECT)

@functions_framework.http
def embed(request):
    logging.debug("Received request.")
    
    # Log environment variables related to project and credentials
    logging.debug(f'GOOGLE_CLOUD_PROJECT: {os.environ.get("GOOGLE_CLOUD_PROJECT")}')
    logging.debug(f'GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")}')

    # Attempt to retrieve and log the service account email from the metadata server
    try:
        metadata_server_url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email"
        headers = {"Metadata-Flavor": "Google"}
        response = requests.get(metadata_server_url, headers=headers, timeout=1)
        if response.status_code == 200:
            logging.debug(f"Running as service account: {response.text}")
        else:
            logging.debug(f"Could not retrieve service account email from metadata server. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.debug(f"Error retrieving service account email from metadata server: {e}")

    request_json = request.get_json(silent=True)
    logging.debug(f"Request JSON: {request_json}")

    if not request_json:
        logging.error("Bad Request: Request body is empty.")
        return 'Bad Request: Request body is empty.', 400

    # Determine if input is a single text or an array of texts
    if 'text' in request_json:
        texts_to_embed = [request_json['text']]
    elif 'texts' in request_json and isinstance(request_json['texts'], list):
        texts_to_embed = request_json['texts']
    else:
        logging.error("Bad Request: Missing 'text' or 'texts' in request body.")
        return 'Bad Request: Missing "text" or "texts" in request body.', 400

    # Get task_type from request, default to RETRIEVAL_QUERY
    task_type = request_json.get('task_type', "RETRIEVAL_QUERY")

    logging.debug(f"Texts to embed: {texts_to_embed}")
    logging.debug(f"Task type: {task_type}")

    try:
        logging.debug("Calling genai.embed_content...")
        response = genai.embed_content(
            model="models/embedding-001",
            contents=texts_to_embed,
            task_type=task_type
        )
        logging.debug(f"Response from genai.embed_content: {response}")
        embeddings = response['embedding']
        logging.debug(f"Extracted embeddings: {embeddings}")
    except Exception as e:
        logging.error(f"Failed to generate embedding: {e}", exc_info=True)
        return "Failed to generate embedding.", 500

    logging.debug(f"Generated embeddings: {embeddings}")
    logging.debug("Returning response.")

    return {'embeddings': embeddings}, 200