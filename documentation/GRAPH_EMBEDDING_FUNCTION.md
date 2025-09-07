# GraphRAG Embedding Function Documentation

This document describes the `graphrag-embedding` Cloud Function, its purpose, how it works, and how to interact with it.

## 1. Purpose

The `graphrag-embedding` function is responsible for generating high-quality vector embeddings for textual data. These embeddings are crucial for various downstream tasks in the GraphRAG pipeline, such as similarity search, clustering, and graph analysis. It leverages Google's Gemini embedding models for state-of-the-art performance.

## 2. Location

The source code for this function is located at: `functions/graphrag-embedding/`

## 3. Technology Stack

*   **Runtime:** Python 3.11
*   **Platform:** Google Cloud Run (deployed as a serverless container)
*   **Embedding Model:** Google Gemini (`models/embedding-001`)
*   **Client Library:** `google.generativeai`

## 4. Functionality and Usage

The `embed` function is exposed as an HTTP endpoint and accepts POST requests with a JSON body.

### Input (Request Body)

The request body should be a JSON object containing one of the following:

*   `text` (string): A single text string for which to generate an embedding.
*   `texts` (array of strings): A list of text strings for which to generate embeddings.

Additionally, you can optionally include:

*   `task_type` (string, optional): Specifies the task type for the embedding. This helps the model generate more relevant embeddings for your use case. The `models/embedding-001` model supports the following task types:
    *   `RETRIEVAL_QUERY`: Use for embedding queries that will be used to retrieve relevant documents.
    *   `RETRIEVAL_DOCUMENT`: Use for embedding documents that will be retrieved by queries.
    *   `SEMANTIC_SIMILARITY`: Use for general semantic similarity tasks, where the embeddings are used to compare the similarity between two pieces of text.
    *   `CLASSIFICATION`: Use for embedding text that will be used for classification tasks.
    *   `CLUSTERING`: Use for embedding text that will be used for clustering tasks.
    *   `QUESTION_ANSWERING`: Use for embedding text that will be used in question-answering systems.
    *   `FACT_VERIFICATION`: Use for embedding text that will be used for fact verification.
    *   `OTHER`: Use for tasks not covered by the above types.

### Output (Response Body)

The response will be a JSON object containing:

*   `embedding` (array of floats): If a single `text` was provided in the request, this field will contain the generated vector embedding as a list of floating-point numbers.
*   `embeddings` (array of arrays of floats): If a `texts` array was provided, this field will contain an array of vector embeddings, where each inner array corresponds to the embedding of the respective text in the input `texts` array.

### Error Handling

In case of an error (e.g., missing input, API issues), the function will return an appropriate HTTP status code (e.g., `400 Bad Request`, `500 Internal Server Error`) and a descriptive error message in the response body.

## 5. Authentication

The `graphrag-embedding` function authenticates with the Gemini API using an API key. This API key is securely stored in Google Secret Manager and is accessed programmatically by the function's service account (`embedding-sa`).

**Required IAM Role:** The `embedding-sa` service account must have the `roles/secretmanager.secretAccessor` role for the `gemini-api-key` secret and the `roles/aiplatform.user` role to interact with the Gemini API.

## 6. Deployment

This function is deployed as a Google Cloud Run service. Its infrastructure and configuration are managed using Terraform. Key deployment parameters include:

*   **Image:** The Docker image for the function is built and pushed to Google Artifact Registry via Cloud Build.
*   **Service Account:** The `embedding-sa` service account is attached to the Cloud Run service.
*   **Resource Limits:** The service is configured with specific CPU and memory limits to optimize cost and performance.
    *   **CPU:** 1 CPU
    *   **Memory:** 512Mi

## 7. Example Usage (using `curl`)

Replace `YOUR_FUNCTION_URL` with the actual URL of your deployed `graphrag-embedding` Cloud Function.

### Embed a single text

```bash
curl -X POST YOUR_FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{"text": "The quick brown fox jumps over the lazy dog.", "task_type": "RETRIEVAL_QUERY"}'
```

### Embed multiple texts

```bash
curl -X POST YOUR_FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello world.", "How are you today?"], "task_type": "SEMANTIC_SIMILARITY"}'
```
