import pytest
import os
from unittest.mock import MagicMock, patch
from main import embed # Assuming main.py is in the same directory

# Mock the os.environ.get for GEMINI_API_KEY
@pytest.fixture(autouse=True)
def mock_env_vars():
    # For integration test, ensure a real API key is available
    # In a real scenario, you'd set this environment variable before running tests
    if "GEMINI_API_KEY" not in os.environ:
        pytest.skip("GEMINI_API_KEY environment variable not set for integration test.")
    yield

# Mock the functions_framework.http.Request object
@pytest.fixture
def mock_request():
    mock_req = MagicMock()
    mock_req.get_json.return_value = {"text": "test text"}
    return mock_req

def test_embed_single_text_integration(mock_request):
    # Test with single text input
    mock_request.get_json.return_value = {"text": "single test text"}
    response, status_code = embed(mock_request)
    assert status_code == 200
    assert "embeddings" in response
    assert isinstance(response["embeddings"], list)
    assert len(response["embeddings"]) == 1
    assert isinstance(response["embeddings"][0], list) # Embedding is a list of floats
    assert len(response["embeddings"][0]) > 0
    assert isinstance(response["embeddings"][0][0], float)

def test_embed_array_texts_integration(mock_request):
    # Test with array of texts input
    mock_request.get_json.return_value = {"texts": ["first text", "second text"]}
    response, status_code = embed(mock_request)
    assert status_code == 200
    assert "embeddings" in response
    assert isinstance(response["embeddings"], list)
    assert len(response["embeddings"]) == 2
    assert isinstance(response["embeddings"][0], list)
    assert isinstance(response["embeddings"][1], list)

def test_embed_with_task_type_integration(mock_request):
    # Test with task_type specified
    mock_request.get_json.return_value = {"text": "task type test", "task_type": "SEMANTIC_SIMILARITY"}
    response, status_code = embed(mock_request)
    assert status_code == 200
    assert "embeddings" in response
    assert isinstance(response["embeddings"], list)
    assert len(response["embeddings"]) == 1

def test_embed_missing_input(mock_request):
    mock_request.get_json.return_value = {} # Missing 'text' or 'texts'
    response, status_code = embed(mock_request)
    assert status_code == 400
    assert response == "Bad Request: Missing \"text\" or \"texts\" in request body."

def test_embed_genai_error_mocked(mock_request):
    # This test will still mock the genai.embed_content to simulate an error
    # as we don't want to rely on a real API error for this specific test case.
    with patch("google.generativeai.embed_content") as mock_embed_content:
        mock_embed_content.side_effect = Exception("GENAI Error")
        response, status_code = embed(mock_request)
        assert status_code == 500
        assert "Failed to generate embedding." in response