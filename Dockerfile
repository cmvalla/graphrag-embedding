# Use a base image with Python and pip installed
FROM python:3.11-slim as downloader

# Install huggingface_hub
RUN pip install huggingface_hub

# Download the model
RUN huggingface-cli download sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --local-dir /app/model --local-dir-use-symlinks False

# Use a slim Python image for the final application
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY main.py .

# Copy the model from the downloader stage
COPY --from=downloader /app/model /app/model

# Set the entrypoint
CMD exec functions-framework --target=embed --port=8080