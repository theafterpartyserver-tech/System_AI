"""
LLM Integration - Load and manage GGUF models with llama-cpp-python
"""

from pathlib import Path
from typing import Optional, Dict, List
import json

class LLMManager:
    """Manage GGUF model loading and inference"""
    
    def __init__(self, models_dir: Path = None, config_path: Path = None):
        self.models_dir = models_dir or Path('./models')
        self.config_path = config_path or Path('./config/config.json')
        self.models = {}
        self.current_model = None
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load system configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {}
    
    def discover_models(self) -> List[str]:
        """Discover available GGUF models"""
        if not self.models_dir.exists():
            return []
        
        models = [f.stem for f in self.models_dir.glob('*.gguf')]
        return models
    
    def load_model(self, model_name: str) -> bool:
        """Load a GGUF model"""
        try:
            from llama_cpp import Llama
            
            model_path = self.models_dir / f"{model_name}.gguf"
            if not model_path.exists():
                print(f"Model not found: {model_path}")
                return False
            
            llm = Llama(
                model_path=str(model_path),
                n_ctx=self.config.get('context_length', 512),
                n_threads=6,
                n_gpu_layers=20,
                verbose=False,
            )
            
            self.models[model_name] = llm
            self.current_model = model_name
            print(f"Loaded model: {model_name}")
            return True
        except ImportError:
            print("llama-cpp-python not available")
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def generate(self, prompt: str, model: Optional[str] = None, 
                max_tokens: int = 256) -> str:
        """Generate text using loaded model"""
        if model:
            if model not in self.models:
                self.load_model(model)
            llm = self.models.get(model)
        else:
            if not self.current_model or self.current_model not in self.models:
                print("No model loaded")
                return ""
            llm = self.models[self.current_model]
        
        try:
            output = llm(prompt, max_tokens=max_tokens, echo=False)
            return output.get('choices', [{}])[0].get('text', '').strip()
        except Exception as e:
            print(f"Error generating: {e}")
            return ""
    
    def get_model_info(self) -> dict:
        """Get information about loaded models"""
        return {
            "available_models": self.discover_models(),
            "loaded_models": list(self.models.keys()),
            "current_model": self.current_model
        }

