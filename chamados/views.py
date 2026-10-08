from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.http import JsonResponse
from .models import Chamado, Setor, Local, HistoricoChamado
from django.core.paginator import Paginator


def inicio(request):

    setor_id = request.GET.get("setor")
    local_id = request.GET.get("local")
    status_filtro = request.GET.get("status", "abertos")
    solicitante_filtro = request.GET.get("solicitante", "").strip()


    # =========================================================
    # CHAMADOS ABERTOS
    # =========================================================

    if status_filtro == "abertos":

        # Pega os 5 chamados FINALIZADOS mais recentemente
        ultimos_finalizados = Chamado.objects.filter(
            status="FINALIZADO"
        ).order_by(
            "-data_finalizacao",
            "-data_abertura"
        ).values_list(
            "id",
            flat=True
        )[:5]


        # Mostra:
        # - todos os ABERTOS
        # - todos os EM ATENDIMENTO
        # - os 5 últimos FINALIZADOS
        chamados_abertos = Chamado.objects.filter(
            Q(status__in=["ABERTO", "ATENDIMENTO"]) |
            Q(id__in=list(ultimos_finalizados))
        )


    # =========================================================
    # CHAMADOS FINALIZADOS
    # =========================================================

    elif status_filtro == "finalizados":

        chamados_abertos = Chamado.objects.filter(
            status="FINALIZADO"
        )


    # =========================================================
    # TODOS OS CHAMADOS
    # =========================================================

    elif status_filtro == "todos":

        chamados_abertos = Chamado.objects.all()


    # =========================================================
    # FILTRO PADRÃO
    # =========================================================

    else:

        chamados_abertos = Chamado.objects.filter(
            status__in=["ABERTO", "ATENDIMENTO"]
        )


    # =========================================================
    # FILTRO POR SOLICITANTE
    # =========================================================

    if solicitante_filtro:

        chamados_abertos = chamados_abertos.filter(
            solicitante__icontains=solicitante_filtro
        )


    # =========================================================
    # FILTRO POR SETOR
    # =========================================================

    if setor_id:

        chamados_abertos = chamados_abertos.filter(
            setor_id=setor_id
        )


    # =========================================================
    # FILTRO POR LOCAL
    # =========================================================

    if local_id:

        chamados_abertos = chamados_abertos.filter(
            local_cadastrado_id=local_id
        )


    # =========================================================
    # ORDENAÇÃO
    # =========================================================

    if status_filtro == "abertos":

        # Para a tela principal:
        # chamados em aberto/em atendimento aparecem primeiro,
        # depois os finalizados mais recentes.

        chamados_abertos = chamados_abertos.order_by(
            "-data_abertura"
        )

    elif status_filtro == "finalizados":

        chamados_abertos = chamados_abertos.order_by(
            "-data_finalizacao",
            "-data_abertura"
        )

    else:

        chamados_abertos = chamados_abertos.order_by(
            "-data_abertura"
        )


    # =========================================================
    # SETORES E LOCAIS
    # =========================================================

    setores = Setor.objects.filter(
        ativo=True
    )

    locais = Local.objects.filter(
        ativo=True
    )


    # =========================================================
    # QUANTIDADE POR PÁGINA
    # =========================================================

    quantidade = request.GET.get(
        "per_page",
        "20"
    )

    try:

        quantidade = int(
            quantidade
        )

    except ValueError:

        quantidade = 20


    if quantidade not in [
        10,
        20,
        30,
        40,
        50
    ]:

        quantidade = 20


    # =========================================================
    # PAGINAÇÃO
    # =========================================================

    paginator = Paginator(
        chamados_abertos,
        quantidade
    )

    pagina = request.GET.get(
        "page",
        1
    )

    chamados = paginator.get_page(
        pagina
    )


    # =========================================================
    # RENDER
    # =========================================================

    return render(
        request,
        "chamados/inicio.html",
        {
            "setores": setores,
            "locais": locais,
            "chamados": chamados,
            "quantidades_por_pagina": [
                10,
                20,
                30,
                40,
                50
            ],
        }
    )


def abrir_chamado(request):

    if request.method == "POST":

        setor_id = request.POST.get("setor")
        local_id = request.POST.get("local")
        descricao = request.POST.get("descricao", "").strip()
        solicitante = request.POST.get("solicitante", "").strip()
        if not descricao:
            return render(
                request,
                "chamados/abrir_chamado.html",
                {
                    "setores": Setor.objects.filter(ativo=True),
                    "locais": Local.objects.filter(ativo=True),
                    "chamados": Chamado.objects.filter(
                        status__in=["ABERTO", "ATENDIMENTO"]
                    ).order_by("data_abertura"),
                    "erro": "A descrição do chamado é obrigatória.",
                }
            )

        setor = get_object_or_404(
            Setor,
            id=setor_id,
            ativo=True
        )

        local = get_object_or_404(
            Local,
            id=local_id,
            ativo=True
        )

        chamado = Chamado.objects.create(
            setor=setor,
            local_cadastrado=local,
            solicitante=solicitante,
            descricao=descricao,
        )

        HistoricoChamado.objects.create(
            chamado=chamado,
            status=chamado.status,
        )

        return render(
            request,
            "chamados/sucesso.html",
            {
                "chamado": chamado
            }
        )

    setores = Setor.objects.filter(
        ativo=True
    )

    locais = Local.objects.filter(
        ativo=True
    )

    chamados_abertos = Chamado.objects.filter(
        status__in=["ABERTO", "ATENDIMENTO"]
    ).order_by("data_abertura")

    return render(
        request,
        "chamados/abrir_chamado.html",
        {
            "setores": setores,
            "locais": locais,
            "chamados": chamados_abertos,
        }
    )


def consultar_chamado(request, numero):

    chamado = get_object_or_404(
        Chamado,
        numero=numero
    )

    return render(
        request,
        "chamados/consultar_chamado.html",
        {
            "chamado": chamado
        }
    )


def verificar_novo_chamado(request):
    ultimo_chamado = Chamado.objects.order_by("-numero").first()

    return JsonResponse({
        "ultimo_numero": ultimo_chamado.numero if ultimo_chamado else 0
    })

def verificar_status_chamados(request):
    chamados = Chamado.objects.select_related(
        "setor",
        "local_cadastrado",
    ).all()

    dados = []

    for chamado in chamados:
        dados.append({
            "numero": chamado.numero,
            "status": chamado.status,
            "solicitante": chamado.solicitante,
            "setor": chamado.setor.nome,
            "local": (
                chamado.local_cadastrado.nome
                if chamado.local_cadastrado
                else ""
            ),
            "data_abertura": chamado.data_abertura.strftime(
                "%d/%m/%Y %H:%M"
            ),
        })

    return JsonResponse({
        "chamados": dados
    })