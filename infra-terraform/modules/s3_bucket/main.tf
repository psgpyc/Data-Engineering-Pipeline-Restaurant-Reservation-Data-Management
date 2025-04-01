resource "aws_s3_bucket" "this" {
    bucket = var.bucket_name

    tags = {
        Name = var.bucket_name
        Environmane = "dev"

    }
  
}


resource "aws_s3_bucket_versioning" "this" {
    bucket = aws_s3_bucket.this.id

    versioning_configuration {
      status = "Enabled"
    }
  
}


