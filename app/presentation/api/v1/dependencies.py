from functools import lru_cache
from app.domain.services.musical_error_service import MusicalErrorService
from app.infrastructure.repositories.mysql_repo import MySQLMusicalErrorRepository
from app.application.use_cases.list_errors_by_practice import ListErrorsByPracticeUseCase

# Repositories
@lru_cache()
def get_musical_error_repository() -> MySQLMusicalErrorRepository:
    """Get instance of the musical error repository"""
    return MySQLMusicalErrorRepository()

# Services
@lru_cache()
def get_musical_error_service() -> MusicalErrorService:
    """Get instance of the musical error domain service"""
    repo = get_musical_error_repository()
    return MusicalErrorService(repo)

# Use Cases
@lru_cache()
def get_list_errors_by_practice_use_case() -> ListErrorsByPracticeUseCase:
    """Get instance of the use case to list musical errors by practice"""
    service = get_musical_error_service()
    return ListErrorsByPracticeUseCase(service)

# Dependency for FastAPI
def list_errors_by_practice_use_case_dependency():
    """Dependency to inject use case for listing musical errors"""
    return get_list_errors_by_practice_use_case()
