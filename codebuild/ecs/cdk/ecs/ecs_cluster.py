""" This AWS CDK part does:
- ASG configuration (2 subnets)
- ALB configuration
- TG configuration for ALB (2 TGs)
- SG for inbound connections
- ECS Configuration
"""

import os
from aws_cdk import (
    core,
    aws_ecr,
    aws_ec2,
    aws_ecs,
    aws_ecs_patterns,
    aws_elasticloadbalancingv2,
)


class Ecscluster(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        vpc = aws_ec2.Vpc(
            self, "Vpc",
            max_azs=2
        )

        cluster = aws_ecs.Cluster(self, 'ECSCluster',
            vpc=vpc,
            cluster_name="flask-ecs"
        )

        cluster.add_capacity("DefaultAutoScalingGroup",
            instance_type=aws_ec2.InstanceType("t2.xlarge"),
            desired_capacity=2,
        )

        # Create Task Definition
        task_definition = aws_ecs.Ec2TaskDefinition(
            self, "TaskDef")
        container = task_definition.add_container(
            "web",
            # image=aws_ecs.ContainerImage.from_ecr_repository(os.environ["ecr"]),
            image=aws_ecs.ContainerImage.from_asset('./'),
            # image=aws_ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
            memory_limit_mib=256
        )
        port_mapping = aws_ecs.PortMapping(
            container_port=80,
            host_port=8080,
            protocol=aws_ecs.Protocol.TCP
        )
        container.add_port_mappings(port_mapping)

        # Create Service
        service = aws_ecs.Ec2Service(
            self, "Service",
            cluster=cluster,
            task_definition=task_definition
        )

        # Setup AutoScaling policy
        scaling = service.auto_scale_task_count(
            min_capacity=2,
            max_capacity=6
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60),
        )

        # Create ALB
        lb = aws_elasticloadbalancingv2.ApplicationLoadBalancer(
            self, "LB",
            vpc=vpc,
            internet_facing=True
        )
        listener = lb.add_listener(
            "PublicListener",
            port=80,
            open=True
        )

        health_check = aws_elasticloadbalancingv2.HealthCheck(
            interval=core.Duration.seconds(60),
            path="/health",
            timeout=core.Duration.seconds(5)
        )

        # Attach ALB to ECS Service
        listener.add_targets(
            "ECSCluster",
            port=80,
            targets=[service],
            health_check=health_check,
        )

        tg1 = aws_elasticloadbalancingv2.ApplicationTargetGroup(self, "TG1",
            target_type=aws_elasticloadbalancingv2.TargetType.INSTANCE,
            port=80,
            stickiness_cookie_duration=core.Duration.minutes(5),
            vpc=vpc
        )

        tg2 = aws_elasticloadbalancingv2.ApplicationTargetGroup(self, "TG2",
            target_type=aws_elasticloadbalancingv2.TargetType.INSTANCE,
            port=80,
            stickiness_cookie_duration=core.Duration.minutes(5),
            vpc=vpc
        )
