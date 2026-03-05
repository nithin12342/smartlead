@echo off
REM SmartLead Test Setup and Execution Script
REM Run this to install dependencies and execute tests

echo Installing test dependencies...
pip install pytest pytest-cov pytest-asyncio

echo.
echo Running observability tests with coverage...
python -m pytest tests/unit/test_observability.py -v --cov=src.utils.observability --cov-report=term-missing --cov-fail-under=100

echo.
echo Test execution complete!
pause
