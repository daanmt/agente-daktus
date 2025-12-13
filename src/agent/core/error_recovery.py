"""
Error Recovery - Graceful error handling com retry logic.

Fase 1 do Roadmap 2025 - Quick Wins
Substitui sys.exit() abruptos por recovery inteligente.

Author: Claude Code (Anthropic)
Date: 2025-12-11
"""

import time
import sys
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass
from enum import Enum

from .logger import logger


class ErrorSeverity(Enum):
    """Níveis de severidade de erro."""
    LOW = "low"           # Aviso, continua normalmente
    MEDIUM = "medium"     # Tenta recovery, pode continuar degradado
    HIGH = "high"         # Tenta recovery, mas pode precisar abortar
    CRITICAL = "critical" # Erro fatal, mas pergunta ao usuário


@dataclass
class RecoveryResult:
    """Resultado de tentativa de recovery."""
    success: bool
    value: Optional[Any] = None
    error: Optional[Exception] = None
    attempts: int = 0
    recovery_method: Optional[str] = None


class ErrorRecovery:
    """
    Sistema de recovery gracioso de erros.

    Substitui sys.exit() por:
    - Retry automático com backoff exponencial
    - User prompts para decidir continuar
    - Graceful degradation quando possível
    - Logging estruturado de todos os erros

    Usage:
        recovery = ErrorRecovery()
        result = recovery.handle_error(
            error=exception,
            context="Loading protocol",
            max_retries=3
        )
        if not result.success:
            # Fallback ou abortar gracefully
    """

    def __init__(self, display_manager=None):
        """
        Inicializa error recovery.

        Args:
            display_manager: DisplayManager para UI feedback (opcional)
        """
        self.display = display_manager
        self.error_count = 0
        self.last_error_time = None

    def handle_error(
        self,
        error: Exception,
        context: str,
        max_retries: int = 3,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recovery_fn: Optional[Callable] = None,
        ask_user: bool = True
    ) -> RecoveryResult:
        """
        Trata erro de forma graceful.

        Args:
            error: Exceção capturada
            context: Contexto do erro (e.g., "Loading protocol")
            max_retries: Máximo de tentativas de retry
            severity: Nível de severidade do erro
            recovery_fn: Função opcional para tentar recovery
            ask_user: Se deve perguntar ao usuário o que fazer

        Returns:
            RecoveryResult com success=True se recuperou, False se não
        """
        self.error_count += 1
        self.last_error_time = time.time()

        # Log estruturado
        logger.error(
            f"Error in {context}: {type(error).__name__}: {str(error)}",
            exc_info=True,
            extra={
                "context": context,
                "severity": severity.value,
                "error_count": self.error_count
            }
        )

        # Trata baseado em severidade
        if severity == ErrorSeverity.CRITICAL:
            return self._handle_critical_error(error, context, ask_user)
        elif severity == ErrorSeverity.HIGH:
            return self._handle_high_error(error, context, max_retries, recovery_fn, ask_user)
        elif severity == ErrorSeverity.MEDIUM:
            return self._handle_medium_error(error, context, max_retries, recovery_fn)
        else:  # LOW
            return self._handle_low_error(error, context)

    def _handle_critical_error(
        self,
        error: Exception,
        context: str,
        ask_user: bool
    ) -> RecoveryResult:
        """Trata erro crítico - pergunta ao usuário."""
        if self.display:
            self.display.show_error(f"Erro crítico em {context}: {str(error)}")
        else:
            print(f"\n❌ ERRO CRÍTICO em {context}:")
            print(f"   {type(error).__name__}: {str(error)}")

        if not ask_user:
            logger.critical(f"Critical error in {context}, aborting")
            return RecoveryResult(
                success=False,
                error=error,
                attempts=0,
                recovery_method="abort"
            )

        # Pergunta ao usuário
        print("\nO que deseja fazer?")
        print("  1 - Tentar continuar (pode causar problemas)")
        print("  2 - Abortar operação")

        try:
            choice = input("\nEscolha (1/2): ").strip()
            if choice == "1":
                logger.warning(f"User chose to continue after critical error in {context}")
                return RecoveryResult(
                    success=True,  # Continua sob risco
                    value=None,
                    attempts=0,
                    recovery_method="user_continue"
                )
            else:
                logger.info(f"User chose to abort after critical error in {context}")
                return RecoveryResult(
                    success=False,
                    error=error,
                    attempts=0,
                    recovery_method="user_abort"
                )
        except (KeyboardInterrupt, EOFError):
            logger.info(f"User interrupted prompt, aborting")
            return RecoveryResult(
                success=False,
                error=error,
                attempts=0,
                recovery_method="user_interrupt"
            )

    def _handle_high_error(
        self,
        error: Exception,
        context: str,
        max_retries: int,
        recovery_fn: Optional[Callable],
        ask_user: bool
    ) -> RecoveryResult:
        """Trata erro high - retry com backoff."""
        if self.display:
            self.display.show_warning(f"Erro em {context}, tentando recovery...")
        else:
            print(f"\n⚠️  Erro em {context}: {str(error)}")
            print(f"   Tentando recovery...")

        # Tenta retry com backoff
        for attempt in range(1, max_retries + 1):
            if recovery_fn:
                try:
                    logger.info(f"Recovery attempt {attempt}/{max_retries} for {context}")
                    result = recovery_fn()
                    logger.info(f"Recovery successful on attempt {attempt}")
                    return RecoveryResult(
                        success=True,
                        value=result,
                        attempts=attempt,
                        recovery_method="retry_success"
                    )
                except Exception as retry_error:
                    logger.warning(
                        f"Recovery attempt {attempt} failed: {str(retry_error)}",
                        exc_info=True
                    )
                    if attempt < max_retries:
                        wait_time = min(5 * (2 ** (attempt - 1)), 30)  # Cap em 30s
                        if self.display:
                            self.display.show_info(f"Aguardando {wait_time}s antes de retry {attempt+1}...")
                        else:
                            print(f"   Aguardando {wait_time}s antes de retry {attempt+1}...")
                        time.sleep(wait_time)

        # Todas as tentativas falharam
        logger.error(f"All {max_retries} recovery attempts failed for {context}")

        if not ask_user:
            return RecoveryResult(
                success=False,
                error=error,
                attempts=max_retries,
                recovery_method="retry_exhausted"
            )

        # Pergunta ao usuário
        print(f"\n❌ Todas as {max_retries} tentativas de recovery falharam.")
        print("O que deseja fazer?")
        print("  1 - Continuar sem esta operação (modo degradado)")
        print("  2 - Abortar")

        try:
            choice = input("\nEscolha (1/2): ").strip()
            if choice == "1":
                logger.warning(f"User chose degraded mode after {context} failures")
                return RecoveryResult(
                    success=True,  # Continua degradado
                    value=None,
                    attempts=max_retries,
                    recovery_method="degraded_mode"
                )
            else:
                logger.info(f"User chose to abort after {context} failures")
                return RecoveryResult(
                    success=False,
                    error=error,
                    attempts=max_retries,
                    recovery_method="user_abort"
                )
        except (KeyboardInterrupt, EOFError):
            return RecoveryResult(
                success=False,
                error=error,
                attempts=max_retries,
                recovery_method="user_interrupt"
            )

    def _handle_medium_error(
        self,
        error: Exception,
        context: str,
        max_retries: int,
        recovery_fn: Optional[Callable]
    ) -> RecoveryResult:
        """Trata erro medium - retry automático."""
        if self.display:
            self.display.show_warning(f"Erro em {context}, tentando novamente...")
        else:
            print(f"\n⚠️  Erro em {context}, tentando novamente...")

        if not recovery_fn:
            # Sem recovery function, apenas log e continua
            return RecoveryResult(
                success=False,
                error=error,
                attempts=0,
                recovery_method="no_recovery_fn"
            )

        # Retry automático sem perguntar ao usuário
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Auto-retry attempt {attempt}/{max_retries} for {context}")
                result = recovery_fn()
                logger.info(f"Auto-retry successful on attempt {attempt}")
                return RecoveryResult(
                    success=True,
                    value=result,
                    attempts=attempt,
                    recovery_method="auto_retry_success"
                )
            except Exception as retry_error:
                logger.warning(
                    f"Auto-retry attempt {attempt} failed: {str(retry_error)}"
                )
                if attempt < max_retries:
                    wait_time = min(3 * attempt, 15)  # Cap em 15s
                    time.sleep(wait_time)

        # Falhou
        logger.error(f"All {max_retries} auto-retry attempts failed for {context}")
        return RecoveryResult(
            success=False,
            error=error,
            attempts=max_retries,
            recovery_method="auto_retry_exhausted"
        )

    def _handle_low_error(
        self,
        error: Exception,
        context: str
    ) -> RecoveryResult:
        """Trata erro low - apenas log e continua."""
        if self.display:
            self.display.show_warning(f"Aviso em {context}: {str(error)}")
        else:
            print(f"\n⚠️  Aviso em {context}: {str(error)}")

        logger.warning(f"Low severity error in {context}: {str(error)}")

        return RecoveryResult(
            success=True,  # Continua normalmente
            value=None,
            attempts=0,
            recovery_method="logged_and_continue"
        )

    def graceful_exit(
        self,
        message: str = "Encerrando aplicação...",
        exit_code: int = 0
    ):
        """
        Encerra aplicação gracefully (substitui sys.exit).

        Args:
            message: Mensagem de despedida
            exit_code: Código de saída (0 = sucesso, >0 = erro)
        """
        if self.display:
            if exit_code == 0:
                self.display.show_success(message)
            else:
                self.display.show_error(message)
        else:
            print(f"\n{'✅' if exit_code == 0 else '❌'} {message}")

        logger.info(f"Graceful exit: {message} (code: {exit_code})")

        # Cleanup (se necessário)
        # - Fechar conexões
        # - Salvar estado
        # - Flush logs

        sys.exit(exit_code)


