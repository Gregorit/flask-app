from aws_cdk import (
    aws_codecommit,
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_ssm,
    core,
)


class CodePipeline(core.Stack):
    def __init__(self, app: core.App, id: str, props, repo_name: str=None, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        source_output = aws_codepipeline.Artifact(artifact_name='source')
        code = aws_codecommit.Repository.from_repository_name(self, "ImportedRepo",
                  repo_name)

        codepipeline = aws_codepipeline.Pipeline(self, "CodePipeline",
            pipeline_name="flask-pipeline",
            artifact_bucket=props['bucket'],
            stages=[
                aws_codepipeline.StageProps(
                    stage_name='Source',
                    actions=[
                        aws_codepipeline_actions.CodeCommitSourceAction(
                            action_name="CodeCommit",
                            repository=code,
                            output=source_output,
                            run_order=1,
                        ),
                    ]
                ),
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
                ),
                aws_codepipeline.StageProps(
                    stage_name='Build2',
                    actions=[
                        aws_codepipeline_actions.CodeBuildAction(
                            action_name='ECSBuild',
                            input=source_output,
                            project=props['ecs_build'],
                            run_order=1,
                        )
                    ]
                )
            ]
        )