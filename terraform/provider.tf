provider "aws" {
    region = "ap-northeast-2"
}

terraform {
  required_version = ">= 0.9.5"
  backend "remote" {
    hostname = "app.terraform.io"
    organization = "test-django"
    workspaces {
      name = "django"
    }
  }
}
