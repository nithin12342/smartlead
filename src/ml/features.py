"""
SmartLead Feature Extractor
==========================
Feature engineering for lead scoring
"""

import logging
import re
from typing import Any, Dict

import redis.asyncio as redis

from src.api.config import Settings
from src.api.models import LeadData

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Feature extraction for lead data
    
    Extracts and transforms features from raw lead data
    """
    
    # Encoding mappings (in production, load from database)
    COMPANY_SIZE_MAP = {
        '1-10': 1,
        '11-50': 2,
        '51-200': 3,
        '201-500': 4,
        '501-1000': 5,
        '1000+': 6
    }
    
    INDUSTRY_MAP = {
        'technology': 1,
        'finance': 2,
        'healthcare': 3,
        'manufacturing': 4,
        'retail': 5,
        'education': 6,
        'other': 7
    }
    
    TRAFFIC_SOURCE_MAP = {
        'organic': 1,
        'paid': 2,
        'referral': 3,
        'social': 4,
        'email': 5,
        'direct': 6
    }
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.redis_client: redis.Redis = None
        self._is_ready = False
    
    async def initialize(self) -> None:
        """Initialize feature store connection"""
        try:
            # Connect to Redis
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            
            self._is_ready = True
            logger.info("FeatureExtractor initialized successfully")
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}, using in-memory features")
            self._is_ready = True
    
    def is_ready(self) -> bool:
        """Check if feature extractor is ready"""
        return self._is_ready
    
    async def extract_features(self, lead_data: LeadData) -> Dict[str, Any]:
        """
        Extract features from lead data
        
        Args:
            lead_data: Raw lead data
        
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Basic encoding features
        features['company_size_encoded'] = self._encode_company_size(lead_data.company_size)
        features['industry_encoded'] = self._encode_industry(lead_data.industry)
        features['job_title_encoded'] = self._encode_job_title(lead_data.job_title)
        features['traffic_source_encoded'] = self._encode_traffic_source(lead_data.traffic_source)
        features['country_encoded'] = self._encode_country(lead_data.country)
        
        # Derived features
        features['email_domain_tld'] = self._extract_tld(lead_data.email)
        features['has_phone'] = 1.0 if lead_data.phone else 0.0
        features['has_company_size'] = 1.0 if lead_data.company_size else 0.0
        features['email_length'] = float(len(lead_data.email))
        features['company_name_length'] = float(len(lead_data.email.split('@')[0]) if '@' in lead_data.email else 0)
        
        # Additional features
        features['email_local_part_length'] = float(len(lead_data.email.split('@')[0]) if '@' in lead_data.email else 0)
        features['has_annual_revenue'] = 1.0 if lead_data.annual_revenue else 0.0
        
        # Try to get cached features from Redis
        cached_features = await self._get_cached_features(lead_data.lead_id)
        if cached_features:
            features.update(cached_features)
        
        return features
    
    def _encode_company_size(self, company_size: str) -> float:
        """Encode company size"""
        return float(self.COMPANY_SIZE_MAP.get(company_size.lower(), 0))
    
    def _encode_industry(self, industry: str) -> float:
        """Encode industry"""
        return float(self.INDUSTRY_MAP.get(industry.lower(), 7))
    
    def _encode_job_title(self, job_title: str) -> float:
        """Encode job title based on seniority"""
        title_lower = job_title.lower()
        
        if any(word in title_lower for word in ['ceo', 'cto', 'cfo', 'founder', 'president']):
            return 5.0
        elif any(word in title_lower for word in ['vp', 'vice president', 'director']):
            return 4.0
        elif any(word in title_lower for word in ['manager', 'lead']):
            return 3.0
        elif any(word in title_lower for word in ['senior', 'sr.']):
            return 2.0
        else:
            return 1.0
    
    def _encode_traffic_source(self, traffic_source: str) -> float:
        """Encode traffic source"""
        if not traffic_source:
            return 0.0
        return float(self.TRAFFIC_SOURCE_MAP.get(traffic_source.lower(), 6))
    
    def _encode_country(self, country: str) -> float:
        """Encode country (simplified)"""
        if not country:
            return 0.0
        
        common_countries = {
            'us': 1, 'usa': 1, 'united states': 1,
            'uk': 2, 'united kingdom': 2,
            'ca': 3, 'canada': 3,
            'au': 4, 'australia': 4,
            'de': 5, 'germany': 5,
            'fr': 6, 'france': 6,
            'in': 7, 'india': 7
        }
        
        return float(common_countries.get(country.lower(), 10))
    
    def _extract_tld(self, email: str) -> float:
        """Extract TLD from email domain"""
        try:
            domain = email.split('@')[1] if '@' in email else ''
            tld = domain.split('.')[-1] if '.' in domain else ''
            
            common_tlds = {
                'com': 1, 'org': 2, 'net': 3,
                'io': 4, 'co': 5, 'ai': 6,
                'edu': 7, 'gov': 8
            }
            
            return float(common_tlds.get(tld.lower(), 10))
        except:
            return 0.0
    
    async def _get_cached_features(self, lead_id) -> Dict[str, Any]:
        """Get cached features from Redis"""
        try:
            if not self.redis_client:
                return {}
            
            cache_key = f"lead_features:{lead_id}"
            cached = await self.redis_client.get(cache_key)
            
            if cached:
                # Parse cached features
                import json
                return json.loads(cached)
            
        except Exception as e:
            logger.debug(f"Cache lookup failed: {str(e)}")
        
        return {}
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()
        self._is_ready = False
        logger.info("FeatureExtractor cleanup complete")
