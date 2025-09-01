from pydantic import BaseModel, Field
from typing import Annotated, List
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


class AtletaIn(BaseSchema):
    nome: Annotated[str, Field(description='Nome do atleta', example='Joao')]
    cpf: Annotated[str, Field(description='CPF do atleta', example='12345678901')]
    idade: Annotated[int, Field(description='Idade do atleta', example=25)]
    peso: Annotated[float, Field(description='Peso do atleta', example=75.5)]
    altura: Annotated[float, Field(description='Altura do atleta', example=1.7)]
    sexo: Annotated[str, Field(description='Sexo do atleta', example='M')]
    categoria: Annotated[CategoriaIn, Field(description='Categoria do atleta')]
    centro_treinamento: Annotated[CentroTreinamentoIn, Field(description='Centro de treinamento do atleta')]


class AtletaOut(BaseSchema):
    id: Annotated[str, Field(description='Identificador único do atleta')]
    nome: Annotated[str, Field(description='Nome do atleta', example='Joao')]
    cpf: Annotated[str, Field(description='CPF do atleta', example='12345678901')]
    idade: Annotated[int, Field(description='Idade do atleta', example=25)]
    peso: Annotated[float, Field(description='Peso do atleta', example=75.5)]
    altura: Annotated[float, Field(description='Altura do atleta', example=1.7)]
    sexo: Annotated[str, Field(description='Sexo do atleta', example='M')]
    created_at: Annotated[str, Field(description='Data de criação do atleta')]
    categoria: Annotated[CategoriaOut, Field(description='Categoria do atleta')]
    centro_treinamento: Annotated[CentroTreinamentoOut, Field(description='Centro de treinamento do atleta')]


class AtletaUpdate(BaseSchema):
    nome: Annotated[str | None, Field(description='Nome do atleta', example='Joao')] = None
    cpf: Annotated[str | None, Field(description='CPF do atleta', example='12345678901')] = None
    idade: Annotated[int | None, Field(description='Idade do atleta', example=25)] = None
    peso: Annotated[float | None, Field(description='Peso do atleta', example=75.5)] = None
    altura: Annotated[float | None, Field(description='Altura do atleta', example=1.7)] = None
    sexo: Annotated[str | None, Field(description='Sexo do atleta', example='M')] = None
    categoria: Annotated[CategoriaIn | None, Field(description='Categoria do atleta')] = None
    centro_treinamento: Annotated[CentroTreinamentoIn | None, Field(description='Centro de treinamento do atleta')] = None


class AtletaListOut(BaseSchema):
    nome: Annotated[str, Field(description='Nome do atleta', example='Joao')]
    centro_treinamento: Annotated[str, Field(description='Nome do centro de treinamento', example='Academia Fitness')]
    categoria: Annotated[str, Field(description='Nome da categoria', example='Peso Pesado')]


# Schema para resposta paginada
class PaginatedResponse(BaseSchema):
    items: List[AtletaListOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool