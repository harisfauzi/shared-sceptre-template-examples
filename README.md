# README

This repo contains sample(s) of how to utilised the [shared-sceptre-template](https://github.com/harisfauzi/shared-sceptre-template) repo.

The structure of the this repo is:

./ = top directory

./network-sample = a `sceptre` project for network-sample. The sceptre project code is `samplenetwork` as can be inspected in ./network-sample/config/config.yaml. Then following `sceptre` convention, you can see sceptre config files under ./network-sample/config/. The templates will be downloaded from share-sceptre-template repo.

To help you try this example, there is a provided bash script that will help you quickly deploy the Cloudformation templates defined in this repo, called `deploy-cfn.sh`. To use it to deploy the resources in network-sample project, you must have the following resources ready:

- AWS account with shell access
- Privilege to create resources in the selected AWS account.
- Linux (or anything that can run bash)
- Python 3 (minimum Python 3.6) installed
- jq installed.
- AWS CLI installed.
- Then either use the IAM User API key or the IAM Role assumed credentials to get the session key before proceeding.

Run the following commands to prepare your AWS access:

```bash
AWS_PROFILE=<your AWS profile>
AWS_DEFAULT_REGION=<your selected AWS region, e.g. us-west-2>
export AWS_PROFILE AWS_DEFAULT_REGION
```

(optional) to test your AWS access run the following (if you have AWS CLI installed):

```bash
aws sts get-caller-identity
```

You should get a JSON output like the following if your AWS authentication was successful:

```json
{
    "UserId": "AIDAIXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:yyyy/zzzzz"
}
```

Then you can try to either manually  deploy the resource one-by-one or let sceptre do the cascade deploy. 

## network-sample project

The network-sample project will deploy the following resources:

- VPC
- Internet Gateway
- Network ACL
- Route Tables + Entries
- Subnets (Public Subnets which will have default route to the Internet Gateway, Private Subnets which will have default route to the NAT instance, and PrivateLink to connect to VPC Endpoint or TransitGateway)
- Security Group for NAT instances
- IAM Role for NAT instances
- IAM Instance Profiles for NAT Instances
- NAT Instances (not NAT Gateways)

To deploy the resources in network-sample one-by-one, run the following commands in these exact sequence:

```bash
./deploy-cfn.sh -p network-sample -n deploy -f sample-vars.yaml -i networkhub/ec2/vpc.yaml
./deploy-cfn.sh -p network-sample -n deploy -f sample-vars.yaml -i networkhub/ec2/internetgateway.yaml
./deploy-cfn.sh -p network-sample -n deploy -f sample-vars.yaml -i networkhub/ec2/networkacl.yaml
./deploy-cfn.sh -p network-sample -n deploy -f sample-vars.yaml -i networkhub/ec2/route.yaml
./deploy-cfn.sh -p network-sample -n deploy -f sample-vars.yaml -i networkhub/ec2/subnet.yaml
./deploy-cfn.sh -p network-sample -n deploy -f sample-vars.yaml -i networkhub/ec2/securitygroup.yaml
./deploy-cfn.sh -p network-sample -n deploy -f sample-vars.yaml -i networkhub/iam/role.yaml
./deploy-cfn.sh -p network-sample -n deploy -f sample-vars.yaml -i networkhub/iam/instanceprofile.yaml
./deploy-cfn.sh -p network-sample -n deploy -f sample-vars.yaml -i networkhub/ec2/natinstance.yaml
```

To let `sceptre`  deploy the resources in cascading style, you can run only the following and all other dependencies will be deployed automatically:

```bash
./deploy-cfn.sh -p network-sample -n deploy -f sample-vars.yaml -i networkhub/ec2/natinstance.yaml
```

To remove the resources, either remove the resources from AWS Cloudformation console, or run the script `delete-all.sh`, or run the following in these exact sequence:

```bash
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/natinstance.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/iam/instanceprofile.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/iam/role.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/securitygroup.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/subnet.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/route.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/networkacl.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/internetgateway.yaml
./deploy-cfn.sh -p network-sample -n destroy -f sample-vars.yaml -i networkhub/ec2/vpc.yaml
```



