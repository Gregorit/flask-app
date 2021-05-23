from aws_cdk import (
    core,
)

from codebuild.ecr.ecr_build import Ecrbuild
from codebuild.ecs.ecs_build import Ecsbuild
from codepipeline.codepipeline import CodePipeline

CODECOMMIT_REPO_NAME = "flask-app"

props = {}
app = core.App()

# stack for ecr, bucket, codebuild
ecr = Ecrbuild(app, "flask-ecr", props)
props = ecr.outputs.copy()
ecs = Ecsbuild(app, "flask-ecs", props)
props = ecs.outputs.copy()

# pipeline stack
code_pipeline = CodePipeline(app, "flask-pipeline", props, repo_name=CODECOMMIT_REPO_NAME)
code_pipeline.add_dependency(ecr)
code_pipeline.add_dependency(ecs)
app.synth()
