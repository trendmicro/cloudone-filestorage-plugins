output "workflow_id" {
  value = google_workflows_workflow.fullscan_workflow.id
}

output "workflow_revision" {
  value = google_workflows_workflow.fullscan_workflow.revision_id
}