# Singleton global para uso conveniente
_global_recovery = None


def get_error_recovery(display_manager=None) -> ErrorRecovery:
    """
    Obtém instância global de ErrorRecovery.

    Args:
        display_manager: DisplayManager (apenas na primeira chamada)

    Returns:
        Instância de ErrorRecovery
    """
    global _global_recovery
    if _global_recovery is None:
        _global_recovery = ErrorRecovery(display_manager)
    return _global_recovery


# Função helper para retry rápido
def retry_on_error(
    fn: Callable,
    max_retries: int = 3,
    context: str = "operation",
    backoff_base: float = 2.0
) -> Any:
    """
    Executa função com retry automático.

    Args:
        fn: Função a executar
        max_retries: Máximo de tentativas
        context: Contexto para logging
        backoff_base: Base para backoff exponencial

    Returns:
        Resultado da função

    Raises:
        Exception se todas as tentativas falharem
    """
    for attempt in range(1, max_retries + 1):
        try:
            return fn()
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"All {max_retries} retries exhausted for {context}")
                raise

            wait_time = min(backoff_base ** attempt, 30)
            logger.warning(
                f"Retry {attempt}/{max_retries} for {context} failed, "
                f"waiting {wait_time}s: {str(e)}"
            )
            time.sleep(wait_time)
