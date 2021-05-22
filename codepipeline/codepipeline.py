from aws_cdk import (
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_ssm,
    core,
)


class CodePipeline(core.Stack):
    def __init__(self, app: core.App, id: str, props, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        codepipeline = aws_codepipeline.Pipeline(
            self, "CodePipeline",
            pipeline_name="flask-pipeline",
            stages=[
                aws_codepipeline.StageProps(
                    stage_name='Build',
                    actions=[
                        aws_codepipeline_actions.CodeBuildAction(
                            action_name='DockerBuildImages',
                            input=source_output,
                            project=props['ecr_build'],
                            run_order=1,
                        )
                    ]
                )
            ]
        )