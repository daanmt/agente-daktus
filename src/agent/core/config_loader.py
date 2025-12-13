"""
Config Loader - Carregamento de configurações externas.

Responsabilidades:
- Carregar config.yaml com valores default
- Validar configurações com Pydantic
- Fornecer acesso global às configurações
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from functools import lru_cache
import yaml

from pydantic import BaseModel, Field, field_validator


class LLMConfig(BaseModel):
    """Configurações de LLM."""
    analysis_model: str = "google/gemini-2.5-flash-lite"
    reconstruction_model: str = "google/gemini-2.5-flash-lite"
    analysis_temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    reconstruction_temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    max_tokens: int = Field(default=8192, ge=1000, le=100000)
    api_timeout: int = Field(default=120, ge=30, le=600)


class CostControlConfig(BaseModel):
    """Configurações de controle de custo."""
    session_warning_threshold: float = Field(default=0.50, ge=0.0)
    session_max_cost: float = Field(default=0.0, ge=0.0)
    show_cost_estimates: bool = True
    show_realtime_cost: bool = True


class AnalysisConfig(BaseModel):
    """Configurações de análise."""
    min_suggestions: int = Field(default=5, ge=1)
    max_suggestions: int = Field(default=60, ge=10)
    learned_filter_threshold: int = Field(default=1, ge=1)
    validate_playbook_references: bool = True
    block_generic_suggestions: bool = True


class ReconstructionConfig(BaseModel):
    """Configurações de reconstrução."""
    use_chunking: bool = True
    chunk_size_kb: int = Field(default=30, ge=10, le=100)
    max_section_retries: int = Field(default=3, ge=1, le=10)
    generate_audit_report: bool = True
    add_changelog_to_nodes: bool = True


class FeedbackConfig(BaseModel):
    """Configurações de feedback e aprendizado."""
    memory_file: str = "memory_qa.md"
    max_active_patterns: int = Field(default=100, ge=10)
    pattern_expiry_days: int = Field(default=90, ge=7)
    auto_backup_sessions: bool = True


class PathsConfig(BaseModel):
    """Configurações de caminhos."""
    protocols_dir: str = "models_json"
    playbooks_dir: str = "biblioteca_clinica/playbooks"
    reports_dir: str = "reports"
    logs_dir: str = "logs"
    feedback_sessions_dir: str = "feedback_sessions"


class CLIConfig(BaseModel):
    """Configurações de CLI."""
    colorize_output: bool = True
    show_progress_bars: bool = True
    show_thinking_messages: bool = True
    input_timeout: int = Field(default=0, ge=0)
    suggestions_per_page: int = Field(default=10, ge=5, le=50)


class SessionConfig(BaseModel):
    """Configurações de sessão e recovery."""
    enable_checkpoints: bool = True
    checkpoint_dir: str = ".session_checkpoints"
    checkpoint_interval: int = Field(default=60, ge=10)
    max_checkpoints: int = Field(default=5, ge=1, le=20)
    prompt_for_recovery: bool = True


class LoggingConfig(BaseModel):
    """Configurações de logging."""
    level: str = "INFO"
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    rotation_days: int = Field(default=7, ge=1)
    max_log_size_mb: int = Field(default=10, ge=1, le=100)
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()


class AppConfig(BaseModel):
    """Configuração completa do aplicativo."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    cost_control: CostControlConfig = Field(default_factory=CostControlConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    reconstruction: ReconstructionConfig = Field(default_factory=ReconstructionConfig)
    feedback: FeedbackConfig = Field(default_factory=FeedbackConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    cli: CLIConfig = Field(default_factory=CLIConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def find_config_file() -> Optional[Path]:
    """
    Encontra arquivo de configuração.
    
    Procura em ordem:
    1. Variável de ambiente DAKTUS_CONFIG
    2. config.yaml no diretório atual
    3. config.yaml no diretório do projeto
    """
    # 1. Variável de ambiente
    env_path = os.environ.get('DAKTUS_CONFIG')
    if env_path and Path(env_path).exists():
        return Path(env_path)
    
    # 2. Diretório atual
    cwd_config = Path.cwd() / 'config.yaml'
    if cwd_config.exists():
        return cwd_config
    
    # 3. Diretório do projeto (onde está este arquivo)
    project_root = Path(__file__).parent.parent.parent.parent
    project_config = project_root / 'config.yaml'
    if project_config.exists():
        return project_config
    
    return None


@lru_cache(maxsize=1)
def load_config() -> AppConfig:
    """
    Carrega e valida configuração.
    
    Returns:
        AppConfig com valores do arquivo ou defaults
    """
    config_path = find_config_file()
    
    if config_path:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f) or {}
            
            return AppConfig(**yaml_data)
        except Exception as e:
            print(f"⚠️ Erro ao carregar {config_path}: {e}")
            print("   Usando configurações padrão.")
    
    # Retorna defaults se não encontrou arquivo
    return AppConfig()


def get_config() -> AppConfig:
    """
    Retorna configuração global (cached).
    
    Use reload_config() para forçar recarga.
    """
    return load_config()


def reload_config() -> AppConfig:
    """
    Força recarga da configuração do disco.
    
    Returns:
        AppConfig atualizada
    """
    load_config.cache_clear()
    return load_config()


# Singleton para acesso fácil
config = get_config()
