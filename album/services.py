from django.db.models import Count, Q, Sum

from .models import ColecaoFigurinha, Figurinha


def resumo_usuario(user):
    total = Figurinha.objects.count()
    agregados = ColecaoFigurinha.objects.filter(user=user).aggregate(
        tenho=Count('id', filter=Q(quantidade__gte=1)),
        repetidas=Sum('quantidade', filter=Q(quantidade__gt=1)),
    )
    tenho = agregados['tenho'] or 0
    total_repetidas = agregados['repetidas'] or 0
    faltam = max(total - tenho, 0)
    percentual = round((tenho / total) * 100) if total else 0

    return {
        'total': total,
        'tenho': tenho,
        'faltam': faltam,
        'repetidas': total_repetidas,
        'percentual': percentual,
    }


def mapa_colecao(user, figurinhas):
    ids = [figurinha.id for figurinha in figurinhas]
    colecoes = ColecaoFigurinha.objects.filter(user=user, figurinha_id__in=ids)
    return {colecao.figurinha_id: colecao for colecao in colecoes}


def quantidade_usuario(user, figurinha):
    colecao = ColecaoFigurinha.objects.filter(user=user, figurinha=figurinha).first()
    return colecao.quantidade if colecao else 0


def ajustar_quantidade(user, figurinha, delta=None, quantidade=None, observacao=None):
    colecao, _ = ColecaoFigurinha.objects.get_or_create(user=user, figurinha=figurinha)
    if quantidade is not None:
        colecao.quantidade = max(int(quantidade), 0)
    elif delta is not None:
        colecao.quantidade = max(colecao.quantidade + int(delta), 0)

    if observacao is not None:
        colecao.observacao = observacao

    colecao.save()
    return colecao


def dados_figurinha(user, figurinha, colecao=None):
    quantidade = colecao.quantidade if colecao else 0
    if quantidade > 1:
        status = 'repetida'
    elif quantidade == 1:
        status = 'tenho'
    else:
        status = 'falta'

    return {
        'figurinha': figurinha,
        'colecao': colecao,
        'quantidade': quantidade,
        'status': status,
        'disponivel_troca': max(quantidade - 1, 0),
    }
