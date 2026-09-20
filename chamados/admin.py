from django.contrib import admin
from django import forms
from .models import Chamado, Setor, Local, HistoricoChamado, RegistroAtendimento


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
        return cleaned_data


class RegistroAtendimentoInline(admin.TabularInline):
    model = RegistroAtendimento
    extra = 1
    can_delete = False
    fields = ("operador", "texto", "data")
    readonly_fields = ("operador", "data")

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


    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, RegistroAtendimento):
                if instance.pk is None:
                    instance.operador = request.user

            instance.save()

        formset.save_m2m()

    inlines = (
            HistoricoChamadoInline,
            RegistroAtendimentoInline,
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

@admin.register(RegistroAtendimento)
class RegistroAtendimentoAdmin(admin.ModelAdmin):
    list_display = ("chamado", "operador", "texto", "data")
    list_filter = ("operador", "data")
    search_fields = ("chamado__numero", "texto")
    ordering = ("-data",)
    readonly_fields = ("operador", "data")

