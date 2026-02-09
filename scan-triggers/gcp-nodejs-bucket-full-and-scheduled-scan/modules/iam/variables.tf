variable "name" {
  type = string
}

variable "id" {
  type = string
}

variable "description" {
  type = string
}

variable "roles" {
  type = map(object({
    name    = string
    project = string
  }))
}
