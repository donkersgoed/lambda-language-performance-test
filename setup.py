import setuptools


with open("README.md") as fp:
    long_description = fp.read()

CDK_VERSION = None
with open('.env.aws', 'r') as env_file:
    env_vars = env_file.read().split('\n')
    for env_var in env_vars:
        if env_var.startswith('CDK_VERSION'):
            CDK_VERSION = env_var.split('=')[1].replace('"', '')

if not CDK_VERSION:
    raise ValueError('The ENV VAR CDK_VERSION is required.')

setuptools.setup(
    name="lambda_language_performance_test",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "lambda_language_performance_test"},
    packages=setuptools.find_packages(where="lambda_language_performance_test"),

    install_requires=[
        'python-dotenv==0.10.3',
        f'aws_cdk.aws_lambda=={CDK_VERSION}',
        f'aws_cdk.aws_stepfunctions_tasks=={CDK_VERSION}',
        f'aws_cdk.aws_stepfunctions=={CDK_VERSION}',
        f'aws-cdk.core=={CDK_VERSION}',
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
