from aws_cdk import (
    core,
)

from codebuild.ecr.Ecrbuild import Ecrbuild
from codepipeline.CodePipeline import CodePipeline

props = {'namespace': 'cdk-example-pipeline'}
app = core.App()

# stack for ecr, bucket, codebuild
ecr = Ecrbuild(app, "flask-ecr", props)

# pipeline stack
code_pipeline = CodePipeline(app, "flask-pipeline", ecr.outputs)
code_pipeline.add_dependency(ecr)
app.synth()