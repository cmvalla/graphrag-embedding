resource "google_cloud_run_v2_service" "embedding_service" {
  name     = "graphrag-embedding"
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = "europe-west1-docker.pkg.dev/${var.project_id}/my-docker-repo/graphrag-embedding:${var.git_tag}"
      ports {
        container_port = 8080
      }
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
      env {
        name = "GEMINI_API_KEY_SECRET_ID"
        value = var.gemini_api_key_secret_id
      }
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
    }
    scaling {
      max_instance_count = 5
    }
    service_account = var.embedding_sa_email
    timeout = "300s"
    
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  ingress = "INGRESS_TRAFFIC_ALL"

  depends_on = [
    google_project_service.run_api,
  ]
}

resource "google_project_service" "run_api" {
  project = var.project_id
  service = "run.googleapis.com"
  disable_on_destroy = false
}
