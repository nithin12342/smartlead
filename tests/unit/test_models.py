"""
SmartLead Unit Tests - API Models
==================================
Test Pydantic models for request/response validation

Spec-Driven: Generated from SmartLead/harness.json testing_harness
"""

import pytest
from uuid import uuid4

from src.api.models import (
    LeadData,
    LeadScoreResponse,
    BatchScoreRequest,
    BatchScoreResponse,
    ErrorResponse
)


class TestLeadData:
    """Tests for LeadData model"""
    
    def test_valid_lead_data(self):
        """Test creating valid lead data"""
        lead_id = uuid4()
        lead = LeadData(
            lead_id=lead_id,
            email="test@example.com",
            company_size="1-10",
            industry="technology",
            job_title="CEO"
        )
        
        assert lead.lead_id == lead_id
        assert lead.email == "test@example.com"
        assert lead.company_size == "1-10"
    
    def test_email_validation(self):
        """Test email format validation"""
        with pytest.raises(ValueError):
            LeadData(
                lead_id=uuid4(),
                email="invalid-email",
                company_size="1-10",
                industry="technology",
                job_title="CEO"
            )
    
    def test_email_normalization(self):
        """Test email is normalized to lowercase"""
        lead = LeadData(
            lead_id=uuid4(),
            email="TEST@EXAMPLE.COM",
            company_size="1-10",
            industry="technology",
            job_title="CEO"
        )
        
        assert lead.email == "test@example.com"
    
    def test_optional_fields(self):
        """Test optional fields"""
        lead_id = uuid4()
        lead = LeadData(
            lead_id=lead_id,
            email="test@example.com",
            company_size="1-10",
            industry="technology",
            job_title="CEO",
            traffic_source="organic",
            country="US"
        )
        
        assert lead.traffic_source == "organic"
        assert lead.country == "US"


class TestLeadScoreResponse:
    """Tests for LeadScoreResponse model"""
    
    def test_valid_response(self):
        """Test creating valid lead score response"""
        lead_id = uuid4()
        response = LeadScoreResponse(
            lead_id=lead_id,
            conversion_probability=0.85,
            lead_grade="A",
            confidence_score=0.90,
            model_version="1.0.0",
            processing_time_ms=50.5
        )
        
        assert response.lead_id == lead_id
        assert response.conversion_probability == 0.85
        assert response.lead_grade == "A"
    
    def test_probability_bounds(self):
        """Test probability is bounded between 0 and 1"""
        with pytest.raises(ValueError):
            LeadScoreResponse(
                lead_id=uuid4(),
                conversion_probability=1.5,  # Invalid
                lead_grade="A",
                confidence_score=0.90,
                model_version="1.0.0",
                processing_time_ms=50.5
            )
        
        with pytest.raises(ValueError):
            LeadScoreResponse(
                lead_id=uuid4(),
                conversion_probability=-0.5,  # Invalid
                lead_grade="A",
                confidence_score=0.90,
                model_version="1.0.0",
                processing_time_ms=50.5
            )


class TestBatchScoreRequest:
    """Tests for BatchScoreRequest model"""
    
    def test_valid_batch_request(self):
        """Test creating valid batch request"""
        leads = [
            LeadData(
                lead_id=uuid4(),
                email=f"test{i}@example.com",
                company_size="1-10",
                industry="technology",
                job_title="CEO"
            )
            for i in range(5)
        ]
        
        request = BatchScoreRequest(leads=leads)
        
        assert len(request.leads) == 5
    
    def test_empty_leads_validation(self):
        """Test validation rejects empty leads"""
        with pytest.raises(ValueError):
            BatchScoreRequest(leads=[])
    
    def test_max_leads_validation(self):
        """Test validation rejects too many leads"""
        leads = [
            LeadData(
                lead_id=uuid4(),
                email=f"test{i}@example.com",
                company_size="1-10",
                industry="technology",
                job_title="CEO"
            )
            for i in range(1001)  # Over max
        ]
        
        with pytest.raises(ValueError):
            BatchScoreRequest(leads=leads)


class TestErrorResponse:
    """Tests for ErrorResponse model"""
    
    def test_error_response_creation(self):
        """Test creating error response"""
        error = ErrorResponse(
            error="Test error",
            status_code=500,
            timestamp=1234567890.0
        )
        
        assert error.error == "Test error"
        assert error.status_code == 500
