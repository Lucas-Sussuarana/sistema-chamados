from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Chamado, Setor, Local, HistoricoChamado, RegistroAtendimento


# ==============================================================================
# FILTROS CUSTOMIZADOS PARA AUTORIZAR OS PARÂMETROS GET E EVITAR O ERRO ?e=1
# ==============================================================================
class FiltroGenericoCustomizado(admin.SimpleListFilter):
    title = ''

    def lookups(self, request, model_admin):
        val = request.GET.get(self.parameter_name)
        if val is not None and str(val).strip() != '':
            return ((str(val).strip(), str(val).strip()),)
        return ()

    def queryset(self, request, queryset):
        # Retornando None garantimos que o Django Admin NÃO aplique filtros
        # automáticos via banco, deixando o controle 100% no get_queryset()
        return None


class SetorFiltro(FiltroGenericoCustomizado):
    parameter_name = 'setor'


class LocalFiltro(FiltroGenericoCustomizado):
    parameter_name = 'local'


class StatusFiltro(FiltroGenericoCustomizado):
    parameter_name = 'status'


class SolicitanteFiltro(FiltroGenericoCustomizado):
    parameter_name = 'solicitante'


class PerPageFiltro(FiltroGenericoCustomizado):
    parameter_name = 'per_page'


# ==============================================================================
# ADMINISTRAÇÃO DOS MODELOS AUXILIARES
# ==============================================================================
@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "ativo",
    )

    list_filter = (
        "ativo",
    )

    search_fields = (
        "nome",
    )


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "ativo",
    )

    list_filter = (
        "ativo",
    )

    search_fields = (
        "nome",
    )

    ordering = (
        "nome",
    )


# ==============================================================================
# INLINES DO CHAMADO
# ==============================================================================
class HistoricoChamadoInline(admin.TabularInline):
    model = HistoricoChamado
    extra = 0
    can_delete = False

    fields = (
        "status",
        "data",
    )

    readonly_fields = (
        "status",
        "data",
    )


class RegistroAtendimentoInline(admin.TabularInline):
    model = RegistroAtendimento
    extra = 1
    can_delete = False
    fields = ("operador", "texto", "data")
    readonly_fields = ("operador", "data")


# ==============================================================================
# FORMULÁRIO DO CHAMADO
# ==============================================================================
class ChamadoAdminForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


# ==============================================================================
# ADMINISTRAÇÃO PRINCIPAL DE CHAMADOS
# ==============================================================================
@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    form = ChamadoAdminForm

    class Media:
        js = (
            "chamados/auto_refresh.js",
            "chamados/admin_linha_clicavel.js"
        )

    fieldsets = (
        (
            "Informações do chamado",
            {
                "fields": (
                    "numero",
                    "solicitante",
                    "setor",
                    "local_cadastrado",
                    "descricao",
                    "status",
                )
            },
        ),
        (
            "Finalização",
            {
                "fields": (
                    "operador_finalizacao",
                    "data_finalizacao",
                )
            },
        ),
        (
            "Datas",
            {
                "fields": (
                    "data_abertura",
                    "data_atualizacao",
                )
            },
        ),
    )

    list_display = (
        "numero",
        "solicitante",
        "setor",
        "local_cadastrado",
        "status_visual",
        "data_abertura",
    )

    list_filter = (
        "data_abertura",
        SetorFiltro,
        LocalFiltro,
        StatusFiltro,
        SolicitanteFiltro,
        PerPageFiltro,
    )

    search_fields = (
        "numero",
        "solicitante",
        "local_cadastrado__nome",
        "descricao",
    )

    ordering = (
        "-data_abertura",
    )

    readonly_fields = (
        "numero",
        "data_abertura",
        "data_atualizacao",
        "data_finalizacao",
        "operador_finalizacao",
    )

    inlines = (
        HistoricoChamadoInline,
        RegistroAtendimentoInline,
    )

    def status_visual(self, obj):
        classes = {
            "ABERTO": "status-aberto",
            "ATENDIMENTO": "status-atendimento",
            "FINALIZADO": "status-finalizado",
        }

        classe = classes.get(obj.status, "status-finalizado")

        return format_html(
            '<span class="admin-status {}">{}</span>',
            classe,
            obj.get_status_display(),
        )

    status_visual.short_description = "Status"

    def save_model(self, request, obj, form, change):
        if (
            change
            and obj.status == "FINALIZADO"
            and obj.operador_finalizacao is None
        ):
            obj.operador_finalizacao = request.user

        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, RegistroAtendimento):
                if instance.pk is None:
                    instance.operador = request.user

            instance.save()

        formset.save_m2m()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        setor = request.GET.get("setor")
        local = request.GET.get("local")
        status = request.GET.get("status")
        solicitante = request.GET.get("solicitante")

        if setor and str(setor).strip() != "":
            queryset = queryset.filter(setor_id=str(setor).strip())

        if local and str(local).strip() != "":
            queryset = queryset.filter(local_cadastrado_id=str(local).strip())

        if status and str(status).strip() != "":
            status_val = str(status).strip()
            if "," in status_val:
                lista_status = [s.strip() for s in status_val.split(",") if s.strip()]
                queryset = queryset.filter(status__in=lista_status)
            else:
                queryset = queryset.filter(status=status_val)

        if solicitante and str(solicitante).strip() != "":
            queryset = queryset.filter(
                solicitante__icontains=str(solicitante).strip()
            )

        return queryset

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        # Captura e valida a quantidade para paginação
        try:
            per_page = int(request.GET.get("per_page", 10))
        except (TypeError, ValueError):
            per_page = 10

        if per_page not in [10, 20, 30, 40, 50]:
            per_page = 10

        # Aplica na propriedade nativa do Django Admin
        self.list_per_page = per_page

        # Contexto do template
        extra_context["setores_filtro"] = Setor.objects.filter(ativo=True)
        extra_context["locais_filtro"] = Local.objects.filter(ativo=True)
        extra_context["filtros"] = {
            "setor": request.GET.get("setor", ""),
            "local": request.GET.get("local", ""),
            "status": request.GET.get("status", ""),
            "solicitante": request.GET.get("solicitante", ""),
            "per_page": per_page,
        }
        extra_context["auto_refresh"] = True

        return super().changelist_view(
            request,
            extra_context=extra_context
        )


# ==============================================================================
# OUTRAS CONFIGURAÇÕES DE ADMIN
# ==============================================================================
@admin.register(HistoricoChamado)
class HistoricoChamadoAdmin(admin.ModelAdmin):
    list_display = (
        "chamado",
        "status",
        "data",
    )

    list_filter = (
        "status",
        "data",
    )

    search_fields = (
        "chamado__numero",
    )

    ordering = (
        "-data",
    )

    readonly_fields = (
        "chamado",
        "status",
        "data",
    )


@admin.register(RegistroAtendimento)
class RegistroAtendimentoAdmin(admin.ModelAdmin):
    list_display = ("chamado", "operador", "texto", "data")
    list_filter = ("operador", "data")
    search_fields = ("chamado__numero", "texto")
    ordering = ("-data",)
    readonly_fields = ("operador", "data")