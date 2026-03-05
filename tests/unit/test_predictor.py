"""
SmartLead Unit Tests - ML Predictor
==================================
Test ML prediction functionality

Spec-Driven: Generated from SmartLead/harness.json testing_harness
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.ml.predictor import LeadPredictor
from src.api.config import Settings


class TestLeadPredictor:
    """Tests for LeadPredictor"""
    
    @pytest.fixture
    def settings(self):
        """Create test settings"""
        return Settings(
            model_path="/tmp/test_model.pkl",
            model_version="1.0.0",
            debug=True
        )
    
    @pytest.fixture
    def predictor(self, settings):
        """Create predictor instance"""
        return LeadPredictor(settings)
    
    @pytest.mark.asyncio
    async def test_load_model(self, predictor):
        """Test model loading"""
        await predictor.load_model()
        
        assert predictor.is_ready()
        assert predictor.model_version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_predict(self, predictor):
        """Test prediction"""
        await predictor.load_model()
        
        features = {
            'company_size_encoded': 2.0,
            'industry_encoded': 1.0,
            'job_title_encoded': 3.0,
            'traffic_source_encoded': 1.0,
            'country_encoded': 1.0,
            'email_domain_tld': 1.0,
            'has_phone': 1.0,
            'has_company_size': 1.0,
            'email_length': 15.0,
            'company_name_length': 10.0
        }
        
        result = await predictor.predict(features)
        
        assert 'probability' in result
        assert 'grade' in result
        assert 'confidence' in result
        assert 0 <= result['probability'] <= 1
        assert result['grade'] in ['A', 'B', 'C', 'D']
    
    @pytest.mark.asyncio
    async def test_predict_not_ready(self, predictor):
        """Test prediction fails when model not loaded"""
        with pytest.raises(RuntimeError):
            await predictor.predict({})
    
    def test_get_grade(self, predictor):
        """Test grade conversion"""
        assert predictor._get_grade(0.9) == "A"
        assert predictor._get_grade(0.7) == "B"
        assert predictor._get_grade(0.5) == "C"
        assert predictor._get_grade(0.2) == "D"
    
    @pytest.mark.asyncio
    async def test_cleanup(self, predictor):
        """Test cleanup"""
        await predictor.load_model()
        await predictor.cleanup()
        
        assert not predictor.is_ready()
