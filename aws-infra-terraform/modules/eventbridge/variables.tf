variable "schedule_name" {
    type = string
    description = "Name of the EventBridge Schedule"

}

variable "description" {
    type = string
    description = "Description of the schedule"
    default = "Daily lambda invoker"
  
}

variable "schedule_expression" {
  type        = string
  description = "Cron or rate expression"
}

variable "lambda_arn" {
  type        = string
  description = "ARN of the Lambda function to trigger"
}

variable "scheduler_role_arn" {
  type        = string
  description = "IAM role ARN that EventBridge will assume to invoke Lambda"
}

variable "payload" {
  type        = map(any)
  description = "Payload to pass to the Lambda function"
  default     = {}
}