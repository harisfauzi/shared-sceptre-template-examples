#!/usr/bin/env python3

import boto3
import argparse
import yaml
import re
import datetime


CONST_DEFAULT_IN_ALARM = 'arn:aws:sns:ap-southeast-2:882744822126:cns-sns-topic-slack-alert'
CONST_DEFAULT_OK_ALARM = 'arn:aws:sns:ap-southeast-2:882744822126:cns-sns-topic-slack-alert'

class ConfigGenerator:
  def __init__(self, namespace, key, value, output, in_alarm, ok_alarm, use_recover='false') -> None:
      self.namespace = namespace
      self.dimension_key = key
      self.dimension_value = value
      self.use_recover = False if use_recover.lower() == 'false' else True
      self.output_file = output
      self.in_alarm = in_alarm if len(in_alarm) > 0 else CONST_DEFAULT_IN_ALARM
      self.ok_alarm = ok_alarm if len(ok_alarm) > 0 else CONST_DEFAULT_OK_ALARM
      currentDT = datetime.datetime.now()
      self.timestamp = currentDT.strftime("%Y%m%d%H%M%S")

  def get_metrics(self):
    client = boto3.client('cloudwatch')
    # param_namespace = 'CWAgent'
    param_dimensions = [{'Name': self.dimension_key, 'Value': self.dimension_value}]
    metrics_data = client.list_metrics(Namespace=self.namespace,
                      Dimensions=param_dimensions)
    metrics = metrics_data['Metrics']
    return_value = []
    metric_alarms = ["disk_used_percent",
                      "mem_used_percent",
                      "CPUCreditBalance",
                      "CPUUtilization",
                      "StatusCheckFailed",
                      "StatusCheckFailed_Instance",
                      "StatusCheckFailed_System"]
    metric_fstype = ["xfs", "nfs4"]
    for metric in metrics:
      metric_name = metric['MetricName']
      if metric_name in metric_alarms:
        # We need to filter out any metric with fstype not defined in metric_fstype
        if metric_name == "disk_used_percent" and self.get_dimension_by_name(metric, "fstype") not in metric_fstype:
          continue
        return_value.append(metric)
    return(return_value)

  def get_alarm_dimensions(self, metric):
    dimensions = {}
    metric_dimensions = metric['Dimensions']
    for metric_dimension in metric_dimensions:
      dimension_name = metric_dimension['Name']
      dimension_value = metric_dimension['Value']
      dimensions[dimension_name] = dimension_value
    return(dimensions)

  def get_dimension_by_name(self, metric, dimension_name):
    return_value = ''
    metric_dimensions = metric['Dimensions']
    for dimension in metric_dimensions:
      if str(dimension['Name']).lower() == dimension_name.lower():
        return_value = dimension['Value']
        break
    return(return_value)


  def get_alarm_disk_used_percent(self, metric, critical_level='warning', critical_threshold='80'):
    return_value = {}
    return_value['comparison_operator'] = 'GreaterThanThreshold'
    return_value['datapoints_to_alarm'] = '2'
    return_value['evaluation_period'] = '3'
    return_value['period'] = '60'
    path = self.get_dimension_by_name(metric, "path")
    return_value['alarm_description'] = "'[{0}] high disk usage on {1}:{2} on path {3}'".format(critical_level.upper(), self.dimension_key, self.dimension_value, path)
    return_value['alarm_name'] = "'[{0}] high disk usage on {1}:{2} on path {3}'".format(critical_level.upper(), self.dimension_key, self.dimension_value, path)
    return_value['threshold'] = critical_threshold
    return_value['actions_enabled'] = True
    return_value['alarm_actions'] = [self.in_alarm]
    return_value['ok_actions'] = [self.ok_alarm]
    return_value['metric_name'] = metric['MetricName']
    return_value['statistic'] = 'Average'
    return_value['namespace'] = self.namespace
    return_value['dimensions'] = self.get_alarm_dimensions(metric)
    return(return_value)

  def get_alarm_mem_used_percent(self, metric, critical_level='warning', critical_threshold='95'):
    return_value = {}
    return_value['comparison_operator'] = 'GreaterThanThreshold'
    return_value['datapoints_to_alarm'] = '2'
    return_value['evaluation_period'] = '3'
    return_value['period'] = '60'
    return_value['alarm_description'] = "'[{0}] high memory usage on {1}:{2}'".format(critical_level.upper(), self.dimension_key, self.dimension_value)
    return_value['alarm_name'] = "'[{0}] high memory usage on {1}:{2}'".format(critical_level.upper(), self.dimension_key, self.dimension_value)
    return_value['threshold'] = critical_threshold
    return_value['actions_enabled'] = True
    return_value['alarm_actions'] = [self.in_alarm]
    return_value['ok_actions'] = [self.ok_alarm]
    return_value['metric_name'] = metric['MetricName']
    return_value['statistic'] = 'Average'
    return_value['namespace'] = self.namespace
    return_value['dimensions'] = self.get_alarm_dimensions(metric)
    return(return_value)

  def get_alarm_cpu_utilization(self, metric, critical_level='warning', critical_threshold='85'):
    return_value = {}
    return_value['comparison_operator'] = 'GreaterThanThreshold'
    return_value['datapoints_to_alarm'] = '5'
    return_value['evaluation_period'] = '5'
    return_value['period'] = '60'
    return_value['alarm_description'] = "'[{0}] high CPU Utilization on {1}:{2}'".format(critical_level.upper(), self.dimension_key, self.dimension_value)
    return_value['alarm_name'] = "'[{0}] high CPU Utilization on {1}:{2}'".format(critical_level.upper(), self.dimension_key, self.dimension_value)
    return_value['threshold'] = critical_threshold
    return_value['actions_enabled'] = True
    return_value['alarm_actions'] = [self.in_alarm]
    return_value['ok_actions'] = [self.ok_alarm]
    return_value['metric_name'] = metric['MetricName']
    return_value['statistic'] = 'Average'
    return_value['namespace'] = self.namespace
    return_value['dimensions'] = self.get_alarm_dimensions(metric)
    return(return_value)

  def get_alarm_cpu_credit_balance(self, metric, critical_level='warning', critical_threshold='500'):
    return_value = {}
    return_value['comparison_operator'] = 'LessThanOrEqualToThreshold'
    return_value['datapoints_to_alarm'] = '5'
    return_value['evaluation_period'] = '5'
    return_value['period'] = '60'
    return_value['alarm_description'] = "'[{0}] low CPU credit balance on {1}:{2}'".format(critical_level.upper(), self.dimension_key, self.dimension_value)
    return_value['alarm_name'] = "'[{0}] low CPU credit balance on {1}:{2}'".format(critical_level.upper(), self.dimension_key, self.dimension_value)
    return_value['threshold'] = critical_threshold
    return_value['actions_enabled'] = True
    return_value['alarm_actions'] = [self.in_alarm]
    return_value['ok_actions'] = [self.ok_alarm]
    return_value['metric_name'] = metric['MetricName']
    return_value['statistic'] = 'Average'
    return_value['namespace'] = self.namespace
    return_value['dimensions'] = self.get_alarm_dimensions(metric)
    return(return_value)

  def get_alarm_status_check_failed(self, metric, use_recover=False):
    return_value = {}
    return_value['comparison_operator'] = 'GreaterThanThreshold'
    return_value['datapoints_to_alarm'] = '2'
    return_value['evaluation_period'] = '2'
    return_value['period'] = '60'
    return_value['alarm_description'] = "'[CRITICAL] {0} on {1}:{2}'".format(metric['MetricName'], self.dimension_key, self.dimension_value)
    return_value['alarm_name'] = "'[CRITICAL] {0} on {1}:{2}'".format(metric['MetricName'], self.dimension_key, self.dimension_value)
    return_value['threshold'] = '2'
    return_value['actions_enabled'] = True
    return_value['alarm_actions'] = [self.in_alarm]
    if metric['MetricName'] == 'StatusCheckFailed_System' and use_recover:
      return_value['alarm_actions'] = [self.in_alarm, '!Sub "arn:aws:automate:${AWS::Region}:ec2:recover"']
    else:
      return_value['alarm_actions'] = [self.in_alarm]
    return_value['ok_actions'] = [self.ok_alarm]
    return_value['metric_name'] = metric['MetricName']
    return_value['statistic'] = 'Average'
    return_value['namespace'] = self.namespace
    return_value['dimensions'] = self.get_alarm_dimensions(metric)
    return(return_value)

  def generate_yaml(self, metrics):
    parsed_data = []
    ii = 0
    replace_pattern = r'[^a-zA-Z0-9]'
    prefix_name = re.sub(replace_pattern, '', self.namespace)
    for metric in metrics:
      metric_namespace = metric['Namespace']
      metric_name = metric['MetricName']
      alarm_data = {}
      if metric_namespace == 'CWAgent' and metric_name == 'disk_used_percent':
        critical_alarm_data = self.get_alarm_disk_used_percent(metric, 'critical', '95')
        critical_alarm_data['name'] = "{0}{1:03d}".format(prefix_name, ii)
        ii += 1
        parsed_data.append(critical_alarm_data)
        alarm_data = self.get_alarm_disk_used_percent(metric)
      elif metric_namespace == 'CWAgent' and metric_name == 'mem_used_percent':
        critical_alarm_data = self.get_alarm_mem_used_percent(metric, 'critical', '99')
        critical_alarm_data['name'] = "{0}{1:03d}".format(prefix_name, ii)
        ii += 1
        parsed_data.append(critical_alarm_data)
        alarm_data = self.get_alarm_mem_used_percent(metric)
      elif metric_namespace == 'AWS/EC2' and metric_name == 'CPUUtilization':
        critical_alarm_data = self.get_alarm_cpu_utilization(metric, 'critical', '99')
        critical_alarm_data['name'] = "{0}{1:03d}".format(prefix_name, ii)
        ii += 1
        parsed_data.append(critical_alarm_data)
        alarm_data = self.get_alarm_cpu_utilization(metric)
      elif metric_namespace == 'AWS/EC2' and metric_name == 'CPUCreditBalance':
        critical_alarm_data = self.get_alarm_cpu_credit_balance(metric, 'critical', '100')
        critical_alarm_data['name'] = "{0}{1:03d}".format(prefix_name, ii)
        ii += 1
        parsed_data.append(critical_alarm_data)
        alarm_data = self.get_alarm_cpu_credit_balance(metric)
      elif metric_namespace == 'AWS/EC2' and metric_name in ['StatusCheckFailed', 'StatusCheckFailed_Instance', 'StatusCheckFailed_System']:
        alarm_data = self.get_alarm_status_check_failed(metric, self.use_recover)
      alarm_data['name'] = "{0}{1:03d}".format(prefix_name, ii)
      ii += 1
      parsed_data.append(alarm_data)
    with open(self.output_file, 'a') as file:
      outputs = yaml.dump(parsed_data, file)


def main():

  parser = argparse.ArgumentParser(description="Generate YAML for sceptre_user_data")
  parser.add_argument('-n', dest='namespace', default='CWAgent',
                    help='The Namespace to filter')
  parser.add_argument('-r', dest='userecover', default='false',
                    help='The MetricName to filter')
  parser.add_argument('-k', dest='key', default='AutoScalingGroupName',
                    help='The Dimension Key to filter')
  parser.add_argument('-v', dest='value', default='',
                    help='The Dimension Value to filter')
  parser.add_argument('-o', dest='output', default='output.yaml',
                    help='The output file')
  parser.add_argument('-a1', dest='in_alarm', default='',
                    help='The ARN for in alarm action')
  parser.add_argument('-a2', dest='ok_alarm', default='',
                    help='The ARN for OK action')

  args = parser.parse_args()
  config_generator = ConfigGenerator(args.namespace, args.key, args.value, args.output, args.in_alarm, args.ok_alarm, args.userecover)

  metrics = config_generator.get_metrics()
  config_generator.generate_yaml(metrics)

if __name__ == "__main__":
    main()