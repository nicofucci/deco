"""
Módulo de Voz de Jarvis 3.0
STT (Whisper), TTS (XTTS), Hotword Detection
"""

import asyncio
import io
import wave
from typing import Optional, AsyncGenerator
from pathlib import Path
import aiohttp
import numpy as np

class WhisperSTT:
    """Speech-to-Text usando Whisper."""
    
    def __init__(self, whisper_url: str = "http://localhost:9000"):
        self.whisper_url = whisper_url
        self.available = False
    
    async def check_availability(self) -> bool:
        """Verifica si Whisper server está disponible."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.whisper_url}/", timeout=5) as resp:
                    self.available = resp.status == 200
        except:
            self.available = False
        
        return self.available
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "es",
        task: str = "transcribe"
    ) -> dict:
        """
        Transcribe audio a texto.
        
        Args:
            audio_data: Audio en formato WAV
            language: Código de idioma (es, en, etc.)
            task: transcribe o translate
            
        Returns:
            {"text": "transcripción...", "language": "es"}
        """
        if not self.available:
            return {"error": "Whisper server no disponible"}
        
        try:
            data = aiohttp.FormData()
            data.add_field('audio_file',
                          audio_data,
                          filename='audio.wav',
                          content_type='audio/wav')
            data.add_field('language', language)
            data.add_field('task', task)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.whisper_url}/asr",
                    data=data,
                    timeout=30
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return {
                            "text": result.get("text", ""),
                            "language": result.get("language", language)
                        }
                    else:
                        return {"error": f"Whisper error: {resp.status}"}
        
        except Exception as e:
            return {"error": str(e)}


class XTTSTS:
    """Text-to-Speech usando XTTS."""
    
    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        self.model_name = model_name
        self.tts = None
        self.available = False
    
    def initialize(self):
        """Inicializa modelo TTS (requiere instalación previa)."""
        try:
            from TTS.api import TTS
            self.tts = TTS(self.model_name)
            self.available = True
            return True
        except ImportError:
            print("⚠️  TTS no instalado. Ejecutar: pip install TTS")
            return False
        except Exception as e:
            print(f"⚠️  Error inicializando TTS: {e}")
            return False
    
    async def synthesize(
        self,
        text: str,
        speaker_wav: Optional[str] = None,
        language: str = "es"
    ) -> bytes:
        """
        Sintetiza texto a voz.
        
        Args:
            text: Texto a sintetizar
            speaker_wav: Archivo de referencia de voz (clonación)
            language: Idioma
            
        Returns:
            Audio en bytes (WAV)
        """
        if not self.available:
            return b""
        
        try:
            # Generar en archivo temporal
            output_path = "/tmp/jarvis_tts_output.wav"
            
            if speaker_wav:
                # Clonación de voz
                self.tts.tts_to_file(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=language,
                    file_path=output_path
                )
            else:
                # Voz por defecto
                self.tts.tts_to_file(
                    text=text,
                    language=language,
                    file_path=output_path
                )
            
            # Leer archivo generado
            with open(output_path, 'rb') as f:
                audio_data = f.read()
            
            return audio_data
        
        except Exception as e:
            print(f"Error TTS: {e}")
            return b""


class HotwordDetector:
    """Detector de palabra clave 'Oye Jarvis'."""
    
    def __init__(self, sensitivity: float = 0.5):
        self.sensitivity = sensitivity
        self.detector = None
        self.available = False
    
    def initialize(self):
        """Inicializa detector de hotword."""
        try:
            import pvporcupine
            
            # Porcupine requiere access key
            # En producción: usar variable de entorno
            access_key = "PORCUPINE_ACCESS_KEY"  # Placeholder
            
            self.detector = pvporcupine.create(
                access_key=access_key,
                keywords=["jarvis"],  # Palabra clave
                sensitivities=[self.sensitivity]
            )
            self.available = True
            return True
        
        except ImportError:
            print("⚠️  Porcupine no instalado. Usar alternativa...")
            return self._initialize_alternative()
        except Exception as e:
            print(f"⚠️  Error hotword detector: {e}")
            return False
    
    def _initialize_alternative(self) -> bool:
        """Inicializa detector alternativo (umbral simple)."""
        # Detector básico usando Whisper mismo
        self.available = "alternative"
        return True
    
    async def detect(self, audio_chunk: bytes) -> bool:
        """
        Detecta si audio contiene hotword.
        
        Args:
            audio_chunk: Chunk de audio para analizar
            
        Returns:
            True si detectó hotword
        """
        if not self.available:
            return False
        
        if self.available == "alternative":
            # Método alternativo: transcribir y buscar palabra
            # Requiere Whisper STT
            return False  # Placeholder
        
        try:
            # Convertir bytes a formato de Porcupine
            # TODO: Implementar conversión
            pcm = self._bytes_to_pcm(audio_chunk)
            
            keyword_index = self.detector.process(pcm)
            return keyword_index >= 0
        
        except Exception as e:
            print(f"Error detección: {e}")
            return False
    
    def _bytes_to_pcm(self, audio_bytes: bytes) -> list:
        """Convierte bytes de audio a PCM."""
        # TODO: Implementar conversión
        return []


class VoiceConversationManager:
    """Gestor de conversaciones por voz continuas."""
    
    def __init__(self, stt: WhisperSTT, tts: XTTSTS, hotword: HotwordDetector):
        self.stt = stt
        self.tts = tts
        self.hotword = hotword
        self.conversation_active = False
        self.context = []
    
    async def listen_for_hotword(self) -> bool:
        """Escucha continuamente por hotword."""
        # TODO: Captura de audio en tiempo real
        # Requiere pyaudio o similar
        print("Esperando 'Oye Jarvis'...")
        return False
    
    async def start_conversation(self):
        """Inicia conversación por voz."""
        self.conversation_active = True
        self.context = []
        
        print("🎤 Jarvis escuchando...")
        
        # TODO: Capturar audio
        # audio_data = await self.capture_audio()
        
        # Transcribir
        # result = await self.stt.transcribe(audio_data)
        # user_text = result.get("text", "")
        
        # Procesar con Jarvis (LLM)
        # response_text = await self.process_with_jarvis(user_text)
        
        # Sintetizar respuesta
        # audio_response = await self.tts.synthesize(response_text)
        
        # Reproducir
        # await self.play_audio(audio_response)
    
    async def process_with_jarvis(self, text: str) -> str:
        """Procesa texto con Jarvis LLM."""
        # Integración con Ollama/Core Engine
        # TODO: Implementar
        return f"Procesando: {text}"
    
    async def capture_audio(self, duration: int = 5) -> bytes:
        """Captura audio del micrófono."""
        # TODO: Implementar con pyaudio
        return b""
    
    async def play_audio(self, audio_data: bytes):
        """Reproduce audio."""
        # TODO: Implementar con pyaudio
        pass


# API REST para voz
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

voice_router = APIRouter(prefix="/api/voice", tags=["voice"])

# Instancias globales
stt_engine = WhisperSTT()
tts_engine = XTTSTS()
hotword_detector = HotwordDetector()

@voice_router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe archivo de audio a texto."""
    if not await stt_engine.check_availability():
        raise HTTPException(
            status_code=503,
            detail="Servicio de transcripción no disponible"
        )
    
    audio_data = await file.read()
    result = await stt_engine.transcribe(audio_data)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@voice_router.post("/synthesize")
async def synthesize_speech(text: str, language: str = "es"):
    """Sintetiza texto a voz."""
    if not tts_engine.available:
        raise HTTPException(
            status_code=503,
            detail="Servicio TTS no disponible. Instalar con: pip install TTS"
        )
    
    audio_data = await tts_engine.synthesize(text, language=language)
    
    if not audio_data:
        raise HTTPException(status_code=500, detail="Error generando audio")
    
    return StreamingResponse(
        io.BytesIO(audio_data),
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=jarvis_speech.wav"}
    )

@voice_router.get("/status")
async def voice_status():
    """Estado de servicios de voz."""
    whisper_available = await stt_engine.check_availability()
    
    return {
        "whisper_stt": whisper_available,
        "xtts_tts": tts_engine.available,
        "hotword_detector": hotword_detector.available
    }
