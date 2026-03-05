@echo off
set PATH=C:\Users\thela\AppData\Local\Programs\Python\Python313;C:\Users\thela\AppData\Local\Programs\Python\Python313\Scripts;%PATH%
python -m pip install pytest pytest-cov pytest-asyncio
python -m pytest tests/unit/test_observability.py -v --cov=src.utils.observability --cov-config=.coveragerc --cov-report=term-missing --cov-fail-under=100
