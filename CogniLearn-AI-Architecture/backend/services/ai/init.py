"""
AI Service Layer.

Implements Module 9: prompt construction, context assembly, provider
communication, response processing, and AI interaction logging.
`ai_service.AIService` is the single entry point the API layer uses;
every other module here (context_builder, prompt_builder,
prompt_templates, provider_manager, response_parser,
response_validator, retry_handler, token_manager) is an internal
collaborator with one responsibility, matching the documented folder
structure.

Reference: 06_IMPLEMENTATION_GUIDE/03_AI_SERVICE_IMPLEMENTATION.md (Section 5 - Folder Structure)
"""

from backend.services.ai.ai_service import AIService, AITutorResult

__all__ = ["AIService", "AITutorResult"]