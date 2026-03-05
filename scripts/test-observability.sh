#!/bin/bash
# Test Execution Script for Observability Module
# Validates 100% test coverage

echo "Running observability tests with coverage..."

# Run tests with coverage for observability module only
pytest tests/unit/test_observability.py \
    --cov=src.utils.observability \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=100 \
    -v

# Check exit code
if [ $? -eq 0 ]; then
    echo "✓ 100% test coverage achieved for observability.py"
else
    echo "✗ Test coverage below 100%"
    exit 1
fi
