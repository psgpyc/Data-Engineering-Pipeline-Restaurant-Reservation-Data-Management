variable "role_name" {
  description = "Name for aws iam role"
  type = string
}

variable "assume_role_policy" {
    description = "Trust relationship policy"
    type = string
  
}

variable "bucket_access_policy" {
  description = "The inline policy JSON that defines permissions"
  type        = string
}
