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