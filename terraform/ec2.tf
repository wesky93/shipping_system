data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name = "name"
    values = [
      "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name = "virtualization-type"
    values = [
      "hvm"]
  }

  owners = [
    "099720109477"]
  # Canonical
}

resource "aws_instance" "web" {
  ami = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  key_name = "everypython"

}
data "aws_route53_zone" "handson" {
  name = "handson.today."
}
resource "aws_route53_record" "www" {
  zone_id = data.aws_route53_zone.handson.zone_id
  name = "django.handson.today"
  type = "A"
  ttl = "300"
  records = [
    aws_instance.web.public_ip
  ]
}