from collections import Counter, defaultdict

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ObservacaoFigurinhaForm, RegistroForm, TrocaForm
from .models import ColecaoFigurinha, Figurinha, ItemTroca, SecaoEspecial, Selecao, Troca
from .services import ajustar_quantidade, dados_figurinha, mapa_colecao, resumo_usuario


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistroForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'album/dashboard.html', {'resumo': resumo_usuario(request.user)})


@login_required
def selecoes_list(request):
    selecoes = Selecao.objects.annotate(
        total=Count('figurinhas', distinct=True),
        tenho=Count(
            'figurinhas__colecoes',
            filter=Q(
                figurinhas__colecoes__user=request.user,
                figurinhas__colecoes__quantidade__gte=1,
            ),
            distinct=True,
        ),
    ).order_by('grupo', 'ordem', 'nome')
    cards = []
    for selecao in selecoes:
        percentual = round((selecao.tenho / selecao.total) * 100) if selecao.total else 0
        cards.append({'selecao': selecao, 'total': selecao.total, 'tenho': selecao.tenho, 'percentual': percentual})

    return render(request, 'album/selecoes_list.html', {'cards': cards})


@login_required
def selecao_detail(request, pk):
    selecao = get_object_or_404(Selecao, pk=pk)
    status = request.GET.get('status', 'todas')
    categoria_id = request.GET.get('categoria')
    figurinhas = Figurinha.objects.filter(selecao=selecao).select_related('categoria', 'selecao')

    if categoria_id:
        figurinhas = figurinhas.filter(categoria_id=categoria_id)

    colecoes = mapa_colecao(request.user, figurinhas)
    cards = [dados_figurinha(request.user, figurinha, colecoes.get(figurinha.id)) for figurinha in figurinhas]

    if status == 'tenho':
        cards = [card for card in cards if card['quantidade'] >= 1]
    elif status == 'faltam':
        cards = [card for card in cards if card['quantidade'] == 0]
    elif status == 'repetidas':
        cards = [card for card in cards if card['quantidade'] > 1]

    total = Figurinha.objects.filter(selecao=selecao).count()
    tenho = ColecaoFigurinha.objects.filter(user=request.user, figurinha__selecao=selecao, quantidade__gte=1).count()
    percentual = round((tenho / total) * 100) if total else 0
    categorias = selecao.figurinhas.order_by('categoria__nome').values('categoria_id', 'categoria__nome').distinct()
    selecoes_ordenadas = list(Selecao.objects.order_by('grupo', 'ordem', 'nome'))
    indice_atual = next((indice for indice, item in enumerate(selecoes_ordenadas) if item.pk == selecao.pk), 0)
    selecao_anterior = selecoes_ordenadas[indice_atual - 1] if indice_atual > 0 else None
    proxima_selecao = selecoes_ordenadas[indice_atual + 1] if indice_atual < len(selecoes_ordenadas) - 1 else None

    return render(request, 'album/selecao_detail.html', {
        'selecao': selecao,
        'selecao_anterior': selecao_anterior,
        'proxima_selecao': proxima_selecao,
        'cards': cards,
        'status_atual': status,
        'categoria_atual': categoria_id or '',
        'categorias': categorias,
        'total': total,
        'tenho': tenho,
        'percentual': percentual,
    })


@login_required
def secao_especial_detail(request, codigo):
    secao = get_object_or_404(SecaoEspecial, codigo_album=codigo.upper())
    status = request.GET.get('status', 'todas')
    figurinhas = Figurinha.objects.filter(secao_especial=secao).select_related('categoria', 'secao_especial')
    colecoes = mapa_colecao(request.user, figurinhas)
    cards = [dados_figurinha(request.user, figurinha, colecoes.get(figurinha.id)) for figurinha in figurinhas]

    if status == 'tenho':
        cards = [card for card in cards if card['quantidade'] >= 1]
    elif status == 'faltam':
        cards = [card for card in cards if card['quantidade'] == 0]
    elif status == 'repetidas':
        cards = [card for card in cards if card['quantidade'] > 1]

    total = Figurinha.objects.filter(secao_especial=secao).count()
    tenho = ColecaoFigurinha.objects.filter(user=request.user, figurinha__secao_especial=secao, quantidade__gte=1).count()
    percentual = round((tenho / total) * 100) if total else 0

    return render(request, 'album/secao_especial_detail.html', {
        'secao': secao,
        'cards': cards,
        'status_atual': status,
        'total': total,
        'tenho': tenho,
        'percentual': percentual,
    })


@login_required
def figurinhas_faltantes(request):
    colecionadas = ColecaoFigurinha.objects.filter(user=request.user, quantidade__gte=1).values('figurinha_id')
    figurinhas = Figurinha.objects.filter(selecao__isnull=False).exclude(id__in=colecionadas).select_related('selecao', 'categoria')
    grupos = defaultdict(list)
    for figurinha in figurinhas:
        grupos[figurinha.selecao].append(figurinha)

    return render(request, 'album/figurinhas_faltantes.html', {'grupos': dict(grupos)})


