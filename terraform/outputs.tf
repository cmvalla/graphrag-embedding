output "embedding_service_url" {
  description = "The URL of the deployed embedding service."
  value       = google_cloud_run_v2_service.embedding_service.uri
}
