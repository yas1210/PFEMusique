import sys
from unittest.mock import MagicMock

# Mock PyQt6 modules
sys.modules["PyQt6"] = MagicMock()
sys.modules["PyQt6.QtCore"] = MagicMock()
sys.modules["PyQt6.QtGui"] = MagicMock()

from core.models import InteractiveSquare