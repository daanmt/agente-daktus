"""
Feedback Collector - Captura de Feedback do Usuário

Responsabilidades:
- Apresentar sugestões ao usuário para revisão interativa
- Capturar feedback: Relevante | Irrelevante | Editar | Comentar
- Armazenar feedback estruturado para análise posterior

Este é o diferencial do V3 - Sistema de aprendizado contínuo baseado em feedback humano.

Fase de Implementação: FASE 2 (5-7 dias)
Status: ✅ Implementado
"""

import sys
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from ..core.logger import logger
from .feedback_storage import FeedbackStorage
from .memory_qa import MemoryQA
from .memory_engine import MemoryEngine


@dataclass
class SuggestionFeedback:
    """
    Feedback do usuário sobre uma sugestão específica.

    Attributes:
        suggestion_id: ID da sugestão
        user_verdict: "relevant", "irrelevant", "edited"
        user_comment: Comentário qualitativo opcional
        edited: Se sugestão foi editada
        edited_version: Versão editada da sugestão (se aplicável)
    """
    suggestion_id: str
    user_verdict: str  # relevant, irrelevant, edited
    user_comment: Optional[str] = None
    edited: bool = False
    edited_version: Optional[Dict] = None


@dataclass
class FeedbackSession:
    """
    Sessão completa de feedback do usuário.

    Attributes:
        session_id: ID único da sessão
        timestamp: Data/hora da sessão
        protocol_name: Nome do protocolo analisado
        model_used: Modelo LLM utilizado
        suggestions_feedback: Lista de feedbacks por sugestão
        general_feedback: Feedback geral sobre a análise
        quality_rating: Avaliação geral (0-10)
    """
    session_id: str
    timestamp: datetime
    protocol_name: str
    model_used: str
    suggestions_feedback: List[SuggestionFeedback]
    general_feedback: Optional[str] = None
    quality_rating: Optional[int] = None


