from django.db import models
from django.conf import settings
from django.utils import timezone


class Setor(models.Model):
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
    

class Local(models.Model):
    nome = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Nome"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    class Meta:
        verbose_name = "Local"
        verbose_name_plural = "Locais"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Chamado(models.Model):

    STATUS_CHOICES = [
        ("ABERTO", "Aberto"),
        ("ATENDIMENTO", "Em atendimento"),
        ("FINALIZADO", "Finalizado"),
    ]

    numero = models.PositiveIntegerField(
    unique=True,
    editable=False,
    verbose_name="Número"
)

    setor = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT,
        related_name="chamados",
        verbose_name="Setor"
    )

    local_cadastrado = models.ForeignKey(
        Local,
        on_delete=models.PROTECT,
        related_name="chamados",
        null=True,
        blank=True,
        verbose_name="Local"
    )

    solicitante = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Solicitante"
    )

    operador_finalizacao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chamados_finalizados",
        verbose_name="Operador da finalização"
    )

    descricao = models.TextField(
        verbose_name="Descrição"
    )
    resolucao = models.TextField(
        blank=True,
        verbose_name="Resolução"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ABERTO",
        verbose_name="Status"
    )

    data_abertura = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de abertura"
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última atualização"
    )
    data_finalizacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de finalização"
    )

    def __str__(self):
        return f"Chamado #{self.numero}"

    def save(self, *args, **kwargs):

        status_anterior = None

        if self.pk:
            chamado_anterior = Chamado.objects.get(pk=self.pk)
            status_anterior = chamado_anterior.status

        if not self.numero:
            ultimo = Chamado.objects.order_by("-numero").first()

            if ultimo:
                self.numero = ultimo.numero + 1
            else:
                self.numero = 1

        if self.status == "FINALIZADO" and self.data_finalizacao is None:
            self.data_finalizacao = timezone.now()

        super().save(*args, **kwargs)

        if status_anterior is not None and status_anterior != self.status:
            HistoricoChamado.objects.create(
                chamado=self,
                status=self.status,
            )

class HistoricoChamado(models.Model):

    chamado = models.ForeignKey(
        Chamado,
        on_delete=models.CASCADE,
        related_name="historico",
        verbose_name="Chamado"
    )

    status = models.CharField(
        max_length=20,
        choices=Chamado.STATUS_CHOICES,
        verbose_name="Status"
    )

    data = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data"
    )

    def __str__(self):
        return f"Chamado #{self.chamado.numero} - {self.get_status_display()}"