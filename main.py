import functions_framework
import logging
import sys
import os
import google.generativeai as genai

# --- Boilerplate and Configuration ---
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the generative AI library
# The API key should be provided via an environment variable or Secret Manager
# For Cloud Functions, it's often automatically handled if the service account has permissions
# or if an API key is explicitly set as an environment variable.
# In a production environment, use Secret Manager.
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Initialize the client globally to reuse connections
client = genai.Client()

@functions_framework.http
def embed(request):
    request_json = request.get_json(silent=True)
    if not request_json or 'text' not in request_json:
        logging.error("Bad Request: Missing 'text' in request body")
        return 'Bad Request: Missing "text" in request body', 400

    text_to_embed = request_json['text']
    logging.info(f"Received text for embedding: {text_to_embed}")

    try:
        # Use client.models.embed_content as requested
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=[text_to_embed],
            task_type="RETRIEVAL_QUERY" # Specify task type as recommended in docs
        )
        embedding = response.embeddings[0]
    except Exception as e:
        logging.error(f"Failed to generate embedding: {e}", exc_info=True)
        return "Failed to generate embedding.", 500

    logging.info(f"Generated embedding: {embedding}")

    return {'embedding': embedding}, 200
