# GraphRAG Embedding Function Usage

This document describes how to use the GraphRAG Embedding function, its parameters, request and response structures.

## Endpoint

The function is exposed as an HTTP POST endpoint.

## Request Structure

The request body must be a JSON object with the following structure:

```json
{
  "texts": [
    "string",
    "string",
    ...
  ],
  "task_type": "string"
}
```

### Parameters

*   `texts` (array of strings, **required**): A list of text strings for which embeddings are to be generated.
*   `task_type` (string, **optional**): Specifies the task type for the embeddings. This influences how the embeddings are generated and can improve performance for specific use cases.
    *   Supported values (as of current implementation):
        *   `retrieval_document`: For embedding documents that will be retrieved.
        *   `retrieval_query`: For embedding queries that will be used to retrieve documents.
    *   If not provided, a default or general-purpose embedding might be used, but specifying it is recommended for optimal results.

## Response Structure

The response body will be a JSON object with the following structure:

```json
{
  "embeddings": {
    "semantic_search": [
      [float, float, ...],
      [float, float, ...],
      ...
    ]
  }
}
```

### Response Fields

*   `embeddings` (object): An object containing the generated embeddings.
    *   `semantic_search` (array of arrays of floats): A list of embedding vectors. Each inner array represents the embedding for the corresponding text string in the request. The dimension of each vector depends on the embedding model used.

## Example Request

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "texts": ["This is a sample text.", "Another text for embedding."],
  "task_type": "retrieval_document"
}' http://your-function-url/
```

## Example Response

```json
{
  "embeddings": {
    "semantic_search": [
      [0.123, 0.456, ..., 0.789],
      [0.987, 0.654, ..., 0.321]
    ]
  }
}
```