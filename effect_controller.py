#!/usr/bin/env python3
"""
Base Effect Controller Class

Provides the base class for all effect controllers to avoid circular imports.
"""

from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from audio_processor import AudioProcessor


class EffectController:
    """Base class for effect controllers."""
    
    def __init__(self, name: str, audio_processor: 'AudioProcessor'):
        self.name = name
        self.audio_processor = audio_processor
        self.is_active = False
        
    def start(self):
        """Start the effect."""
        self.audio_processor.start_effect(self.name)
        self.is_active = self.name in self.audio_processor.active_effects
        
    def stop(self):
        """Stop the effect."""
        self.audio_processor.stop_effect(self.name)
        self.is_active = self.name in self.audio_processor.active_effects
        
    def get_status(self) -> Dict[str, Any]:
        """Get effect status."""
        return self.audio_processor.get_effect_status(self.name)
        
    def get_help(self) -> str:
        """Get effect-specific help."""
        return f"Help for {self.name} effect"
