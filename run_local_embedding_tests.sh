#!/bin/bash

# Your Google Cloud Project ID
GCP_PROJECT_ID="spanner-demo-kid" # Replace with your actual project ID

SERVICE_ACCOUNT_ID="embedding-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_ID}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE_PATH="./${SERVICE_ACCOUNT_ID}-key.json"

echo "Attempting to download key for service account: ${SERVICE_ACCOUNT_EMAIL}"

# Create a new key and download it
gcloud iam service-accounts keys create "${KEY_FILE_PATH}" \
  --iam-account="${SERVICE_ACCOUNT_EMAIL}" \
  --project="${GCP_PROJECT_ID}"

if [ $? -ne 0 ]; then
  echo "Error: Failed to download service account key. Please ensure you have permissions to create keys for ${SERVICE_ACCOUNT_EMAIL} in project ${GCP_PROJECT_ID}."
  exit 1
fi

echo "Key downloaded to: ${KEY_FILE_PATH}"

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
export GOOGLE_APPLICATION_CREDENTIALS="${KEY_FILE_PATH}"
echo "GOOGLE_APPLICATION_CREDENTIALS set to: ${GOOGLE_APPLICATION_CREDENTIALS}"

echo "Running local tests..."
# Run your pytest command
source .venv/bin/activate
/Users/carlovalla/Library/Python/3.9/bin/pytest functions/graphrag-embedding/test_main.py

# Unset the environment variable and delete the key file after tests
echo "Cleaning up..."
unset GOOGLE_APPLICATION_CREDENTIALS
rm "${KEY_FILE_PATH}"

echo "Cleanup complete. Key file deleted."
