#!/usr/bin/env python3

import boto3
import argparse
import yaml
import re

CONST_DEFAULT_IN_ALARM = 'arn:aws:sns:ap-southeast-2:882744822126:cns-sns-topic-slack-alert'
CONST_DEFAULT_OK_ALARM = 'arn:aws:sns:ap-southeast-2:882744822126:cns-sns-topic-slack-alert'

class ConfigGenerator:
  def __init__(self, namespace, key, value, output, in_alarm, ok_alarm) -> None:
      self.namespace = namespace
      self.dimension_key = key
      self.dimension_value = value
      self.output_file = output
      self.in_alarm = in_alarm if len(in_alarm) > 0 else CONST_DEFAULT_IN_ALARM
      self.ok_alarm = ok_alarm if len(ok_alarm) > 0 else CONST_DEFAULT_OK_ALARM

  def get_metrics(self):
    client = boto3.client('cloudwatch')
    param_dimensions = [{'Name': self.dimension_key, 'Value': self.dimension_value}]
    metrics_data = client.list_metrics(Namespace=self.namespace, Dimensions=param_dimensions)
    metrics = metrics_data['Metrics']
    return_value = []
    metric_alarms = []
    metric_alarms.append('BurstBalance')
    metric_alarms.append('FreeStorageSpace')
    metric_alarms.append('FreeableMemory')

    for metric in metrics:
      metric_name = metric['MetricName']
      if metric_name in metric_alarms:
        return_value.append(metric)
    return(return_value)

  def get_alarm_dimensions(self, metric):
    dimensions = {}
    metric_dimensions = metric['Dimensions']
    for metric_dimension in metric_dimensions:
      dimension_name = metric_dimension['Name']
      dimension_value = "'{0}'".format(metric_dimension['Value'])
      dimensions[dimension_name] = dimension_value
    return(dimensions)

  def get_alarm_free_storage_space(self, metric, critical_level='warning', critical_threshold='21474836480'):
    return_value = {}
    return_value['comparison_operator'] = ' LessThanThreshold'
    return_value['datapoints_to_alarm'] = '2'
    return_value['evaluation_period'] = '3'
    return_value['period'] = '60'
    return_value['alarm_description'] = "'[{0}] low free storage space on RDS {1}:{2}'".format(critical_level.upper(), self.dimension_key, self.dimension_value)
    return_value['alarm_name'] = "'[{0}] low free storage space on RDS {1}:{2}'".format(critical_level.upper(), self.dimension_key, self.dimension_value)
    return_value['threshold'] = critical_threshold  # default is '21474836480' / 20 GB
    return_value['actions_enabled'] = True
    return_value['alarm_actions'] = [self.in_alarm]
    return_value['ok_actions'] = [self.ok_alarm]
    return_value['metric_name'] = metric['MetricName']
    return_value['statistic'] = 'Average'
    return_value['namespace'] = self.namespace
    return_value['dimensions'] = self.get_alarm_dimensions(metric)
    return(return_value)

  def get_alarm_feeable_memory(self, metric, critical_level='warning', critical_threshold='104857600'):
    return_value = {}
    return_value['comparison_operator'] = 'LessThanThreshold'
    return_value['datapoints_to_alarm'] = '2'
    return_value['evaluation_period'] = '3'
    return_value['period'] = '60'
    return_value['alarm_description'] = "'[{0}] low free memory on RDS {1}:{2}'".format(critical_level.upper(), self.dimension_key, self.dimension_value)
    return_value['alarm_name'] = "'[{0}] low free memory on RDS {1}:{2}'".format(critical_level.upper(), self.dimension_key, self.dimension_value)
    return_value['threshold'] = critical_threshold  # Default is '104857600' / 100 MiB
    return_value['actions_enabled'] = True
    return_value['alarm_actions'] = [self.in_alarm]
    return_value['ok_actions'] = [self.ok_alarm]
    return_value['metric_name'] = metric['MetricName']
    return_value['statistic'] = 'Average'
    return_value['namespace'] = self.namespace
    return_value['dimensions'] = self.get_alarm_dimensions(metric)
    return(return_value)

  def get_alarm_burst_balance(self, metric, critical_level='warning', critical_threshold='50'):
    return_value = {}
    return_value['comparison_operator'] = 'LessThanOrEqualToThreshold'
    return_value['datapoints_to_alarm'] = '5'
    return_value['evaluation_period'] = '5'
    return_value['period'] = '60'
    return_value['alarm_description'] = "'[{0}] low CPU burst balance on RDS {1}:{2}'".format(critical_level.upper(), self.dimension_key, self.dimension_value)
    return_value['alarm_name'] = "'[{0}] low CPU burst balance on RDS {1}:{2}'".format(critical_level.upper(), self.dimension_key, self.dimension_value)
    return_value['threshold'] = critical_threshold  # Default is '100'
    return_value['actions_enabled'] = True
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
      if metric_namespace == 'AWS/RDS' and metric_name == 'BurstBalance':
        critical_alarm_data = self.get_alarm_burst_balance(metric, 'critical', critical_threshold='25')
        critical_alarm_data['name'] = "{0}{1:03d}".format(prefix_name, ii)
        ii += 1
        parsed_data.append(critical_alarm_data)
        alarm_data = self.get_alarm_burst_balance(metric)
      elif metric_namespace == 'AWS/RDS' and metric_name == 'FreeStorageSpace':
        critical_alarm_data = self.get_alarm_free_storage_space(metric, 'critical', '2000000000')
        critical_alarm_data['name'] = "{0}{1:03d}".format(prefix_name, ii)
        ii += 1
        parsed_data.append(critical_alarm_data)
        alarm_data = self.get_alarm_free_storage_space(metric)
      elif metric_namespace == 'AWS/RDS' and metric_name == 'FreeableMemory':
        critical_alarm_data = self.get_alarm_feeable_memory(metric, 'critical', critical_threshold='10485760')
        critical_alarm_data['name'] = "{0}{1:03d}".format(prefix_name, ii)
        ii += 1
        parsed_data.append(critical_alarm_data)
        alarm_data = self.get_alarm_feeable_memory(metric)
      alarm_data['name'] = "{0}{1:03d}".format(prefix_name, ii)
      ii += 1
      parsed_data.append(alarm_data)
    with open(self.output_file, 'a') as file:
      outputs = yaml.dump(parsed_data, file)

      
def main():

  parser = argparse.ArgumentParser(description="Generate YAML for sceptre_user_data")
  parser.add_argument('-n', dest='namespace', default='AWS/RDS',
                    help='The Namespace to filter')
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
  config_generator = ConfigGenerator(args.namespace, args.key, args.value, args.output, args.in_alarm, args.ok_alarm)

  metrics = config_generator.get_metrics()
  config_generator.generate_yaml(metrics)

if __name__ == "__main__":
    main()