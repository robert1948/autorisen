from setuptools import setup, find_packages

setup(
    name='autoagent',
    version='0.1.0',
    description='AI Autoagent SAAS Core',
    author='Robert',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
        'numpy',
        'fastapi',
        'uvicorn[standard]',
    ],
    entry_points={
        'console_scripts': [
            'autoagent = main:main',  # This line assumes src/main.py defines `main()`
        ],
    },
    include_package_data=True,
    python_requires='>=3.8',
)
