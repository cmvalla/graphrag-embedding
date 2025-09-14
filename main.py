import functions_framework
import logging
import sys
import os
import google.generativeai as genai
from langchain_community.embeddings import SentenceTransformerEmbeddings, HuggingFaceEmbeddings, CohereEmbeddings

class TaskType:
    RETRIEVAL_DOCUMENT = "retrieval_document"
    RETRIEVAL_QUERY = "retrieval_query"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    QUESTION_ANSWERING = "question_answering"
    FACT_VERIFICATION = "fact_verification"
    CODE_RETRIEVAL_QUERY = "code_retrieval_query"


EMBEDDING_DIMENSION = 768 # Default embedding dimension for models/embedding-001
import requests
import google.cloud.secretmanager as secretmanager

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

# Initialize Secret Manager client globally
sm_client = secretmanager.SecretManagerServiceClient()

# Configure the generative AI library
# The API key will be fetched from Secret Manager
GEMINI_API_KEY_SECRET_ID = os.environ.get("GEMINI_API_KEY_SECRET_ID")
if GEMINI_API_KEY_SECRET_ID:
    try:
        gemini_api_key = sm_client.access_secret_version(request={"name": GEMINI_API_KEY_SECRET_ID}).payload.data.decode("UTF-8")
        genai.configure(api_key=gemini_api_key)
        logging.debug("Gemini API key fetched from Secret Manager and configured.")
    except Exception as e:
        logging.error(f"Failed to fetch Gemini API key from Secret Manager: {e}", exc_info=True)
        # Fallback to environment variable if secret access fails
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        logging.warning("Falling back to GEMINI_API_KEY from environment variable.")
else:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    logging.warning("GEMINI_API_KEY_SECRET_ID not set. Falling back to GEMINI_API_KEY from environment variable.")

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

    # Get desired embedding types from request, default to ["semantic_search"]
    # This allows requesting multiple types of embeddings in one call
    embedding_types_requested = request_json.get('embedding_types', ["semantic_search"])
    if not isinstance(embedding_types_requested, list):
        logging.error("Bad Request: 'embedding_types' must be a list.")
        return 'Bad Request: \'embedding_types\' must be a list.', 400

    # Define mapping from requested embedding type to genai.TaskType
    TASK_TYPE_MAPPING = {
        "clustering": TaskType.CLUSTERING,
        "semantic_search": TaskType.RETRIEVAL_DOCUMENT,
        "semantic_query": TaskType.RETRIEVAL_QUERY,
        # Add other mappings as needed
    }

    all_embeddings = {}
    for embed_type in embedding_types_requested:
        task_type = TASK_TYPE_MAPPING.get(embed_type)
        if task_type is None:
            logging.warning(f"Unknown embedding type requested: {embed_type}. Skipping.")
            continue

        logging.debug(f"Texts to embed for {embed_type}: {texts_to_embed}")
        logging.debug(f"Task type for {embed_type}: {task_type}")

        try:
            logging.debug(f"Calling genai.embed_content for {embed_type}...")
            response = genai.embed_content(
                model="models/embedding-001",
                content=texts_to_embed,
                task_type=task_type
            )
            logging.debug(f"Response from genai.embed_content for {embed_type}: {response}")
            
            # The 'embedding' key in the response from genai.embed_content is always singular
            # and contains a list of embeddings (one for each text in content).
            embeddings_list = response['embedding'] 
            all_embeddings[embed_type] = embeddings_list
            logging.debug(f"Extracted {len(embeddings_list)} embeddings for {embed_type}.")
        except Exception as e:
            logging.error(f"Failed to generate {embed_type} embedding: {e}", exc_info=True)
            # Continue to try other embedding types even if one fails
            all_embeddings[embed_type] = [[0.0] * EMBEDDING_DIMENSION] * len(texts_to_embed) # Return zero embeddings for failed type

    if not all_embeddings:
        logging.error("No embeddings could be generated for any requested type.")
        return "No embeddings could be generated.", 500

    logging.debug(f"Generated all embeddings: {all_embeddings}")
    logging.debug("Returning response.")

    return {'embeddings': all_embeddings}, 200

