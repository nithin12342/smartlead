"""
SmartLead Lead Predictor
========================
ML model for lead conversion prediction
"""

import logging
from typing import Any, Dict, Optional

import joblib
import numpy as np
import xgboost as xgb

from src.api.config import Settings

logger = logging.getLogger(__name__)


class LeadPredictor:
    """
    Lead conversion prediction model
    
    Uses XGBoost for prediction with SHAP explainability
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model: Optional[xgb.XGBClassifier] = None
        self.model_version = settings.model_version
        self._is_ready = False
        self._feature_names = [
            'company_size_encoded',
            'industry_encoded',
            'job_title_encoded',
            'traffic_source_encoded',
            'country_encoded',
            'email_domain_tld',
            'has_phone',
            'has_company_size',
            'email_length',
            'company_name_length'
        ]
    
    async def load_model(self) -> None:
        """Load the trained model from disk"""
        try:
            model_path = self.settings.model_path
            
            # Try to load model, use default if not exists
            try:
                self.model = joblib.load(model_path)
                logger.info(f"Loaded model from {model_path}")
            except FileNotFoundError:
                logger.warning(f"Model not found at {model_path}, creating default model")
                self._create_default_model()
            
            self._is_ready = True
            logger.info(f"LeadPredictor ready with version {self.model_version}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def _create_default_model(self) -> None:
        """Create a default XGBoost model for development"""
        # Create a simple model that can be used for testing
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            objective='binary:logistic',
            eval_metric='auc',
            use_label_encoder=False,
            n_jobs=-1
        )
        
        # Create dummy training data
        X = np.random.rand(100, len(self._feature_names))
        y = np.random.randint(0, 2, 100)
        
        # Fit the model
        self.model.fit(X, y)
    
    def is_ready(self) -> bool:
        """Check if model is ready for inference"""
        return self._is_ready and self.model is not None
    
    async def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction for lead features
        
        Args:
            features: Dictionary of extracted features
        
        Returns:
            Prediction results with probability, grade, and confidence
        """
        if not self.is_ready():
            raise RuntimeError("Model not loaded")
        
        try:
            # Convert features to model input
            X = self._prepare_features(features)
            
            # Get prediction
            probability = self.model.predict_proba(X)[0][1]
            
            # Get grade
            grade = self._get_grade(probability)
            
            # Calculate confidence (based on probability distance from 0.5)
            confidence = min(abs(probability - 0.5) * 2, 1.0)
            
            # Get SHAP values if available
            shap_values = self._get_shap_values(X)
            
            return {
                "probability": float(probability),
                "grade": grade,
                "confidence": float(confidence),
                "shap_values": shap_values
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise
    
    def _prepare_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepare features for model input"""
        # Extract feature values in correct order
        feature_values = []
        
        for feature_name in self._feature_names:
            value = features.get(feature_name, 0.0)
            feature_values.append(float(value))
        
        return np.array([feature_values])
    
    def _get_grade(self, probability: float) -> str:
        """Convert probability to lead grade"""
        if probability >= 0.8:
            return "A"
        elif probability >= 0.6:
            return "B"
        elif probability >= 0.4:
            return "C"
        else:
            return "D"
    
    def _get_shap_values(self, X: np.ndarray) -> Dict[str, float]:
        """Get SHAP values for explanation (simplified)"""
        # In production, use SHAP library
        # This is a simplified version
        feature_importance = self.model.feature_importances_
        
        shap_dict = {}
        for i, name in enumerate(self._feature_names):
            shap_dict[name] = float(feature_importance[i])
        
        return shap_dict
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        self.model = None
        self._is_ready = False
        logger.info("LeadPredictor cleanup complete")
