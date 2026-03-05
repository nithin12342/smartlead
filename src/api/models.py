"""
SmartLead API Models
====================
Pydantic models for API request/response validation
"""

from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class LeadData(BaseModel):
    """Lead data for scoring"""
    
    lead_id: UUID = Field(..., description="Unique lead identifier")
    email: str = Field(..., description="Lead email address")
    company_size: str = Field(..., description="Company size (e.g., 1-10, 11-50, 51-200)")
    industry: str = Field(..., description="Industry sector")
    job_title: str = Field(..., description="Job title")
    traffic_source: Optional[str] = Field(None, description="Source of lead (e.g., organic, paid)")
    country: Optional[str] = Field(None, description="Country")
    city: Optional[str] = Field(None, description="City")
    phone: Optional[str] = Field(None, description="Phone number")
    annual_revenue: Optional[str] = Field(None, description="Annual revenue range")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format"""
        if '@' not in v:
            raise ValueError("Invalid email format")
        return v.lower()
    
    @field_validator('company_size')
    @classmethod
    def validate_company_size(cls, v: str) -> str:
        """Validate company size"""
        valid_sizes = ['1-10', '11-50', '51-200', '201-500', '501-1000', '1000+']
        if v not in valid_sizes:
            # Allow any but normalize
            return v
        return v


class LeadScoreResponse(BaseModel):
    """Response for single lead scoring"""
    
    lead_id: UUID
    conversion_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of conversion")
    lead_grade: str = Field(..., description="Lead grade (A, B, C, D)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Model confidence")
    model_version: str
    shap_explanation: Optional[Dict] = Field(None, description="SHAP values for explanation")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class BatchScoreRequest(BaseModel):
    """Request for batch lead scoring"""
    
    leads: List[LeadData] = Field(..., min_length=1, max_length=1000)
    
    @field_validator('leads')
    @classmethod
    def validate_leads_not_empty(cls, v: List[LeadData]) -> List[LeadData]:
        """Validate leads list is not empty"""
        if not v:
            raise ValueError("Leads list cannot be empty")
        return v


class BatchScoreResponse(BaseModel):
    """Response for batch lead scoring"""
    
    total_leads: int
    scored_leads: int
    results: List[LeadScoreResponse]
    processing_time_ms: float


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str
    service: str
    version: str
    timestamp: float
    model: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    
    error: str
    status_code: int
    timestamp: float
    details: Optional[Dict] = None
