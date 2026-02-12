"""
Placeholder para módulo de voz de Jarvis.
Requiere instalación de Whisper local o integración con servidor externo.

Funcionalidades planificadas:
- Hotword detection ("Hey Jarvis")
- Speech-to-Text (STT) con Whisper
- Text-to-Speech (TTS)
- Procesamiento de audio en tiempo real
"""

class JarvisVoiceModule:
    """
    Módulo de voz para Jarvis (PLACEHOLDER).
    
    Para habilitar:
    1. Instalar Whisper: pip install openai-whisper
    2. O usar servidor Whisper en Docker (puerto 9000)
    3. Para TTS: pip install pyttsx3 o gTTS
    """
    
    def __init__(self, whisper_url: str = "http://localhost:9000"):
        self.whisper_url = whisper_url
        self.enabled = False
    
    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio a texto.
        
        TODO: Implementar integración con Whisper
        """
        raise NotImplementedError("Módulo de voz no implementado todavía")
    
    def synthesize_speech(self, text: str) -> bytes:
        """
        Convierte texto a voz.
        
        TODO: Implementar TTS
        """
        raise NotImplementedError("TTS no implementado todavía")
    
    def detect_hotword(self, audio_stream) -> bool:
        """
        Detecta palabra clave ("Hey Jarvis").
        
        TODO: Implementar detección de hotword
        """
        raise NotImplementedError("Hotword detection no implementado")


# Guía de instalación:
"""
Para habilitar voz en Jarvis:

1. Whisper (STT):
   # Opción A: Local
   pip install openai-whisper
   
   # Opción B: Docker
   docker compose --profile with-voice up
   
2. TTS:
   pip install pyttsx3  # Linux: requiere espeak
   # o
   pip install gTTS

3. Hotword (opcional):
   pip install pvporcupine  # Requiere licencia

4. Integrar en main.py:
   from app.services.voice_module import JarvisVoiceModule
   
   @app.post("/api/voice/transcribe")
   async def transcribe(file: UploadFile):
       voice = JarvisVoiceModule()
       text = voice.transcribe_audio(file.filename)
       return {"text": text}
"""
