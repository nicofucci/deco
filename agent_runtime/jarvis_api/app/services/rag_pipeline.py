import PyPDF2
import docx
from typing import List, Dict, Any
from pathlib import Path
import hashlib

class JarvisRAGPipeline:
    """Pipeline RAG para ingesta y procesamiento de documentos."""
    
    def __init__(self, ollama_client, qdrant_memory):
        self.ollama = ollama_client
        self.qdrant = qdrant_memory
    
    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extrae texto de PDF con metadatos de página."""
        chunks = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        chunks.append({
                            "text": text,
                            "page": page_num,
                            "source": Path(file_path).name
                        })
        except Exception as e:
            print(f"[RAG] Error extrayendo PDF: {e}")
        return chunks
    
    def extract_text_from_docx(self, file_path: str) -> List[Dict[str, Any]]:
        """Extrae texto de DOCX."""
        chunks = []
        try:
            doc = docx.Document(file_path)
            full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            if full_text:
                chunks.append({
                    "text": full_text,
                    "source": Path(file_path).name
                })
        except Exception as e:
            print(f"[RAG] Error extrayendo DOCX: {e}")
        return chunks
    
    def extract_text_from_txt(self, file_path: str) -> List[Dict[str, Any]]:
        """Extrae texto plano."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return [{
                "text": text,
                "source": Path(file_path).name
            }]
        except Exception as e:
            print(f"[RAG] Error extrayendo TXT: {e}")
            return []
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Divide texto en chunks con overlap."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def ingest_document(self, file_path: str) -> Dict[str, Any]:
        """Ingesta documento completo."""
        file_ext = Path(file_path).suffix.lower()
        
        # Extracción
        if file_ext == '.pdf':
            raw_chunks = self.extract_text_from_pdf(file_path)
        elif file_ext == '.docx':
            raw_chunks = self.extract_text_from_docx(file_path)
        elif file_ext in ['.txt', '.md']:
            raw_chunks = self.extract_text_from_txt(file_path)
        else:
            return {"error": f"Formato no soportado: {file_ext}"}
        
        # Chunking y embedding
        stored_ids = []
        for raw_chunk in raw_chunks:
            sub_chunks = self.chunk_text(raw_chunk["text"])
            
            for idx, chunk_text in enumerate(sub_chunks):
                # Generar embedding
                embedding = self.ollama.generate_embedding(chunk_text)
                if not embedding:
                    continue
                
                # Almacenar en Qdrant
                metadata = {
                    "source": raw_chunk["source"],
                    "page": raw_chunk.get("page"),
                    "chunk_id": idx,
                    "chunk_hash": hashlib.md5(chunk_text.encode()).hexdigest()
                }
                
                point_id = self.qdrant.store_knowledge(
                    text=chunk_text,
                    embedding=embedding,
                    metadata=metadata
                )
                stored_ids.append(point_id)
        
        return {
            "status": "success",
            "document": Path(file_path).name,
            "chunks_stored": len(stored_ids),
            "ids": stored_ids[:5]  # Solo primeros 5 IDs
        }
    
    def query_knowledge(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Consulta base de conocimiento con síntesis."""
        # Generar embedding de pregunta
        query_embedding = self.ollama.generate_embedding(question)
        if not query_embedding:
            return {"error": "No se pudo generar embedding de pregunta"}
        
        # Buscar contexto relevante
        results = self.qdrant.search_knowledge(
            query_embedding=query_embedding,
            limit=top_k,
            score_threshold=0.6
        )
        
        if not results:
            return {
                "answer": "No encontré información relevante en mi base de conocimiento.",
                "sources": []
            }
        
        # Construir contexto
        context = "\n\n---\n\n".join([
            f"[Fuente: {r['source']}, Página: {r.get('page', 'N/A')}]\n{r['text']}"
            for r in results
        ])
        
        # Sintetizar con LLM
        messages = [
            {
                "role": "system",
                "content": "Eres Jarvis, un asistente experto. Responde la pregunta usando SOLO la información del contexto. Cita fuentes."
            },
            {
                "role": "user",
                "content": f"Contexto:\n{context}\n\nPregunta: {question}"
            }
        ]
        
        llm_response = self.ollama.chat(messages=messages)
        answer = llm_response.get("message", {}).get("content", "Error generando respuesta")
        
        return {
            "answer": answer,
            "sources": [
                {"source": r["source"], "page": r.get("page"), "score": round(r["score"], 3)}
                for r in results
            ]
        }
