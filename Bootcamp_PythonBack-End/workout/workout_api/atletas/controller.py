
from uuid import uuid4
from fastapi import APIRouter, status, Body, HTTPException
from pydantic import UUID4
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from workout.workout_api.atletas.schemas import AtletaIN, AtletaOut, AtletaUpdate
from workout.workout_api.atletas.models import AtletaModel
from workout.workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout.workout_api.contrib.dependencies import DataBaseDependecy
from datetime import datetime
from workout.workout_api.categorias.models import CategoriaModel
from fastapi import Query, Depends


router = APIRouter()


def get_pagination_params(
    page: int = Query(1, gt=0),
    per_page: int = Query(10, gt=0)
):
    return {"page": page, "per_page": per_page}


@router.post(
        '/',
        summary='Adicionar um novo atleta',
        status_code=status.HTTP_201_CREATED,
        response_model=AtletaOut,
        )
async def post(
    db_session: DataBaseDependecy,
    atleta_in: AtletaIN = Body(...)
        ):

    categoria = (await db_session.execute(select(
        CategoriaModel).filter_by(nome=atleta_in.categoria.nome))).scalars().first()

    if not categoria:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'A categoria {atleta_in.categoria.nome} não foi encontrada.')

    centro_treinamento = (await db_session.execute(select(
        CentroTreinamentoModel).filter_by(nome=atleta_in.centro_treinamento.nome))).scalars().first()

    if not centro_treinamento:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'O centro de treinamento {atleta_in.centro_treinamento.nome} não foi encontrado.')

    try:
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        db_session.add(atleta_model)
        await db_session.commit()

    except IntegrityError:
        raise HTTPException(
                            status_code=status.HTTP_303_SEE_OTHER,
                            detail="Já existe um atleta cadastrado com o CPF informado"
                            )
    except Exception:
        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Ocorreu um erro ao inserir os dados no banco.'
                            )

    return atleta_out


@router.get(
    '/',
    summary='Consultar todos os atletas',
    status_code=status.HTTP_200_OK,
    response_model=list[dict[str, str]],
)
async def get(db_session: DataBaseDependecy, pagination: dict = Depends(get_pagination_params),
              offset: int = Query(0, ge=0), limit: int = Query(10, gt=0)) -> list[dict[str, str]]:
    atletas: list[AtletaOut] = (await db_session.execute(select(AtletaModel))).scalars().all()
    page = pagination["page"]
    per_page = pagination["per_page"]
    start = (page - 1) * per_page
    end = start + per_page
    # Criar uma lista de dicionários com os campos desejados
    resultado = [
        {
            "nome": atleta.nome,
            "categoria": atleta.categoria.nome,  # Acessar o nome da categoria
            "centro_treinamento": atleta.centro_treinamento.nome,  # Acessar o nome do centro de treinamento
        }
        for atleta in atletas
    ]

    return resultado[start:end][offset:offset + limit]


@router.get(
        '/buscar',
        summary='Consultar um atleta por nome e cpf',
        status_code=status.HTTP_200_OK,
        response_model=AtletaOut,
        )
async def get_one(nome, cpf, db_session: DataBaseDependecy) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(nome=nome, cpf=cpf))
        ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta com nome {nome} e cpf: {cpf} não encontrado.'
            )

    return atleta


@router.patch(
        '/{id}',
        summary='Editar um atleta pelo id',
        status_code=status.HTTP_200_OK,
        response_model=AtletaOut,
        )
async def patch(id: UUID4, db_session: DataBaseDependecy, atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
        ).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrado no id {id}')

    atleta_update = atleta_up.model_dump(exclude_unset=True)

    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.delete(
        '/{id}',
        summary='Deletar um atleta pelo id',
        status_code=status.HTTP_204_NO_CONTENT,

        )
async def delete(id: UUID4, db_session: DataBaseDependecy) -> None:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
        ).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrado no id {id}')

    await db_session.delete(atleta)
    await db_session.commit()
