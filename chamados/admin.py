from django.contrib import admin
from django import forms
from .models import Chamado, Setor, Local, HistoricoChamado


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


class ChamadoAdminForm(forms.ModelForm):

    class Meta:
        model = Chamado
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get("status")
        resolucao = cleaned_data.get("resolucao")

        if status == "FINALIZADO" and not resolucao:
            self.add_error(
                "resolucao",
                "Informe a resolução antes de finalizar o chamado."
            )

        return cleaned_data


@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    form = ChamadoAdminForm
    class Media:
        js = (
            "chamados/auto_refresh.js",
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
            "Atendimento",
            {
                "fields": (
                    "resolucao",
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
        "status",
        "data_abertura",
    )

    list_filter = (
        "status",
        "setor",
        "data_abertura",
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

    def save_model(self, request, obj, form, change):
        if (
            change
            and obj.status == "FINALIZADO"
            and obj.operador_finalizacao is None
        ):
            obj.operador_finalizacao = request.user

        super().save_model(request, obj, form, change)


    inlines = (
        HistoricoChamadoInline,
    )


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

def changelist_view(self, request, extra_context=None):
    if extra_context is None:
        extra_context = {}

    extra_context["auto_refresh"] = True

    return super().changelist_view(
        request,
        extra_context=extra_context
    )