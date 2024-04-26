output "service_account_email" {
  value = google_service_account.service_account.email
}

output "service_account_id" {
  value = google_service_account.service_account.account_id
}

output "service_account_member" {
  value = google_service_account.service_account.member
}
