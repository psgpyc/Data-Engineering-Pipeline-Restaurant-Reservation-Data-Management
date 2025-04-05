resource "aws_iam_role" "this" {
    name = var.i_am_role_name
    assume_role_policy = var.lambda_assume_role_policy

    tags = {
      Name = "pipeline"
    }
  
}

resource "aws_iam_policy" "cloudwatch-access" {
    name = "${aws_iam_role.this.name}-policy"
    policy = var.lambda_cloudwatch_access_policy

    tags = {
        Name = "pipeline"
    }
  
}

resource "aws_iam_policy" "bucket-access" {
    name = "${aws_iam_role.this.name}-bucket-access-policy"
    policy = var.lambda_bucket_access_policy

    tags = {
        Name = "pipeline"
    }
  
}


resource "aws_iam_policy_attachment" "attach-cloudwatch-policy" {
    name = "attach_${aws_iam_policy.cloudwatch-access.name}_to_${aws_iam_role.this.name}"
    roles = [aws_iam_role.this.name]
    policy_arn = aws_iam_policy.cloudwatch-access.arn
    
  
}

resource "aws_iam_policy_attachment" "attach-bucket-access-policy" {
    name = "attach_${aws_iam_policy.bucket-access.name}_to_${aws_iam_role.this.name}"
    roles = [aws_iam_role.this.name]
    policy_arn = aws_iam_policy.bucket-access.arn
    
  
}


data "archive_file" "zip_airflow_dags" {
    type = "zip"
    source_dir = "${path.module}/code/lambda_build"
    output_path = "${path.module}/payload/lambda_function_payload.zip"

}


resource "aws_lambda_function" "this" {
    
    filename = "${path.module}/payload/lambda_function_payload.zip"
    function_name = "gfaker"
    role = aws_iam_role.this.arn
    handler = "populate.lambda_handler"

    runtime = "python3.12"

    timeout = 60
    memory_size = 1024 

    depends_on = [ aws_iam_policy_attachment.attach-cloudwatch-policy,  aws_iam_policy_attachment.attach-bucket-access-policy]
  
}






