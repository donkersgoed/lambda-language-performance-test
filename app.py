#!/usr/bin/env python3

from aws_cdk import core

from lambda_language_performance_test.lambda_language_performance_test_stack import LambdaLanguagePerformanceTestStack


app = core.App()
LambdaLanguagePerformanceTestStack(app, "lambda-language-performance-test")

app.synth()
