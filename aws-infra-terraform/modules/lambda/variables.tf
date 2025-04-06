variable "i_am_role_name" {
    type = string
  
}

variable "lambda_assume_role_policy" {
    type = string
}


variable "lambda_cloudwatch_access_policy" {
    type = string
  
}

variable "lambda_bucket_access_policy" {
    type = string
  
}

variable "eventbridge_schedule_arn" {
  description = "ARN of the EventBridge schedule that triggers this Lambda"
  type        = string
}