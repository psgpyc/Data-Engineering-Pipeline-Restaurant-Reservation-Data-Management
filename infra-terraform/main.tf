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