class FeedbackCollector:
    """
    Coleta feedback do usuário sobre sugestões de melhoria.

    Este componente apresenta sugestões interativamente e captura
    feedback estruturado para o sistema de fine-tuning de prompts.

    Fluxo de Coleta:
    1. Apresentar sugestão formatada ao usuário
    2. Perguntar: Relevante? (S/N/Editar/Comentar)
    3. Se Editar: permite edição inline
    4. Se Comentar: captura comentário qualitativo
    5. Armazenar feedback estruturado

    Example:
        >>> collector = FeedbackCollector()
        >>> session = collector.collect_feedback_interactive(suggestions, "protocol.json", "model")
        >>> print(f"Feedback coletado: {len(session.suggestions_feedback)} sugestões")
    """

    def __init__(self, auto_save: bool = True, display_manager=None):
        """
        Inicializa o coletor de feedback.

        Args:
            auto_save: Se True, salva automaticamente após coleta
            display_manager: DisplayManager para UI integrada (opcional)
        """
        self.memory_qa = MemoryQA()
        self.storage = FeedbackStorage()  # Mantido para backup opcional
        self.memory_engine = MemoryEngine()  # Memory Engine V2 para regras estruturadas
        self.auto_save = auto_save
        self.display = display_manager
        logger.info("FeedbackCollector initialized")

    def collect_feedback_interactive(
        self,
        suggestions: List[Dict],
        protocol_name: str,
        model_used: str,
        skip_if_empty: bool = False
    ) -> FeedbackSession:
        """
        Apresenta sugestões interativamente e coleta feedback.

        Para cada sugestão:
        1. Exibe sugestão formatada
        2. Pergunta: Relevante? (S/N/Editar/Comentar)
        3. Captura resposta e processa
        4. Armazenar feedback estruturado

        Args:
            suggestions: Lista de sugestões para revisão
            protocol_name: Nome do protocolo
            model_used: Modelo LLM utilizado
            skip_if_empty: Se True, retorna sessão vazia se não houver sugestões

        Returns:
            FeedbackSession com todos os feedbacks coletados
        """
        if not suggestions and skip_if_empty:
            logger.info("No suggestions to collect feedback for, skipping")
            return None
        
        if not suggestions:
            logger.warning("No suggestions provided for feedback collection")
            return None
        
        # Header moderno e limpo (usando display_manager se disponível)
        if self.display:
            self.display.show_info(f"💬 Feedback - {len(suggestions)} sugestões")
            self.display.show_info(f"Protocolo: {protocol_name} | Modelo: {model_used}")
        else:
            print(f"\n💬 Feedback - {len(suggestions)} sugestões")
            print(f"Protocolo: {protocol_name} | Modelo: {model_used}")
            print("=" * 60)
        
        # Gerar session ID
        from .feedback_storage import FeedbackStorage
        temp_storage = FeedbackStorage()
        session_id = temp_storage._generate_session_id()
        suggestions_feedback = []
        
        # Carregar memória estruturada
        self.memory_engine.load_memory()
        
        # Coletar feedback para cada sugestão
        for idx, suggestion in enumerate(suggestions, 1):
            try:
                feedback = self.capture_user_verdict(suggestion, idx, len(suggestions))
                if feedback is None:  # Usuário saiu
                    print("\n⚠️  Feedback interrompido pelo usuário")
                    print("Salvando feedback parcial coletado até agora...")
                    logger.info(f"Feedback collection interrupted by user at suggestion {idx}/{len(suggestions)}")
                    
                    # Salvar feedback parcial se houver algum
                    if suggestions_feedback:
                        session = FeedbackSession(
                            session_id=session_id,
                            timestamp=datetime.now(),
                            protocol_name=protocol_name,
                            model_used=model_used,
                            suggestions_feedback=suggestions_feedback,
                            general_feedback=None,
                            quality_rating=None
                        )
                        if self.auto_save:
                            session_dict = asdict(session)
                            if isinstance(session_dict.get('timestamp'), datetime):
                                session_dict['timestamp'] = session_dict['timestamp'].isoformat()
                            self.memory_qa.add_feedback_session(session_dict)
                            self.storage.save_feedback_session(session_dict)  # Backup
                            print(f"✅ Feedback parcial salvo: {len(suggestions_feedback)} sugestões revisadas")
                        logger.info(f"Partial feedback saved: {session_id}, {len(suggestions_feedback)} suggestions")
                        return session
                    else:
                        print("Nenhum feedback coletado até agora.")
                        return None
                
                # Registrar feedback no Memory Engine V2
                if feedback:
                    decision = "S" if feedback.user_verdict == "relevant" else "N"
                    self.memory_engine.register_feedback(
                        suggestion=suggestion,
                        decision=decision,
                        comment=feedback.user_comment or "",
                        protocol_id=protocol_name,
                        model_id=model_used
                    )
                    # Salvar memória após cada feedback (incremental)
                    try:
                        self.memory_engine.save_memory()
                    except Exception as e:
                        logger.warning(f"Failed to save memory after feedback: {e}")
                
                suggestions_feedback.append(feedback)
            except KeyboardInterrupt:
                print("\n\n⚠️  Feedback interrompido (Ctrl+C)")
                print("Salvando feedback parcial coletado até agora...")
                logger.info(f"Feedback collection interrupted by keyboard interrupt")
                
                # Salvar feedback parcial se houver algum
                if suggestions_feedback:
                    session = FeedbackSession(
                        session_id=session_id,
                        timestamp=datetime.now(),
                        protocol_name=protocol_name,
                        model_used=model_used,
                        suggestions_feedback=suggestions_feedback,
                        general_feedback=None,
                        quality_rating=None
                    )
                    if self.auto_save:
                        session_dict = asdict(session)
                        if isinstance(session_dict.get('timestamp'), datetime):
                            session_dict['timestamp'] = session_dict['timestamp'].isoformat()
                        self.memory_qa.add_feedback_session(session_dict)
                        self.storage.save_feedback_session(session_dict)  # Backup
                        print(f"✅ Feedback parcial salvo: {len(suggestions_feedback)} sugestões revisadas")
                    logger.info(f"Partial feedback saved: {session_id}, {len(suggestions_feedback)} suggestions")
                    return session
                return None
        
        # Criar sessão (sem feedback geral - removido para simplificar)
        session = FeedbackSession(
            session_id=session_id,
            timestamp=datetime.now(),
            protocol_name=protocol_name,
            model_used=model_used,
            suggestions_feedback=suggestions_feedback,
            general_feedback=None,
            quality_rating=None
        )
        
        # Salvar se auto_save
        if self.auto_save:
            # Salvar no memory_qa.md (principal) - histórico textual
            session_dict = asdict(session)
            # Converter datetime para string se necessário
            if isinstance(session_dict.get('timestamp'), datetime):
                session_dict['timestamp'] = session_dict['timestamp'].isoformat()
            self.memory_qa.add_feedback_session(session_dict)
            
            # Salvar no FeedbackStorage (backup opcional)
            self.storage.save_feedback_session(session_dict)
            
            # Memory Engine já foi salvo incrementalmente durante coleta
            print(f"\n✅ Feedback salvo: {session_id}")
            print(f"✅ Memória estruturada atualizada: {len(self.memory_engine.rules_accepted)} aceitas, {len(self.memory_engine.rules_rejected)} rejeitadas")
        
        logger.info(f"Feedback collection completed: {session_id}, {len(suggestions_feedback)} suggestions")
        return session

    def present_suggestion(
        self,
        suggestion: Dict,
        index: int,
        total: int
    ) -> None:
        """
        Apresenta uma sugestão formatada ao usuário com contexto ampliado.

        Args:
            suggestion: Sugestão a ser apresentada
            index: Índice da sugestão atual
            total: Total de sugestões
        """
        # Layout moderno e limpo
        priority = suggestion.get("priority", "baixa").upper()
        priority_emoji = {
            "ALTA": "🔴",
            "HIGH": "🔴",
            "MEDIA": "🟡",
            "MEDIUM": "🟡",
            "BAIXA": "🟢",
            "LOW": "🟢"
        }
        emoji = priority_emoji.get(priority, "⚪")
        
        title = suggestion.get("title", "")
        description = suggestion.get("description", "")
        
        # Usar display_manager se disponível, senão usar print
        if self.display:
            # UI integrada com display_manager
            header = f"[{index}/{total}] {emoji} {priority} | {suggestion.get('category', 'N/A')} | {suggestion.get('id', 'N/A')}"
            self.display.show_info(header)
            
            if title:
                self.display.console.print(f"\n[bold]{title}[/bold]")
            
            if description:
                # Mostrar descrição completa, quebrando em linhas de forma inteligente
                desc_clean = " ".join(description.split())
                words = desc_clean.split()
                lines = []
                current_line = ""
                for word in words:
                    test_line = (current_line + " " + word) if current_line else word
                    if len(test_line) <= 75:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                
                # Mostrar até 3 linhas completas
                for line in lines[:3]:
                    self.display.console.print(f"   {line}")
                if len(lines) > 3:
                    self.display.console.print("   ...")
            self.display.console.print()
        else:
            # Fallback para print simples
            print(f"\n[{index}/{total}] {emoji} {priority} | {suggestion.get('category', 'N/A')} | {suggestion.get('id', 'N/A')}")
            print("-" * 60)
            
            if title:
                print(f"\n{title}")
            
            if description:
                desc_clean = " ".join(description.split())
                words = desc_clean.split()
                lines = []
                current_line = ""
                for word in words:
                    test_line = (current_line + " " + word) if current_line else word
                    if len(test_line) <= 75:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                
                for line in lines[:3]:
                    print(f"   {line}")
                if len(lines) > 3:
                    print("   ...")
            print()

    def capture_user_verdict(
        self,
        suggestion: Dict,
        index: int,
        total: int
    ) -> SuggestionFeedback:
        """
        Captura veredito do usuário sobre uma sugestão.

        Opções:
        - S (Sim, relevante)
        - N (Não, irrelevante)
        - E (Editar sugestão)
        - C (Adicionar comentário)

        Args:
            suggestion: Sugestão sendo avaliada
            index: Índice da sugestão
            total: Total de sugestões

        Returns:
            SuggestionFeedback com veredito e dados adicionais
        """
        # Apresentar sugestão
        self.present_suggestion(suggestion, index, total)
        
        suggestion_id = suggestion.get("id", f"sug-{index}")
        
        while True:
            try:
                # CRITICAL FIX: Simplified UX from 7 options to 3 (user request)
                print(f"\nEsta sugestão é relevante?")
                print("  S - Relevante")
                print("  N - Irrelevante (com opção de comentar)")
                print("  Q - Sair do feedback")

                response = input("\nEscolha (S/N/Q): ").strip().upper()

                if response in ("Q", "SAIR", "QUIT", "EXIT"):
                    # Usuário quer sair
                    return None

                elif response in ("S", "SIM", "Y", "YES"):
                    # Relevante
                    return SuggestionFeedback(
                        suggestion_id=suggestion_id,
                        user_verdict="relevant",
                        user_comment=None,
                        edited=False
                    )

                elif response in ("N", "NAO", "NO"):
                    # Irrelevante - sempre oferecer opção de comentar
                    print("\nPor favor, explique por que esta sugestão é irrelevante.")
                    print("Isso ajudará o sistema a aprender e evitar sugestões similares.")
                    comment = input("Motivo da rejeição (opcional, Enter para pular): ").strip()
                    if not comment:
                        comment = None

                    return SuggestionFeedback(
                        suggestion_id=suggestion_id,
                        user_verdict="irrelevant",
                        user_comment=comment,
                        edited=False
                    )
                
                else:
                    print("❌ Opção inválida. Por favor, escolha S (Relevante), N (Irrelevante) ou Q (Sair).")
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Coleta de feedback cancelada pelo usuário.")
                # Marcar como relevante por padrão se cancelado
                return SuggestionFeedback(
                    suggestion_id=suggestion_id,
                    user_verdict="relevant",
                    user_comment="Feedback cancelado pelo usuário",
                    edited=False
                )

    def allow_edit_suggestion(
        self,
        suggestion: Dict
    ) -> Dict:
        """
        Permite edição inline de uma sugestão.

        Args:
            suggestion: Sugestão original

        Returns:
            Sugestão editada pelo usuário
        """
        print("\n✏️  Edição de Sugestão")
        print("-" * 60)
        print("1. Título | 2. Descrição | 3. Cancelar")
        
        edited = suggestion.copy()
        
        while True:
            try:
                choice = input("\nQual campo deseja editar? (1/2/3): ").strip()
                
                if choice == "1":
                    current_title = suggestion.get("title", "")
                    print(f"\nTítulo atual: {current_title}")
                    new_title = input("Novo título (Enter para manter): ").strip()
                    if new_title:
                        edited["title"] = new_title
                        print("✅ Título atualizado")
                
                elif choice == "2":
                    current_desc = suggestion.get("description", "")
                    print(f"\nDescrição atual: {current_desc}")
                    print("Nova descrição (Enter para manter, 'END' para finalizar):")
                    new_desc_lines = []
                    while True:
                        line = input()
                        if line.strip().upper() == "END":
                            break
                        new_desc_lines.append(line)
                    if new_desc_lines:
                        edited["description"] = "\n".join(new_desc_lines)
                        print("✅ Descrição atualizada")
                
                elif choice == "3":
                    print("❌ Edição cancelada")
                    return suggestion
                
                else:
                    print("❌ Opção inválida")
                    continue
                
                # Continuar editando?
                if input("\nEditar outro campo? (S/N): ").strip().upper() not in ("S", "SIM", "Y", "YES"):
                    break
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Edição cancelada")
                return suggestion
        
        return edited

    def capture_comment(
        self,
        suggestion: Dict
    ) -> str:
        """
        Captura comentário qualitativo do usuário.

        Args:
            suggestion: Sugestão sendo comentada

        Returns:
            Comentário do usuário
        """
        print("\n" + "-" * 60)
        print("COMENTÁRIO")
        print("-" * 60)
        print("Digite seu comentário (Enter para finalizar, 'END' em linha vazia para concluir):")
        
        comment_lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == "END" and not comment_lines:
                    return ""
                if line.strip().upper() == "END":
                    break
                comment_lines.append(line)
            except KeyboardInterrupt:
                print("\n⚠️  Comentário cancelado")
                return ""
        
        comment = "\n".join(comment_lines).strip()
        return comment if comment else None

