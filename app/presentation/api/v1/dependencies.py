from functools import lru_cache
from app.domain.services.musical_error_service import MusicalErrorService
from app.infrastructure.repositories.mysql_repo import MySQLMusicalErrorRepository
from app.application.use_cases.list_errors_by_practice import ListErrorsByPracticeUseCase

# Repositorios
@lru_cache()
def get_musical_error_repository() -> MySQLMusicalErrorRepository:
    """Obtener instancia del repositorio de errores musicales"""
    return MySQLMusicalErrorRepository()

# Servicios
@lru_cache()
def get_musical_error_service() -> MusicalErrorService:
    """Obtener instancia del servicio de dominio de errores musicales"""
    repo = get_musical_error_repository()
    return MusicalErrorService(repo)

# Casos de uso
@lru_cache()
def get_list_errors_by_practice_use_case() -> ListErrorsByPracticeUseCase:
    """Obtener instancia del caso de uso para listar errores musicales de una práctica"""
    service = get_musical_error_service()
    return ListErrorsByPracticeUseCase(service)

# Dependencia para FastAPI
def list_errors_by_practice_use_case_dependency():
    """Dependencia para inyectar caso de uso de listar errores musicales"""
    return get_list_errors_by_practice_use_case()