@login_required
def figurinhas_repetidas(request):
    colecoes = ColecaoFigurinha.objects.filter(user=request.user, quantidade__gt=1).select_related(
        'figurinha__selecao',
        'figurinha__secao_especial',
        'figurinha__categoria',
    )
    cards = [dados_figurinha(request.user, colecao.figurinha, colecao) for colecao in colecoes]
    return render(request, 'album/figurinhas_repetidas.html', {'cards': cards})


@login_required
def figurinha_detail(request, pk):
    figurinha = get_object_or_404(Figurinha.objects.select_related('selecao', 'secao_especial', 'categoria'), pk=pk)
    colecao, _ = ColecaoFigurinha.objects.get_or_create(user=request.user, figurinha=figurinha)

    if request.method == 'POST':
        form = ObservacaoFigurinhaForm(request.POST)
        if form.is_valid():
            ajustar_quantidade(
                request.user,
                figurinha,
                quantidade=form.cleaned_data['quantidade'],
                observacao=form.cleaned_data['observacao'],
            )
            messages.success(request, 'Figurinha atualizada.')
            return redirect('figurinha_detail', pk=figurinha.pk)
    else:
        form = ObservacaoFigurinhaForm(initial={
            'quantidade': colecao.quantidade,
            'observacao': colecao.observacao,
        })

    return render(request, 'album/figurinha_detail.html', {
        'figurinha': figurinha,
        'colecao': colecao,
        'card': dados_figurinha(request.user, figurinha, colecao),
        'form': form,
    })


@login_required
@require_POST
def alterar_quantidade(request, pk):
    figurinha = get_object_or_404(Figurinha, pk=pk)
    delta = request.POST.get('delta', '0')
    colecao = ajustar_quantidade(request.user, figurinha, delta=delta)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'quantidade': colecao.quantidade,
            'tem': colecao.quantidade > 0,
            'repetida': colecao.quantidade > 1,
        })
    proximo = request.POST.get('next') or reverse('figurinha_detail', args=[figurinha.pk])
    return redirect(proximo)


@login_required
def trocas_list(request):
    selecao_id = request.GET.get('selecao')
    selecoes = Selecao.objects.order_by('grupo', 'ordem', 'nome')
    selecao_atual = None
    faltantes = []
    sugestoes = []

    if selecao_id:
        selecao_atual = get_object_or_404(Selecao, pk=selecao_id)
        minhas_figurinhas = ColecaoFigurinha.objects.filter(
            user=request.user,
            quantidade__gte=1,
            figurinha__selecao=selecao_atual,
        ).values('figurinha_id')
        faltantes = list(
            Figurinha.objects.filter(selecao=selecao_atual)
            .exclude(id__in=minhas_figurinhas)
            .select_related('categoria')
            .order_by('ordem')
        )
        repetidas = (
            ColecaoFigurinha.objects.filter(
                figurinha__in=faltantes,
                quantidade__gt=1,
            )
            .exclude(user=request.user)
            .select_related('user', 'figurinha')
            .order_by('user__username', 'figurinha__ordem')
        )

        por_usuario = {}
        for colecao in repetidas:
            item = por_usuario.setdefault(colecao.user_id, {
                'user': colecao.user,
                'figurinhas': [],
            })
            item['figurinhas'].append({
                'figurinha': colecao.figurinha,
                'disponivel': colecao.disponivel_troca,
            })
        sugestoes = list(por_usuario.values())

    trocas = Troca.objects.filter(user=request.user).prefetch_related('itens__figurinha')
    return render(request, 'album/trocas_list.html', {
        'trocas': trocas,
        'selecoes': selecoes,
        'selecao_atual': selecao_atual,
        'faltantes': faltantes,
        'sugestoes': sugestoes,
    })


@login_required
@transaction.atomic
def troca_nova(request):
    if request.method == 'POST':
        form = TrocaForm(request.POST)
        if form.is_valid():
            numeros = set(form.cleaned_data['figurinhas_dei'] + form.cleaned_data['figurinhas_recebi'])
            encontradas = {f.numero: f for f in Figurinha.objects.filter(numero__in=numeros)}
            faltando = sorted(numeros - set(encontradas))
            if faltando:
                form.add_error(None, f'Figurinhas nao encontradas: {", ".join(map(str, faltando))}.')
            else:
                troca = form.save(commit=False)
                troca.user = request.user
                troca.save()
                _criar_itens_troca(request.user, troca, encontradas, form.cleaned_data['figurinhas_dei'], ItemTroca.TIPO_DEI)
                _criar_itens_troca(request.user, troca, encontradas, form.cleaned_data['figurinhas_recebi'], ItemTroca.TIPO_RECEBI)
                messages.success(request, 'Troca registrada.')
                return redirect('trocas_list')
    else:
        form = TrocaForm()

    return render(request, 'album/troca_form.html', {'form': form})


def _criar_itens_troca(user, troca, encontradas, numeros, tipo):
    delta = -1 if tipo == ItemTroca.TIPO_DEI else 1
    for numero, quantidade in Counter(numeros).items():
        figurinha = encontradas[numero]
        ItemTroca.objects.create(troca=troca, figurinha=figurinha, tipo=tipo, quantidade=quantidade)
        ajustar_quantidade(user, figurinha, delta=delta * quantidade)
