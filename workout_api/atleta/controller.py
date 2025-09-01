from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status, Query
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
# from fastapi_pagination import Page, paginate, add_pagination
# from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate, AtletaListOut
from workout_api.atleta.models import AtletaModel
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel

from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select
from sqlalchemy import or_

router = APIRouter()

@router.post(
    '/', 
    summary='Criar um novo atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
)
async def post(
    db_session: DatabaseDependency, 
    atleta_in: AtletaIn = Body(...)
):
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome

    # Verificar se a categoria existe
    categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_nome))
    ).scalars().first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f'A categoria {categoria_nome} não foi encontrada.'
        )
    
    # Verificar se o centro de treinamento existe
    centro_treinamento = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))
    ).scalars().first()
    
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f'O centro de treinamento {centro_treinamento_nome} não foi encontrado.'
        )
    
    # VERIFICAÇÃO PRÉVIA: Verificar se CPF já existe
    cpf_existente = (await db_session.execute(
        select(AtletaModel).filter_by(cpf=atleta_in.cpf))
    ).scalars().first()
    
    if cpf_existente:
        raise HTTPException(
            status_code=303,
            detail=f"Já existe um atleta cadastrado com o CPF: {atleta_in.cpf}"
        )
    
    # VERIFICAÇÃO PRÉVIA: Verificar se nome já existe
    nome_existente = (await db_session.execute(
        select(AtletaModel).filter_by(nome=atleta_in.nome))
    ).scalars().first()
    
    if nome_existente:
        raise HTTPException(
            status_code=303,
            detail=f"Já existe um atleta cadastrado com o nome: {atleta_in.nome}"
        )
    
    try:
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.now(timezone.utc), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))

        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id
        
        db_session.add(atleta_model)
        await db_session.commit()
        
    except IntegrityError as e:
        # Capturar erro de integridade específico (fallback)
        error_message = str(e).lower()
        
        if "cpf" in error_message:
            raise HTTPException(
                status_code=303,
                detail=f"Já existe um atleta cadastrado com o CPF: {atleta_in.cpf}"
            )
        elif "nome" in error_message:
            raise HTTPException(
                status_code=303,
                detail=f"Já existe um atleta cadastrado com o nome: {atleta_in.nome}"
            )
        elif "unique" in error_message:
            raise HTTPException(
                status_code=303,
                detail="Já existe um atleta com dados duplicados. Verifique se o CPF ou nome já não foram cadastrados."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro de validação: {str(e)}"
            )
            
    except Exception as e:
        # Capturar outros erros genéricos
        print(f"Erro inesperado ao criar atleta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='Erro interno do servidor. Entre em contato com o suporte técnico.'
        )

    return atleta_out


@router.get(
    '/', 
    summary='Consultar todos os Atletas',
    status_code=status.HTTP_200_OK,
    response_model=list[AtletaListOut],  # TEMPORARIAMENTE SEM PAGINAÇÃO
)
async def query(
    db_session: DatabaseDependency,
    nome: str = Query(None, description='Filtrar por nome do atleta'),
    cpf: str = Query(None, description='Filtrar por CPF do atleta')
) -> list[AtletaListOut]:
    query = select(AtletaModel)
    
    # Aplicar filtros se fornecidos
    if nome:
        query = query.filter(AtletaModel.nome.ilike(f'%{nome}%'))
    if cpf:
        query = query.filter(AtletaModel.cpf.ilike(f'%{cpf}%'))
    
    # Executar query SEM paginação (TEMPORARIAMENTE)
    result = await db_session.execute(query)
    atletas = result.scalars().all()
    
    # Converter para o formato de resposta customizado
    atletas_list = []
    for atleta in atletas:
        atleta_list_out = AtletaListOut(
            nome=atleta.nome,
            centro_treinamento=atleta.centro_treinamento.nome if atleta.centro_treinamento else "",
            categoria=atleta.categoria.nome if atleta.categoria else ""
        )
        atletas_list.append(atleta_list_out)
    
    return atletas_list


@router.get(
    '/{id}', 
    summary='Consulta um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    return atleta


@router.patch(
    '/{id}', 
    summary='Editar um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def patch(id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    try:
        atleta_update = atleta_up.model_dump(exclude_unset=True)
        for key, value in atleta_update.items():
            setattr(atleta, key, value)

        await db_session.commit()
        await db_session.refresh(atleta)
        
    except IntegrityError as e:
        # Capturar erro de integridade específico
        error_message = str(e).lower()
        
        if "cpf" in error_message:
            raise HTTPException(
                status_code=303,
                detail=f"Já existe um atleta cadastrado com o CPF: {atleta.cpf}"
            )
        elif "unique" in error_message:
            raise HTTPException(
                status_code=303,
                detail="Já existe um atleta com dados duplicados. Verifique se o CPF já não foi cadastrado."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro de validação: {str(e)}"
            )
            
    except Exception as e:
        # Capturar outros erros genéricos
        print(f"Erro inesperado ao atualizar atleta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='Ocorreu um erro interno ao processar a solicitação. Tente novamente mais tarde.'
        )

    return atleta


@router.delete(
    '/{id}', 
    summary='Deletar um Atleta pelo id',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    try:
        await db_session.delete(atleta)
        await db_session.commit()
        
    except Exception as e:
        print(f"Erro inesperado ao deletar atleta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='Ocorreu um erro interno ao processar a solicitação. Tente novamente mais tarde.'
        )
