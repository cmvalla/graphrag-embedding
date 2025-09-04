import functions_framework
import logging
import sys
import os
import google.generativeai as genai
import asyncio

# --- Boilerplate and Configuration ---
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the generative AI library
# The API key should be provided via an environment variable or Secret Manager
# For Cloud Functions, it's often automatically handled if the service account has permissions
# or if an API key is explicitly set as an environment variable.
# In a production environment, use Secret Manager.
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Initialize the client globally to reuse connections
_genai_client = None

@functions_framework.http
def embed(request):
    global _genai_client

    if _genai_client is None:
        logging.info("Initializing genai client...")
        _genai_client = genai.Client()
        logging.info("genai client initialized successfully.")

    request_json = request.get_json(silent=True)
    if not request_json or 'text' not in request_json:
        logging.error("Bad Request: Missing 'text' in request body")
        return 'Bad Request: Missing "text" in request body', 400

    text_to_embed = request_json['text']
    logging.info(f"Received text for embedding: {text_to_embed}")

    embedding = None
    try:
        # Explicitly create and set an event loop for the current thread
        # This is a workaround for grpcio/asyncio issues in some environments
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # The embed_content call itself is synchronous, but its internal dependencies might be async
        response = _genai_client.models.embed_content(
            model="gemini-embedding-001",
            contents=[text_to_embed],
            task_type="RETRIEVAL_QUERY" # Specify task type as recommended in docs
        )
        embedding = response.embeddings[0]
    except Exception as e:
        logging.error(f"Failed to generate embedding: {e}", exc_info=True)
        return "Failed to generate embedding.", 500
    finally:
        # Clean up the event loop if it was created in this function
        if 'loop' in locals() and not loop.is_running():
            loop.close()


    logging.info(f"Generated embedding: {embedding}")

    return {'embedding': embedding}, 200
