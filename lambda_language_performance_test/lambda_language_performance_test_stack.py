# Standard library imports
# -

# Related third party imports
from aws_cdk import (
    aws_lambda as lambda_,
    aws_stepfunctions as stepfunctions,
    aws_stepfunctions_tasks as tasks,
    core,
)

# Local application/library specific imports
# -

class LambdaLanguagePerformanceTestStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        memory_size = 3008
        data_file_size = 100000
        test_data_file = f'test_data_{data_file_size}.json'

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

        # The performance test in Python
        python_test = lambda_.Function(
            scope=self,
            id='perf-test-python',
            function_name=f'perf-test-python-{memory_size}-{data_file_size}',
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

        # The performance test in Rust
        rust_test = lambda_.Function(
            scope=self,
            id='perf-test-rust',
            function_name=f'perf-test-rust-{memory_size}-{data_file_size}',
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

        # The performance test in Go
        go_test = lambda_.Function(
            scope=self,
            id='perf-test-go',
            function_name=f'perf-test-go-{memory_size}-{data_file_size}',
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

        # Create three nested state machines. The first one ('perf-test-level-1-state-machine') will
        # run the second one ten times in parallel. The second one will run the third state machine
        # ten times in parallel, which in turn will run the lambda 10 times. This results in 1000
        # (10 * 10 * 10) parallel executions.
        level_3_state_machine_definition = stepfunctions.Parallel(
            scope=self,
            id='Run 10 parallel executions (Level 3)',
        )

        for i in range(0,10):
            level_3_state_machine_definition.branch(
                tasks.LambdaInvoke(
                    scope=self,
                    id=f'Run Lambda {i}',
                    lambda_function=go_test,
                    payload_response_only=True,
                )
            )

        level_3_state_machine = stepfunctions.StateMachine(
            scope=self,
            id='perf-test-level-3-state-machine',
            definition=level_3_state_machine_definition,
            timeout=core.Duration.minutes(180),
        )

        # Create ten level 3 state machine tasks (each will execute the lambda_task
        # defined above)
        trigger_level_3_state_machines = []
        for i in range(0,10):
            trigger_level_3_state_machines.append(
                tasks.StepFunctionsStartExecution(
                    scope=self,
                    id=f'Start Level 3 SFN {i}',
                    state_machine=level_3_state_machine,
                    integration_pattern=stepfunctions.IntegrationPattern.RUN_JOB,
                )
            )

        # Create the Parallel step for the level 2 state machine
        level_2_state_machine_definition = stepfunctions.Parallel(
            scope=self,
            id='Run 10 parallel executions (level 2)',
        )
        # Add the ten level 3 state machines
        for trigger_level_3_state_machine in trigger_level_3_state_machines:
            level_2_state_machine_definition.branch(trigger_level_3_state_machine)

        # Create the Parallel step for the level 2 state machine
        level_2_state_machine = stepfunctions.StateMachine(
            scope=self,
            id='perf-test-level-2-state-machine',
            definition=level_2_state_machine_definition,
            timeout=core.Duration.minutes(180),
        )

        # Create ten level 2 state machine tasks (each will execute the level_2_state_machine
        # defined above)
        trigger_level_2_state_machines = []
        for i in range(0,10):
            trigger_level_2_state_machines.append(
                tasks.StepFunctionsStartExecution(
                    scope=self,
                    id=f'Start Level 2 SFN {i}',
                    state_machine=level_2_state_machine,
                    integration_pattern=stepfunctions.IntegrationPattern.RUN_JOB,
                )
            )

        # Create the Parallel step for the top level state machine
        level_1_state_machine_definition = stepfunctions.Parallel(
            scope=self,
            id='Run 10 parallel executions (top level)',
        )
        # Add the ten level 2 state machines
        for trigger_level_2_state_machine in trigger_level_2_state_machines:
            level_1_state_machine_definition.branch(trigger_level_2_state_machine)

        stepfunctions.StateMachine(
            scope=self,
            id='perf-test-level-1-state-machine',
            definition=level_1_state_machine_definition,
            timeout=core.Duration.minutes(180),
        )
