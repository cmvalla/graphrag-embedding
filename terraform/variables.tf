variable "project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "region" {
  description = "The GCP region where the Cloud Run service will be deployed."
  type        = string
}

variable "git_tag" {
  description = "The Git tag for the Docker image."
  type        = string
  default     = "latest"
}

variable "embedding_sa_email" {
  description = "The email of the service account for the embedding service."
  type        = string
}

variable "image_url" {
  description = "The URL of the Docker image."
  type        = string
}

variable "gemini_api_key_secret_id" {
  description = "The Secret Manager ID for the Gemini API key."
  type        = string
}
