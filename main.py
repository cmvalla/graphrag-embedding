import functions_framework
import logging
import sys
import os
import asyncio
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# --- Boilerplate and Configuration ---
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

gemini_embeddings_client = None

@functions_framework.http
def embed(request):
    global gemini_embeddings_client

    if gemini_embeddings_client is None:
        logging.info("Initializing Gemini Embeddings client...")
        gemini_embeddings_client = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        logging.info("Gemini Embeddings client initialized successfully.")

    request_json = request.get_json(silent=True)
    if not request_json or 'text' not in request_json:
        logging.error("Bad Request: Missing 'text' in request body")
        return 'Bad Request: Missing "text" in request body', 400

    text_to_embed = request_json['text']
    logging.info(f"Received text for embedding: {text_to_embed}")

    embedding = None
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
