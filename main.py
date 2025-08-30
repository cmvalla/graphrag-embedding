import functions_framework
import logging
from sentence_transformers import SentenceTransformer

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
        return 'Bad Request: Missing "text" in request body', 400

    text_to_embed = request_json['text']
    embedding = embedding_model.encode(text_to_embed).tolist()

    return {'embedding': embedding}, 200