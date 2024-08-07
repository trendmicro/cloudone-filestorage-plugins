resource "google_cloud_scheduler_job" "workflow" {
  project          = var.project_id
  name             = "tm-c1fss-fs-pl-ws-${var.suffix}"
  description      = "Cloud Scheduler for fullscan plugin workflow Job"
  schedule         = var.schedular_settings.cron
  time_zone        = var.schedular_settings.timezone
  attempt_deadline = "1800s"
  region           = var.region

  http_target {
    http_method = "POST"
    uri         = "https://workflowexecutions.googleapis.com/v1/${google_workflows_workflow.fullscan_workflow.id}/executions"
    body = base64encode(
      jsonencode({
        "argument" : jsonencode({
          "bucketName" : "${var.scanning_bucket_name}"
        }),
        "callLogLevel" : "CALL_LOG_LEVEL_UNSPECIFIED"
        }
    ))

    oauth_token {
      service_account_email = var.service_account
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }
}

resource "google_cloud_tasks_queue" "workflow_queue" {
  name     = "tmfss-fullscan-workflow-queue-${var.suffix}"
  location = var.region
}

resource "google_workflows_workflow" "fullscan_workflow" {
  name            = "tmfss-fullscan-workflow-${var.suffix}"
  description     = "trendmicro fss fullscan plugin workflow."
  service_account = var.service_account
  source_contents = <<-EOF
  main:
    params: [args]
    steps:
        - init:
            assign:
                - step_count: 0
                - listResult:
                    assign:
                        - nextPageToken: $${map.get(args, "nextPageToken")}
            next: listObject
        - listObject:
            call: googleapis.storage.v1.objects.list
            args:
                bucket: $${args.bucketName}
                pageToken: $${map.get(listResult, "nextPageToken")}
                maxResults: 500
            result: listResult
        - loopFiles:
            parallel:
                for:
                    value: file
                    in: $${listResult.items}
                    steps:
                        - triggerScan:
                            call: http.post
                            args:
                                url: ${var.scan_trigger_function_url}
                                body:
                                    file: $${file}
                                auth:
                                    type: OIDC
        - increment:
            assign:
                - step_count: $${step_count + 600}
        - checkNextToken:
            switch:
                - condition: $${listResult.nextPageToken != null}
                  next: checkStepsCount
            next: end
        - checkStepsCount:
            switch:
                - condition: $${step_count > 30000}
                  next: createBodyObject
            next: listObject
        - createBodyObject:
            assign:
                - data:
                    bucketName: $${args.bucketName}
                    nextPageToken: $${listResult.nextPageToken}
                - body:
                    argument: $${json.encode_to_string(data)}
            next: startNewExecution
        - startNewExecution:
            call: googleapis.cloudtasks.v2.projects.locations.queues.tasks.create
            args:
                parent: ${google_cloud_tasks_queue.workflow_queue.id}
                body:
                  task:
                    httpRequest:
                      body: '$${base64.encode(json.encode(body))}'
                      url: $${"https://workflowexecutions.googleapis.com/v1/projects/${var.project_id}/locations/${var.region}/workflows/" + sys.get_env("GOOGLE_CLOUD_WORKFLOW_ID") + "/executions"}
                      oauthToken:
                        serviceAccountEmail: ${var.service_account}
            next: end
  EOF
}
