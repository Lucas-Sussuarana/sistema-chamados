from django.shortcuts import get_object_or_404, render
from .models import Chamado, Setor, Local, HistoricoChamado


def inicio(request):

    setor_id = request.GET.get("setor")
    local_id = request.GET.get("local")
    status_filtro = request.GET.get("status", "abertos")
    solicitante_filtro = request.GET.get("solicitante", "").strip()

    if status_filtro == "finalizados":
        chamados_abertos = Chamado.objects.filter(
            status="FINALIZADO"
    )
    elif status_filtro == "todos":
        chamados_abertos = Chamado.objects.all()
    else:
        chamados_abertos = Chamado.objects.filter(
            status__in=["ABERTO", "ATENDIMENTO"]
    )

        
    if solicitante_filtro:
        chamados_abertos = chamados_abertos.filter(
            solicitante__icontains=solicitante_filtro
    )
    if setor_id:
        chamados_abertos = chamados_abertos.filter(
            setor_id=setor_id
        )

    if local_id:
        chamados_abertos = chamados_abertos.filter(
            local_cadastrado_id=local_id
        )

    chamados_abertos = chamados_abertos.order_by("data_abertura")

    setores = Setor.objects.filter(
        ativo=True
    )

    locais = Local.objects.filter(
        ativo=True
    )

    return render(
        request,
        "chamados/inicio.html",
        {
            "setores": setores,
            "locais": locais,
            "chamados": chamados_abertos,
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