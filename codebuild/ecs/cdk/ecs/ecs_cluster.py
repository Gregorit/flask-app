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
)


class Ecscluster(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        vpc = aws_ec2.Vpc.from_vpc_attributes(self, "VPC",
            vpc_id="vpc-f80bfa81",
            availability_zones=["eu-west-1a","eu-west-1b","eu-west-1c"]
        )

        cluster = aws_ecs.Cluster(self, 'ECSCluster',
            vpc=vpc,
            cluster_name="flask-ecs"
        )

        load_balanced_ec2_service = aws_ecs_patterns.ApplicationMultipleTargetGroupsEc2Service(self, "ECSService",
            cluster=cluster,
            memory_limit_mi_b=512,
            task_image_options={
                "image": aws_ecs.ContainerImage.from_asset('.')
            },
            target_groups=[{
                "container_port": 5000
            }, {
                "container_port": 5000,
                "path_pattern": "a/b/c",
                "priority": 10
            }
            ]
        )

        scalable_target = load_balanced_ec2_service.service.auto_scale_task_count(
            min_capacity=2,
            max_capacity=10
        )

        scalable_target.scale_on_cpu_utilization("CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60)
        )

        scalable_target.scale_on_memory_utilization("MemoryScaling",
            target_utilization_percent=50,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60)
        )
