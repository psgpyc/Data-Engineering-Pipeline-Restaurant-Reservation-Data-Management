variable "ami_id" {
    type = string
    description = "Name of your ec2 instance"
  
}

variable "instance_type_" {
    type = string
    description = "instance type"
  
}

# variable "public_key_location" {
#     type = string
#     description = "Your public key"
  
# }

variable "key_name" {
    description = "Your key-val pair name"
    type = string
  
}


variable "attach_role_to_instance_profile" {
    type = string
}