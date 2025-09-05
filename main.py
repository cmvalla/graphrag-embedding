import functions_framework
import logging
import sys
import os
import google.generativeai as genai
import requests

# --- Boilerplate and Configuration ---
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the generative AI library
# The API key should be provided via an environment variable or Secret Manager
# For Cloud Functions, it's often automatically handled if the service account has permissions
# or if an API key is explicitly set as an environment variable.
# In a production environment, use Secret Manager.

# Get GCP_PROJECT from environment variables
GCP_PROJECT = "spanner-demo-kid"

# Configure genai with the project_id
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

    if not request_json or 'text' not in request_json:
        logging.error("Bad Request: Missing 'text' in request body")
        return 'Bad Request: Missing "text" in request body', 400

    text_to_embed = request_json['text']
    logging.debug(f"Text to embed: {text_to_embed}")

    try:
        logging.debug("Calling genai.embed_content...")
        # The endpoint used by google.generativeai is usually inferred or default.
        # It's not directly exposed as a configurable parameter in embed_content.
        # However, we can log the model name being used.
        logging.debug(f"Embedding model: models/embedding-001")
        response = genai.embed_content(
            model="models/embedding-001",
            content=text_to_embed,
            task_type="RETRIEVAL_QUERY" # Specify task type as recommended in docs
        )
        logging.debug(f"Response from genai.embed_content: {response}")
        embedding = response['embedding']
        logging.debug(f"Extracted embedding: {embedding}")
    except Exception as e:
        logging.error(f"Failed to generate embedding: {e}", exc_info=True)
        return "Failed to generate embedding.", 500

    logging.debug(f"Generated embedding: {embedding}")
    logging.debug("Returning response.")

    return {'embedding': embedding}, 200