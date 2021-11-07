#!/bin/bash

./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/natinstance.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/iam/instanceprofile.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/iam/role.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/securitygroup.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/subnet.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/route.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/networkacl.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/internetgateway.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/vpc.yaml
