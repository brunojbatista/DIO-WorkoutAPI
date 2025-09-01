from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workout_api.centro_treinamento.models import CentroTreinamentoModel

from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

@router.post(
    '/', 
    summary='Criar um novo Centro de treinamento',
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
)
async def post(
    db_session: DatabaseDependency, 
    centro_treinamento_in: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    try:
        centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())
        centro_treinamento_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())
        
        db_session.add(centro_treinamento_model)
        await db_session.commit()
        
    except IntegrityError as e:
        # Capturar erro de integridade específico
        error_message = str(e).lower()
        
        if "nome" in error_message:
            raise HTTPException(
                status_code=303,
                detail=f"Já existe um centro de treinamento cadastrado com o nome: {centro_treinamento_in.nome}"
            )
        elif "unique" in error_message:
            raise HTTPException(
                status_code=303,
                detail="Já existe um centro de treinamento com dados duplicados. Verifique se o nome já não foi cadastrado."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro de validação: {str(e)}"
            )
            
    except Exception as e:
        # Capturar outros erros genéricos
        print(f"Erro inesperado ao criar centro de treinamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='Ocorreu um erro interno ao processar a solicitação. Tente novamente mais tarde.'
        )

    return centro_treinamento_out
    
    
@router.get(
    '/', 
    summary='Consultar todos os centros de treinamento',
    status_code=status.HTTP_200_OK,
    response_model=list[CentroTreinamentoOut],
)
async def query(db_session: DatabaseDependency) -> list[CentroTreinamentoOut]:
    centros_treinamento_out: list[CentroTreinamentoOut] = (
        await db_session.execute(select(CentroTreinamentoModel))
    ).scalars().all()
    
    return centros_treinamento_out


@router.get(
    '/{id}', 
    summary='Consulta um centro de treinamento pelo id',
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    centro_treinamento_out: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()

    if not centro_treinamento_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Centro de treinamento não encontrado no id: {id}'
        )
    
    return centro_treinamento_out