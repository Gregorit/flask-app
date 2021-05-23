""" This AWS CDK part does:
- ASG configuration (2 subnets)
- ALB configuration
- TG configuration for ALB (2 TGs)
- SG for inbound connections
- ECS Configuration
"""

from aws_cdk import (
    core,
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

        # vpc = aws_ec2.Vpc.from_vpc_attributes(self, "VPC",
        #     vpc_id="vpc-f80bfa81",
        #     availability_zones=["eu-west-1a","eu-west-1b","eu-west-1c"]
        # )

        cluster = aws_ecs.Cluster(self, 'ECSCluster',
            vpc=vpc,
            cluster_name="flask-ecs"
        )

        cluster.add_capacity("DefaultAutoScalingGroup",
            instance_type=aws_ec2.InstanceType("t2.xlarge"),
        )

        # Create Task Definition
        task_definition = aws_ecs.Ec2TaskDefinition(
            self, "TaskDef")
        container = task_definition.add_container(
            "web",
            image=aws_ecs.ContainerImage.from_asset('/'),
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
            desired_capacity=2,
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

        # load_balanced_ec2_service = aws_ecs_patterns.ApplicationMultipleTargetGroupsEc2Service(self, "ECSService",
        #     cluster=cluster,
        #     # memory_limit_mi_b=512,
        #     task_image_options={
        #         "image": aws_ecs.ContainerImage.from_asset('.')
        #     },
        #     container_port=5000,
        #     target_groups=[{
        #         "container_port": 5000
        #     }, {
        #         "container_port": 5000,
        #         "path_pattern": "a/b/c",
        #         "priority": 10
        #     }
        #     ]
        # )

        # scalable_target = load_balanced_ec2_service.service.auto_scale_task_count(
        #     min_capacity=2,
        #     max_capacity=10
        # )

        # scalable_target.scale_on_cpu_utilization("CpuScaling",
        #     target_utilization_percent=50,
        #     scale_in_cooldown=core.Duration.seconds(60),
        #     scale_out_cooldown=core.Duration.seconds(60)
        # )

        # scalable_target.scale_on_memory_utilization("MemoryScaling",
        #     target_utilization_percent=50,
        #     scale_in_cooldown=core.Duration.seconds(60),
        #     scale_out_cooldown=core.Duration.seconds(60)
        # )
