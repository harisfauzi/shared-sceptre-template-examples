#!/bin/bash
DEFAULT_IMAGE_PATTERN="amzn2-ami-hvm-2.?.????????.?-x86_64-ebs"
IMAGE_PATTERN=""
OWNER_ARG=""

parse_arguments() {
    while (( "$#" )); do
      case "$1" in
        -p|--pattern)
          IMAGE_PATTERN=$2
          shift 2
          ;;
        -o|--owner)
          IMAGE_OWNER=$2
          shit 2
          ;;
      esac
    done
    # set positional arguments in their proper place
    eval set -- "$PARAMS"
}

main() {
  parse_arguments "$@"

  if [ "z${IMAGE_PATTERN}" == "z" ]; then
    IMAGE_PATTERN="${DEFAULT_IMAGE_PATTERN}"
  fi
  if [ "z${IMAGE_OWNER}" != "z" ]; then
    OWNER_ARG="--owners ${DEFAULT_IMAGE_OWNER}"
  fi
  IMAGE_ID=$(aws ec2 describe-images --filters "Name=name,Values='${IMAGE_PATTERN}'" ${OWNER_ARG} --query "reverse(sort_by(Images, &CreationDate))[0].ImageId" --output text)
  echo "${IMAGE_ID}"
}

main "$@"