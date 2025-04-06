resource "aws_iam_role" "scheduler_assume_role" {
    name = "eventbridge-scheduler-lambda-invoke"
    assume_role_policy = file("${path.module}/policies/event_bridge_assume_role_policy.json")
  
}

resource "aws_iam_policy" "scheduler_access_lambda_permission" {
    name = "eventbridge-scheduler-policy"

    policy = jsonencode({
        Version = "2012-10-17",
        Statement = [
            {
                Effect = "Allow",
                Action = "lambda:InvokeFunction",
                Resource = [
                  "arn:aws:lambda:eu-west-2:897729116490:function:gfaker:*",
                  "arn:aws:lambda:eu-west-2:897729116490:function:gfaker"
            ]

            }
        ]
    })
  
}


resource "aws_iam_role_policy_attachment" "attach_lambda_invoke_policy_to_iam_role" {
    policy_arn = aws_iam_policy.scheduler_access_lambda_permission.arn
    role = aws_iam_role.scheduler_assume_role.name
  
}

resource "aws_scheduler_schedule" "this" {
  name        = var.schedule_name
  description = var.description
  group_name  = "default"

  schedule_expression = var.schedule_expression

  flexible_time_window {
    mode = "OFF"
  }
  
  target {
    arn      = var.lambda_arn
    role_arn = var.scheduler_role_arn
  }
}


