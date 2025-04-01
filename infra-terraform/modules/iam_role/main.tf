resource "aws_iam_role" "this" {
    # creates an IAM role
    name = var.role_name
    assume_role_policy = var.assume_role_policy

    tags = {
        Name = var.role_name
        Environment = "dev"
    }
}


resource "aws_iam_policy" "this" {
    # cretes a seperate policy
    name = "${var.role_name}-policy"
    description = "Policy for ${var.role_name}"
    policy = var.bucket_access_policy
  
}

resource "aws_iam_role_policy_attachment" "this" {
    # attaches the above policy to the role
    role = aws_iam_role.this.name
    policy_arn = aws_iam_policy.this.arn

}

