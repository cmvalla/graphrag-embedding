import functions_framework
import logging
import sys
import os
import asyncio
from sentence_transformers import SentenceTransformer
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# --- Boilerplate and Configuration ---
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

embedding_model = None
gemini_embeddings_client = None

@functions_framework.http
def embed(request):
    global embedding_model, gemini_embeddings_client

    request_json = request.get_json(silent=True)
    if not request_json or 'text' not in request_json:
        logging.error("Bad Request: Missing 'text' in request body")
        return 'Bad Request: Missing "text" in request body', 400

    text_to_embed = request_json['text']
    embedding_source = request_json.get('embedding_source', 'gemini') # 'local' or 'gemini', defaults to 'gemini'

    if embedding_source == 'local':
        if embedding_model is None:
            logging.info("Loading local embedding model...")
            embedding_model = SentenceTransformer('/app/model', device='cpu')
            logging.info("Local embedding model loaded successfully.")
    elif embedding_source == 'gemini':
        if gemini_embeddings_client is None:
            logging.info("Initializing Gemini Embeddings client...")
            gemini_embeddings_client = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            logging.info("Gemini Embeddings client initialized successfully.")
    else:
        logging.error(f"Invalid embedding_source in request body: {embedding_source}. Must be 'local' or 'gemini'.")
        return f"Invalid embedding_source: {embedding_source}", 400

    logging.info(f"Received text for embedding: {text_to_embed} with source: {embedding_source}")

    embedding = None
    if embedding_source == 'local':
        embedding = embedding_model.encode(text_to_embed).tolist()
    elif embedding_source == 'gemini':
        # Run the asynchronous embed_query in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            embedding = loop.run_until_complete(gemini_embeddings_client.embed_query(text_to_embed))
        finally:
            loop.close()

    if embedding is None:
        logging.error("Failed to generate embedding.")
        return "Failed to generate embedding.", 500

    logging.info(f"Generated embedding: {embedding}")

    return {'embedding': embedding}, 200