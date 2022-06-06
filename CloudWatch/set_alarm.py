# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) with Amazon CloudWatch to create
and manage custom metrics and alarms.
"""

# snippet-start:[python.example_code.cloudwatch.imports]
from datetime import datetime, timedelta
import logging
from pprint import pprint
import random
import time
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# snippet-end:[python.example_code.cloudwatch.imports]


# snippet-start:[python.example_code.cloudwatch.CloudWatchWrapper]
class CloudWatchWrapper:
    """Encapsulates Amazon CloudWatch functions."""
    def __init__(self, cloudwatch_resource):
        """
        :param cloudwatch_resource: A Boto3 CloudWatch resource.
        """
        self.cloudwatch_resource = cloudwatch_resource
# snippet-end:[python.example_code.cloudwatch.CloudWatchWrapper]

# snippet-start:[python.example_code.cloudwatch.ListMetrics]
    def list_metrics(self, namespace, name, recent=False):
        """
        Gets the metrics within a namespace that have the specified name.
        If the metric has no dimensions, a single metric is returned.
        Otherwise, metrics for all dimensions are returned.

        :param namespace: The namespace of the metric.
        :param name: The name of the metric.
        :param recent: When True, only metrics that have been active in the last
                       three hours are returned.
        :return: An iterator that yields the retrieved metrics.
        """
        try:
            kwargs = {'Namespace': namespace, 'MetricName': name}
            if recent:
                kwargs['RecentlyActive'] = 'PT3H'  # List past 3 hours only
            metric_iter = self.cloudwatch_resource.metrics.filter(**kwargs)
            logger.info("Got metrics for %s.%s.", namespace, name)
        except ClientError:
            logger.exception("Couldn't get metrics for %s.%s.", namespace, name)
            raise
        else:
            return metric_iter
# snippet-end:[python.example_code.cloudwatch.ListMetrics]

# snippet-start:[python.example_code.cloudwatch.PutMetricData]
    def put_metric_data(self, namespace, name, value, unit):
        """
        Sends a single data value to CloudWatch for a metric. This metric is given
        a timestamp of the current UTC time.

        :param namespace: The namespace of the metric.
        :param name: The name of the metric.
        :param value: The value of the metric.
        :param unit: The unit of the metric.
        """
        try:
            metric = self.cloudwatch_resource.Metric(namespace, name)
            metric.put_data(
                Namespace=namespace,
                MetricData=[{
                    'MetricName': name,
                    'Value': value,
                    'Unit': unit
                }]
            )
            logger.info("Put data for metric %s.%s", namespace, name)
        except ClientError:
            logger.exception("Couldn't put data for metric %s.%s", namespace, name)
            raise
# snippet-end:[python.example_code.cloudwatch.PutMetricData]

# snippet-start:[python.example_code.cloudwatch.PutMetricData_DataSet]
    def put_metric_data_set(self, namespace, name, timestamp, unit, data_set):
        """
        Sends a set of data to CloudWatch for a metric. All of the data in the set
        have the same timestamp and unit.

        :param namespace: The namespace of the metric.
        :param name: The name of the metric.
        :param timestamp: The UTC timestamp for the metric.
        :param unit: The unit of the metric.
        :param data_set: The set of data to send. This set is a dictionary that
                         contains a list of values and a list of corresponding counts.
                         The value and count lists must be the same length.
        """
        try:
            metric = self.cloudwatch_resource.Metric(namespace, name)
            metric.put_data(
                Namespace=namespace,
                MetricData=[{
                    'MetricName': name,
                    'Timestamp': timestamp,
                    'Values': data_set['values'],
                    'Counts': data_set['counts'],
                    'Unit': unit}])
            logger.info("Put data set for metric %s.%s.", namespace, name)
        except ClientError:
            logger.exception("Couldn't put data set for metric %s.%s.", namespace, name)
            raise
# snippet-end:[python.example_code.cloudwatch.PutMetricData_DataSet]

# snippet-start:[python.example_code.cloudwatch.GetMetricStatistics]
    def get_metric_statistics(self, namespace, name, start, end, period, stat_types):
        """
        Gets statistics for a metric within a specified time span. Metrics are grouped
        into the specified period.

        :param namespace: The namespace of the metric.
        :param name: The name of the metric.
        :param start: The UTC start time of the time span to retrieve.
        :param end: The UTC end time of the time span to retrieve.
        :param period: The period, in seconds, in which to group metrics. The period
                       must match the granularity of the metric, which depends on
                       the metric's age. For example, metrics that are older than
                       three hours have a one-minute granularity, so the period must
                       be at least 60 and must be a multiple of 60.
        :param stat_types: The type of statistics to retrieve, such as average value
                           or maximum value.
        :return: The retrieved statistics for the metric.
        """
        try:
            metric = self.cloudwatch_resource.Metric(namespace, name)
            stats = metric.get_statistics(
                StartTime=start, EndTime=end, Period=period, Statistics=stat_types)
            logger.info(
                "Got %s statistics for %s.", len(stats['Datapoints']), stats['Label'])
        except ClientError:
            logger.exception("Couldn't get statistics for %s.%s.", namespace, name)
            raise
        else:
            return stats
# snippet-end:[python.example_code.cloudwatch.GetMetricStatistics]

# snippet-start:[python.example_code.cloudwatch.PutMetricAlarm]
    def create_metric_alarm(
            self, metric_namespace, metric_name, alarm_name, stat_type, period,
            eval_periods, threshold, comparison_op, dims, actions):
        """
        Creates an alarm that watches a metric.

        :param metric_namespace: The namespace of the metric.
        :param metric_name: The name of the metric.
        :param alarm_name: The name of the alarm.
        :param stat_type: The type of statistic the alarm watches.
        :param period: The period in which metric data are grouped to calculate
                       statistics.
        :param eval_periods: The number of periods that the metric must be over the
                             alarm threshold before the alarm is set into an alarmed
                             state.
        :param threshold: The threshold value to compare against the metric statistic.
        :param comparison_op: The comparison operation used to compare the threshold
                              against the metric.
        :param dims: Dimensions for the alarm, such as instance id, rds identifier
        :return: The newly created alarm.
        """
        try:
            metric = self.cloudwatch_resource.Metric(metric_namespace, metric_name)
            alarm = metric.put_alarm(
                AlarmName=alarm_name,
                AlarmActions=actions,
                Statistic=stat_type,
                Period=period,
                EvaluationPeriods=eval_periods,
                Threshold=threshold,
                ComparisonOperator=comparison_op,
                Dimensions=dims)
            logger.info(
                "Added alarm %s to track metric %s.%s.", alarm_name, metric_namespace,
                metric_name)
        except ClientError:
            logger.exception(
                "Couldn't add alarm %s to metric %s.%s", alarm_name, metric_namespace,
                metric_name)
            raise
        else:
            return alarm
# snippet-end:[python.example_code.cloudwatch.PutMetricAlarm]

# snippet-start:[python.example_code.cloudwatch.DescribeAlarmsForMetric]
    def get_metric_alarms(self, metric_namespace, metric_name):
        """
        Gets the alarms that are currently watching the specified metric.

        :param metric_namespace: The namespace of the metric.
        :param metric_name: The name of the metric.
        :returns: An iterator that yields the alarms.
        """
        metric = self.cloudwatch_resource.Metric(metric_namespace, metric_name)
        alarm_iter = metric.alarms.all()
        logger.info("Got alarms for metric %s.%s.", metric_namespace, metric_name)
        return alarm_iter
# snippet-end:[python.example_code.cloudwatch.DescribeAlarmsForMetric]

# snippet-start:[python.example_code.cloudwatch.EnableAlarmActions.DisableAlarmActions]
    def enable_alarm_actions(self, alarm_name, enable):
        """
        Enables or disables actions on the specified alarm. Alarm actions can be
        used to send notifications or automate responses when an alarm enters a
        particular state.

        :param alarm_name: The name of the alarm.
        :param enable: When True, actions are enabled for the alarm. Otherwise, they
                       disabled.
        """
        try:
            alarm = self.cloudwatch_resource.Alarm(alarm_name)
            if enable:
                alarm.enable_actions()
            else:
                alarm.disable_actions()
            logger.info(
                "%s actions for alarm %s.", "Enabled" if enable else "Disabled",
                alarm_name)
        except ClientError:
            logger.exception(
                "Couldn't %s actions alarm %s.", "enable" if enable else "disable",
                alarm_name)
            raise
# snippet-end:[python.example_code.cloudwatch.EnableAlarmActions.DisableAlarmActions]

# snippet-start:[python.example_code.cloudwatch.DeleteAlarms]
    def delete_metric_alarms(self, metric_namespace, metric_name):
        """
        Deletes all of the alarms that are currently watching the specified metric.

        :param metric_namespace: The namespace of the metric.
        :param metric_name: The name of the metric.
        """
        try:
            metric = self.cloudwatch_resource.Metric(metric_namespace, metric_name)
            metric.alarms.delete()
            logger.info(
                "Deleted alarms for metric %s.%s.", metric_namespace, metric_name)
        except ClientError:
            logger.exception(
                "Couldn't delete alarms for metric %s.%s.", metric_namespace,
                metric_name)
            raise
# snippet-end:[python.example_code.cloudwatch.DeleteAlarms]


# snippet-start:[python.example_code.cloudwatch.Usage_MetricsAlarms]
def usage_demo():
    print('-'*88)
    print("Welcome to the Amazon CloudWatch metrics and alarms demo!")
    print('-'*88)

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    cw_wrapper = CloudWatchWrapper(boto3.resource('cloudwatch'))

    metric_namespace = 'AWS/RDS'
    metric_name = 'CPUUtilization'
    alarm_name = 'RDS_CPU_UsageHigh'    # Alarm名称，根据需要调整
    period = 60                     # 告警统计周期单位为秒，根据需要调整
    eval_periods = 2                # 连续x次则触发告警，根据需要调整
    print(f"Creating alarm {alarm_name} for metric {metric_name}.")
    # 通过dims以Name、Value方式指定alarm适用的对象
    dims = [
        {
            'Name': 'DBInstanceIdentifier',
            'Value': 'mysql-slow-query'     # RDS数据库标识，根据需要调整，一次只能包含一个
        }
    ]

    # actions 指定告警发生时的动作，比如通过SNS发送邮件通知
    actions = [
        'arn:aws:sns:ap-northeast-1:123456789123:cw-alarm-topic'    # 填SNS的ARN
    ]
    alarm = cw_wrapper.create_metric_alarm(
        metric_namespace, metric_name, alarm_name, 'Average', period, eval_periods,
        90, 'GreaterThanThreshold', dims, actions)
    print(f"Alarm ARN is {alarm.alarm_arn}.")
    print(f"Current alarm state is: {alarm.state_value}.")
    print("Thanks for watching!")
    print('-'*88)
# snippet-end:[python.example_code.cloudwatch.Usage_MetricsAlarms]


if __name__ == '__main__':
    usage_demo()