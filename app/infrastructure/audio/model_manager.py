import os
import time
import logging
from typing import Tuple, Optional, Any

logger = logging.getLogger(__name__)


class ModelManager:
    """Singleton class to manage audio analysis models (basic_pitch)."""
    
    _instance = None
    _basic_pitch_predict = None
    _basic_pitch_model_path = None
    _model_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_basic_pitch(cls) -> Tuple[Any, str]:
        """
        Gets or initializes the basic_pitch model.
        
        Returns:
            Tuple[predict_function, model_path]: The predict function and model path
            
        Usage:
            predict, model_path = AudioModelManager.get_basic_pitch()
            model_output, midi, notes = predict(audio_path, model_or_model_path=model_path, ...)
        """
        instance = cls()
        if not instance._model_loaded:
            instance._initialize_basic_pitch()
        return instance._basic_pitch_predict, instance._basic_pitch_model_path
    
    def _initialize_basic_pitch(self):
        """Initializes the basic_pitch model with safe loading."""
        logger.info("Initializing basic_pitch model...")
        
        try:
            # Set TensorFlow environment for stability
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
            os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
            
            # Lazy import to avoid startup freeze
            from basic_pitch.inference import predict
            from basic_pitch import ICASSP_2022_MODEL_PATH
            
            # Store references
            self._basic_pitch_predict = predict
            self._basic_pitch_model_path = ICASSP_2022_MODEL_PATH
            self._model_loaded = True
            
            logger.info(f"basic_pitch model loaded successfully from: {ICASSP_2022_MODEL_PATH}")
            
        except Exception as e:
            logger.error(f"Failed to load basic_pitch model: {e}")
            raise RuntimeError(f"Unable to initialize basic_pitch model: {e}")
    
    @classmethod
    def is_loaded(cls) -> bool:
        """Check if the model is already loaded."""
        instance = cls()
        return instance._model_loaded
    
    @classmethod
    def reload(cls):
        """Force reload of the model."""
        instance = cls()
        instance._model_loaded = False
        instance._basic_pitch_predict = None
        instance._basic_pitch_model_path = None
        logger.info("Model cache cleared, will reload on next use")