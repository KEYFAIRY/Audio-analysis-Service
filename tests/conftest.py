import sys
from unittest.mock import MagicMock

# Mock de módulos de audio
sys.modules['app.infrastructure.audio.model_manager'] = MagicMock()
sys.modules['app.infrastructure.audio.analyzer'] = MagicMock()
sys.modules['app.infrastructure.audio.utils.time_utils'] = MagicMock()
sys.modules['app.infrastructure.audio.utils.note_utils'] = MagicMock()