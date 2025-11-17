from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class StandardResponse(BaseModel, Generic[DataT]):
    status: ResponseStatus = Field(
        ResponseStatus.SUCCESS, description="Status da resposta ('success' ou 'error')."
    )
    message: str | None = Field(
        None, description="Mensagem legível opcional sobre a operação."
    )
    data: DataT | None = Field(None, description="O payload de dados da resposta.")


class ErrorResponse(BaseModel):
    """
    Define a estrutura de resposta padrão para respostas de ERRO.
    """

    status: str = Field(
        ResponseStatus.ERROR, description="Status da resposta ('error')"
    )
    message: str = Field(..., description="Descrição detalhada e legível do erro.")
    code: int | None = Field(None, description="Código de erro ou status HTTP.")
