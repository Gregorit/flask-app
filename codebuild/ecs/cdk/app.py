from aws_cdk import (
    core,
)

from ecs.ecs_cluster import Ecscluster

app = core.App()

ecs = Ecscluster(app, "flask-ecs-cluster")

app.synth()
