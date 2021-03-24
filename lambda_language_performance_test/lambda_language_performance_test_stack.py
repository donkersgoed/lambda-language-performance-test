# Standard library imports
# -

# Related third party imports
from aws_cdk import (
    aws_lambda as lambda_,
    core,
)

# Local application/library specific imports
# -

class LambdaLanguagePerformanceTestStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        memory_size = 128
        test_data_file = 'test_data_10000.json'

        # Lambda Layer with the test JSON
        json_layer = lambda_.LayerVersion(
            self, 'lambda-json-layer',
            code=lambda_.Code.asset('lambda_code/layer/test_data.zip'),
            compatible_runtimes=[
                lambda_.Runtime.PYTHON_3_8,
                lambda_.Runtime.PROVIDED_AL2,
                lambda_.Runtime.GO_1_X,
            ],
            description='Layer with the JSON files for benchmarking'
        )

        lambda_.Function(
            scope=self,
            id='perf-test-python',
            function_name='perf-test-python',
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.asset('lambda_code/python'),
            handler='index.lambda_handler',
            layers=[json_layer],
            memory_size=memory_size,
            timeout=core.Duration.seconds(60),
            environment={
                'TEST_DATA_FILE': test_data_file
            },
        )

        lambda_.Function(
            scope=self,
            id='perf-test-rust',
            function_name='perf-test-rust',
            runtime=lambda_.Runtime.PROVIDED_AL2,
            code=lambda_.Code.asset('lambda_code/rust/rust.zip'),
            handler='doesnt.matter',
            layers=[json_layer],
            memory_size=memory_size,
            timeout=core.Duration.seconds(60),
            environment={
                'TEST_DATA_FILE': test_data_file
            },
        )

        lambda_.Function(
            scope=self,
            id='perf-test-go',
            function_name='perf-test-go',
            runtime=lambda_.Runtime.GO_1_X,
            code=lambda_.Code.asset('lambda_code/go/go.zip'),
            handler='main',
            layers=[json_layer],
            memory_size=memory_size,
            timeout=core.Duration.seconds(60),
            environment={
                'TEST_DATA_FILE': test_data_file
            },
        )
