#!/bin/bash

send_command() {
  local instance_id="$1"
  local pubkey="$2"
  local s3_bucket="$3"

  aws ssm send-command --instance-ids "${instance_id}" \
    --document-name AWS-RunShellScript \
    --output-s3-bucket-name "${s3_bucket}" \
    --output-s3-key-prefix "${instance_id}" \
    --parameters "{\"commands\":[\"echo '${pubkey}' | tee -a ~ec2-user/.ssh/authorized_keys\"], \"workingDirectory\":[\"/root\"]}"

}
main() {
  local pubkey="ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAuPAe+J5G6QYR8Op/aJ/jsGmoeJz7wFOK08EvF6fIMgZTYOEj7e9qMTRIbraCpJqVQsGRKm79cdySacOuRUuzrpVPRYPV7sc0KY9oIEoKUa+CI2416zSmy9MtuTzmCDav1BbnU5dcGYosnayI7kHJbZINApl9gG8JwByo8qQEvG+nBs2T/sgbKhlRf2O9Zd6MvrDTsKS4SGk2W9QQnTxDsr6b7CTmQ8avn6mW1PJMqX2Cpus63jtUDDVuBYL96SY6i4GLY/KlNrJ3QiSE94aQnId8/dEgc8fYuqU3GlTO1L2NXfH/dyuruSamAImlDcES/q2mzqtkgyu/ts4NCJR/CQ== haris.fauzi@ezidebit.com.au-AWS_only"

  local instance_id=$(aws cloudformation describe-stacks \
                  --stack-name ec2sample-demoaccount-ec2-instance-basic-metadata \
                  --query "Stacks[0].Outputs[?OutputKey=='Test02'].OutputValue" \
                  --output text)
  local s3_output_bucket=$(aws cloudformation describe-stacks \
                  --stack-name ec2sample-demoaccount-s3-bucket \
                  --query "Stacks[0].Outputs[?OutputKey=='Test01'].OutputValue" \
                  --output text)
  echo "instance_id = ${instance_id}"
  send_command "${instance_id}" "${pubkey}" "${s3_output_bucket}"
}

main "$@"
