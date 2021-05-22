""" This AWS CDK part does:
- ECR repository
- CodeBuild:
    - creates Docker image
    - push Docker image to ECR repository
"""

from aws_cdk import (
    aws_ecr,
    aws_codebuild,
    aws_s3,
    core,
)


class Ecrbuild(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        bucket = aws_s3.Bucket(
            self, "SourceBucket",
            bucket_name=f"flask-bucket-{core.Aws.ACCOUNT_ID}",
            versioned=True,
            removal_policy=core.RemovalPolicy.DESTROY)

        # ECR repository for Docker images
        ecr = aws_ecr.Repository(
            self, "ECR",
            repository_name="flask-repo",
            removal_policy=core.RemovalPolicy.DESTROY
        )

        ecr_build = aws_codebuild.PipelineProject(
            self, "ECRBuild",
            project_name="ecr-image-build",
            build_spec=aws_codebuild.BuildSpec.from_source_filename(
                filename='buildspec.yml'),
            environment=aws_codebuild.BuildEnvironment(
                privileged=True,),
            # pass the ecr repo uri into the codebuild project so codebuild knows where to push
            environment_variables={
                'ecr': aws_codebuild.BuildEnvironmentVariable(
                    value=ecr.repository_uri),
                'tag': aws_codebuild.BuildEnvironmentVariable(
                    value='flask')
            },
            description='Pipeline for CodeBuild',
            timeout=core.Duration.minutes(30),
        )

        ecr.grant_pull_push(ecr_build)

        self.output_params['ecr_build'] = ecr_build
        self.output_params['bucket'] = bucket


    @property
    def outputs(self):
        return self.output_params