module "raw_bucket" {
    source = "./modules/s3_bucket"
    bucket_name = "booking-raw-bucket"
  
}

module "staging_bucket" {
  source = "./modules/s3_bucket"
  bucket_name = "booking-staging-bucket"
}

module "processed_bucket" {
    source = "./modules/s3_bucket"
    bucket_name = "booking-processed-bucket"
  
}


module "access_s3_iam_role_module" {

  source = "./modules/iam_role"
  
  role_name = "access_s3_iam_role"

  assume_role_policy = file("./policies/assume-role-policy.json")

  bucket_access_policy = file("./policies/s3-bucket-access-policy.json")

}

module "create_ec2" {

    source = "./modules/ec2"

    ami_id = "ami-01e479df1702f1d13"

    instance_type_ = "t2.micro"
    
    key_name = "base-kp"

    attach_role_to_instance_profile = module.access_s3_iam_role_module.role_name

}

module "provision_pipeline_lambda" {
  source = "./modules/lambda"
  i_am_role_name = "grant_lambda_access_to_cloudwatch_and_s3"
  lambda_assume_role_policy = file("./policies/lambda-assume-role-policy.json")
  lambda_bucket_access_policy = file("./policies/s3-bucket-access-policy.json")
  lambda_cloudwatch_access_policy = file("./policies/cloudwatch-log-access-policy.json")


  eventbridge_schedule_arn = module.eventbridge_booking_create_trigger.scheduler_role_arn
}

module "eventbridge_booking_create_trigger" {
  source = "./modules/eventbridge"

  schedule_name       = "daily-booking-schedule"
  description         = "Trigger Lambda daily at 5AM UTC"
  schedule_expression = "cron(0 5 * * ? *)"

  lambda_arn          = module.provision_pipeline_lambda.lambda_function_arn

  scheduler_role_arn = module.eventbridge_booking_create_trigger.scheduler_role_arn

  payload = {
    message = "Booking trigger from EventBridge"
  }

 
}


resource "aws_lambda_permission" "allow_eventbridge_scheduler" {
  statement_id  = "AllowEventBridgeScheduler"
  action        = "lambda:InvokeFunction"
  function_name = module.provision_pipeline_lambda.lambda_function_name
  principal     = "scheduler.amazonaws.com"
  source_arn    = module.eventbridge_booking_create_trigger.eventbridge_schedule_arn

   depends_on = [
    module.provision_pipeline_lambda,
    module.eventbridge_booking_create_trigger
  ]
}