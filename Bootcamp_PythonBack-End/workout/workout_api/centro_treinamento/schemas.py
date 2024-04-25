from workout.workout_api.contrib.schemas import BaseSchema
from pydantic import UUID4, Field
from typing import Annotated


class CentroTreinamentoIn(BaseSchema):
    nome: Annotated[str, Field(description='Nome do centro de treinamento', examples=['CT master'], max_length=20)]
    endereco: Annotated[str, Field(description='Endereco do centro de treinamento',
                                   examples=['Rua x, 222'], max_length=60)]
    proprietario: Annotated[str, Field(description='Proprietario do centro de treinamento', examples=['Joao'],
                                       max_length=30)]


class CentroTreinamentoAtleta(BaseSchema):
    nome: Annotated[str, Field(description='Nome do centro de treinamento', examples=['CT Main'], max_length=30)]


class CentroTreinamentoOut(CentroTreinamentoIn):
    id: Annotated[UUID4, Field(description='Identificador da categoria')]
