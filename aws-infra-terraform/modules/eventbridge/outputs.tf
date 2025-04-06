output "eventbridge_schedule_arn" {
  value = aws_scheduler_schedule.this.arn
}

output "scheduler_role_arn" {
  value = aws_iam_role.scheduler_assume_role.arn
}