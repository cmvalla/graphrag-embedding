import functions_framework
import logging
import sys
from sentence_transformers import SentenceTransformer

# --- Boilerplate and Configuration ---
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

embedding_model = None

@functions_framework.http
def embed(request):
    global embedding_model
    if embedding_model is None:
        logging.info("Loading embedding model...")
        embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        logging.info("Embedding model loaded successfully.")

    request_json = request.get_json(silent=True)
    if not request_json or 'text' not in request_json:
        logging.error("Bad Request: Missing 'text' in request body")
        return 'Bad Request: Missing "text" in request body', 400

    text_to_embed = request_json['text']
    logging.info(f"Received text for embedding: {text_to_embed}")
    embedding = embedding_model.encode(text_to_embed).tolist()
    logging.info(f"Generated embedding: {embedding}")

    return {'embedding': embedding}, 200