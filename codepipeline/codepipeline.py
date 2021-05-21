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
            artifact_bucket=props['bucket'],
            stages=[
                aws_codepipeline.StageProps(
                    stage_name='Source',
                    actions=[
                        aws_codepipeline_actions.S3SourceAction(
                            bucket=props['bucket'],
                            bucket_key='source.zip',
                            action_name='S3Source',
                            run_order=1,
                            output=source_output,
                            trigger=aws_codepipeline_actions.S3Trigger.POLL
                        ),
                    ]
                ),
                aws_codepipeline.StageProps(
                    stage_name='Build',
                    actions=[
                        aws_codepipeline_actions.CodeBuildAction(
                            action_name='DockerBuildImages',
                            input=source_output,
                            project=props['cb_docker_build'],
                            run_order=1,
                        )
                    ]
                )
            ]
        )