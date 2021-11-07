#!/bin/bash
IMAGE_PATTERN="amzn2-ami-hvm-2.?.????????.?-x86_64-ebs"
IMAGE_ID=$(aws ec2 describe-images --filters "Name=name,Values='${IMAGE_PATTERN}'" --owners amazon --query "reverse(sort_by(Images, &CreationDate))[0].ImageId" --output text)
echo "${IMAGE_ID}"
