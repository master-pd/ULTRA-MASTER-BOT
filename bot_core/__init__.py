"""
MASTER 🪓 ULTRA BOT - Core Package
Advanced AI Bot with Self-Learning Capabilities
"""

__version__ = "4.0.0"
__author__ = "RANA (MASTER 🪓)"
__license__ = "MIT"

from .master_ultra import UltraMasterBot
from .facebook_ultra import FacebookUltra
from .diagram_generator import DiagramGenerator
from .image_creator import ImageCreator
from .bengali_nlp_advanced import BengaliNLP
from .firebase_ultra import FirebaseUltra
from .cloudinary_pro import CloudinaryPro
from .memory_ultra import MemoryUltra
from .security_ultra import SecurityLayer

__all__ = [
    "UltraMasterBot",
    "FacebookUltra",
    "DiagramGenerator",
    "ImageCreator",
    "BengaliNLP",
    "FirebaseUltra",
    "CloudinaryPro",
    "MemoryUltra",
    "SecurityLayer"
]