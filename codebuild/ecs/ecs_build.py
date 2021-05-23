""" This AWS CDK part does:
- CodeBuild:
    - execute CDK code
"""

from aws_cdk import (
    aws_codebuild,
    core,
)


class Ecsbuild(core.Stack):
    def __init__(self, app: core.App, id: str, props, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        ecs_build = aws_codebuild.PipelineProject(self, "ECSBuild",
            project_name="ecs-cluster-build",
            build_spec=aws_codebuild.BuildSpec.from_source_filename(
                filename='codebuild/ecs/buildspec.yml'),
            environment=aws_codebuild.BuildEnvironment(
                privileged=True,),
            environment_variables={
                'ecr': aws_codebuild.BuildEnvironmentVariable(
                    value=props['ecr'])
            },
            description='Pipeline for CodeBuild',
            timeout=core.Duration.minutes(30),
        )

        self.output_params = props.copy()
        self.output_params['ecs_build'] = ecs_build
    
    @property
    def outputs(self):
        return self.output_params
