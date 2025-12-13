"""
Session State - Estado de sessão com checkpoints.

Responsabilidades:
- Salvar checkpoints automáticos durante operações longas
- Permitir recovery após crash/interrupção
- Manter histórico de ações da sessão
"""

import json
import time
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib

from .logger import logger


@dataclass
class SessionCheckpoint:
    """Checkpoint de sessão."""
    checkpoint_id: str
    timestamp: str
    stage: str
    protocol_name: Optional[str] = None
    protocol_version: Optional[str] = None
    suggestions_count: int = 0
    approved_suggestions: List[str] = field(default_factory=list)
    rejected_suggestions: List[str] = field(default_factory=list)
    current_suggestion_index: int = 0
    analysis_complete: bool = False
    feedback_complete: bool = False
    reconstruction_complete: bool = False
    data: Dict[str, Any] = field(default_factory=dict)


class SessionState:
    """
    Gerenciador de estado de sessão com checkpoints.
    
    Permite:
    - Salvar estado atual para recovery
    - Carregar sessão anterior após crash
    - Rastrear progresso de operações
    """
    
    STAGES = [
        "welcome",
        "onboarding", 
        "analysis",
        "results",
        "feedback",
        "reconstruction",
        "complete"
    ]
    
    def __init__(
        self,
        checkpoint_dir: str = ".session_checkpoints",
        max_checkpoints: int = 5,
        auto_checkpoint_interval: int = 60
    ):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.max_checkpoints = max_checkpoints
        self.auto_checkpoint_interval = auto_checkpoint_interval
        self._last_checkpoint_time = 0
        
        # Estado atual
        self.session_id = self._generate_session_id()
        self.stage = "welcome"
        self.protocol_name: Optional[str] = None
        self.protocol_version: Optional[str] = None
        self.suggestions: List[Dict] = []
        self.approved_suggestions: List[str] = []
        self.rejected_suggestions: List[str] = []
        self.current_suggestion_index: int = 0
        self.analysis_result: Optional[Dict] = None
        self.reconstruction_result: Optional[Dict] = None
        self.custom_data: Dict[str, Any] = {}
        
        # Garante que diretório existe
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_session_id(self) -> str:
        """Gera ID único para sessão."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_part = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"session_{timestamp}_{random_part}"
    
    def set_stage(self, stage: str):
        """
        Define estágio atual.
        
        Args:
            stage: Nome do estágio (deve estar em STAGES)
        """
        if stage not in self.STAGES:
            logger.warning(f"Unknown stage: {stage}. Continuing anyway.")
        
        old_stage = self.stage
        self.stage = stage
        logger.debug(f"Session stage: {old_stage} → {stage}")
        
        # Auto checkpoint em mudança de estágio importante
        if stage in ["feedback", "reconstruction"]:
            self.save_checkpoint()
    
    def set_protocol(self, name: str, version: str):
        """Define protocolo sendo processado."""
        self.protocol_name = name
        self.protocol_version = version
    
    def set_suggestions(self, suggestions: List[Dict]):
        """Define sugestões da análise."""
        self.suggestions = suggestions
        self.current_suggestion_index = 0
    
    def approve_suggestion(self, suggestion_id: str):
        """Marca sugestão como aprovada."""
        if suggestion_id not in self.approved_suggestions:
            self.approved_suggestions.append(suggestion_id)
        if suggestion_id in self.rejected_suggestions:
            self.rejected_suggestions.remove(suggestion_id)
    
    def reject_suggestion(self, suggestion_id: str):
        """Marca sugestão como rejeitada."""
        if suggestion_id not in self.rejected_suggestions:
            self.rejected_suggestions.append(suggestion_id)
        if suggestion_id in self.approved_suggestions:
            self.approved_suggestions.remove(suggestion_id)
    
    def advance_suggestion_index(self):
        """Avança índice de sugestão atual."""
        self.current_suggestion_index += 1
    
    def set_custom_data(self, key: str, value: Any):
        """Armazena dados customizados."""
        self.custom_data[key] = value
    
    def get_custom_data(self, key: str, default: Any = None) -> Any:
        """Recupera dados customizados."""
        return self.custom_data.get(key, default)
    
    def should_auto_checkpoint(self) -> bool:
        """Verifica se deve fazer checkpoint automático."""
        elapsed = time.time() - self._last_checkpoint_time
        return elapsed >= self.auto_checkpoint_interval
    
    def save_checkpoint(self, force: bool = False) -> Optional[Path]:
        """
        Salva checkpoint atual.
        
        Args:
            force: Se True, salva mesmo que intervalo não tenha passado
            
        Returns:
            Path do checkpoint ou None se não salvou
        """
        if not force and not self.should_auto_checkpoint():
            return None
        
        checkpoint = SessionCheckpoint(
            checkpoint_id=f"{self.session_id}_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            stage=self.stage,
            protocol_name=self.protocol_name,
            protocol_version=self.protocol_version,
            suggestions_count=len(self.suggestions),
            approved_suggestions=self.approved_suggestions.copy(),
            rejected_suggestions=self.rejected_suggestions.copy(),
            current_suggestion_index=self.current_suggestion_index,
            analysis_complete=self.stage in ["results", "feedback", "reconstruction", "complete"],
            feedback_complete=self.stage in ["reconstruction", "complete"],
            reconstruction_complete=self.stage == "complete",
            data={
                "custom_data": self.custom_data,
                "session_id": self.session_id
            }
        )
        
        checkpoint_path = self.checkpoint_dir / f"{checkpoint.checkpoint_id}.json"
        
        try:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(checkpoint), f, ensure_ascii=False, indent=2)
            
            self._last_checkpoint_time = time.time()
            logger.debug(f"Checkpoint saved: {checkpoint_path}")
            
            # Limpa checkpoints antigos
            self._cleanup_old_checkpoints()
            
            return checkpoint_path
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            return None
    
    def _cleanup_old_checkpoints(self):
        """Remove checkpoints antigos além do limite."""
        try:
            checkpoints = sorted(
                self.checkpoint_dir.glob("session_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            for old_checkpoint in checkpoints[self.max_checkpoints:]:
                old_checkpoint.unlink()
                logger.debug(f"Removed old checkpoint: {old_checkpoint}")
                
        except Exception as e:
            logger.warning(f"Failed to cleanup checkpoints: {e}")
    
    def get_latest_checkpoint(self) -> Optional[SessionCheckpoint]:
        """
        Obtém checkpoint mais recente.
        
        Returns:
            SessionCheckpoint ou None se não existir
        """
        try:
            checkpoints = sorted(
                self.checkpoint_dir.glob("session_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            if not checkpoints:
                return None
            
            with open(checkpoints[0], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return SessionCheckpoint(**data)
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None
    
    def restore_from_checkpoint(self, checkpoint: SessionCheckpoint) -> bool:
        """
        Restaura estado de um checkpoint.
        
        Args:
            checkpoint: Checkpoint a restaurar
            
        Returns:
            True se restaurou com sucesso
        """
        try:
            self.stage = checkpoint.stage
            self.protocol_name = checkpoint.protocol_name
            self.protocol_version = checkpoint.protocol_version
            self.approved_suggestions = checkpoint.approved_suggestions.copy()
            self.rejected_suggestions = checkpoint.rejected_suggestions.copy()
            self.current_suggestion_index = checkpoint.current_suggestion_index
            
            if "custom_data" in checkpoint.data:
                self.custom_data = checkpoint.data["custom_data"]
            if "session_id" in checkpoint.data:
                self.session_id = checkpoint.data["session_id"]
            
            logger.info(f"Restored session from checkpoint: {checkpoint.checkpoint_id}")
            logger.info(f"  Stage: {self.stage}")
            logger.info(f"  Protocol: {self.protocol_name} v{self.protocol_version}")
            logger.info(f"  Progress: {self.current_suggestion_index}/{checkpoint.suggestions_count}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore checkpoint: {e}")
            return False
    
    def prompt_for_recovery(self) -> bool:
        """
        Pergunta ao usuário se quer recuperar sessão anterior.
        
        Returns:
            True se usuário quer recuperar
        """
        checkpoint = self.get_latest_checkpoint()
        
        if not checkpoint:
            return False
        
        # Verifica se checkpoint é recente (menos de 24h)
        try:
            checkpoint_time = datetime.fromisoformat(checkpoint.timestamp)
            age = datetime.now() - checkpoint_time
            
            if age.total_seconds() > 86400:  # 24 horas
                logger.info("Checkpoint muito antigo, ignorando")
                return False
                
        except:
            pass
        
        print("\n" + "="*60)
        print("🔄 SESSÃO ANTERIOR ENCONTRADA")
        print("="*60)
        print(f"  Protocolo: {checkpoint.protocol_name} v{checkpoint.protocol_version}")
        print(f"  Estágio: {checkpoint.stage}")
        print(f"  Progresso: {checkpoint.current_suggestion_index} de {checkpoint.suggestions_count} sugestões")
        print(f"  Aprovadas: {len(checkpoint.approved_suggestions)}")
        print(f"  Rejeitadas: {len(checkpoint.rejected_suggestions)}")
        print(f"  Timestamp: {checkpoint.timestamp}")
        print("="*60)
        
        try:
            choice = input("\nDeseja continuar sessão anterior? (S/N): ").strip().upper()
            
            if choice == 'S':
                return self.restore_from_checkpoint(checkpoint)
            else:
                logger.info("Usuário escolheu iniciar nova sessão")
                return False
                
        except (KeyboardInterrupt, EOFError):
            return False
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Retorna resumo do progresso atual."""
        return {
            "session_id": self.session_id,
            "stage": self.stage,
            "protocol": f"{self.protocol_name} v{self.protocol_version}" if self.protocol_name else None,
            "suggestions_total": len(self.suggestions),
            "suggestions_reviewed": self.current_suggestion_index,
            "suggestions_approved": len(self.approved_suggestions),
            "suggestions_rejected": len(self.rejected_suggestions),
            "analysis_complete": self.analysis_result is not None,
            "reconstruction_complete": self.reconstruction_result is not None
        }


# Singleton global
_session_state: Optional[SessionState] = None


def get_session_state(
    checkpoint_dir: str = ".session_checkpoints"
) -> SessionState:
    """Retorna instância global do SessionState."""
    global _session_state
    if _session_state is None:
        _session_state = SessionState(checkpoint_dir=checkpoint_dir)
    return _session_state


def reset_session_state():
    """Reseta estado global para nova sessão."""
    global _session_state
    _session_state = None
