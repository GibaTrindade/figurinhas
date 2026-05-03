from django.conf import settings
from django.db import models
from django.urls import reverse


class Selecao(models.Model):
    nome = models.CharField(max_length=80)
    grupo = models.CharField(max_length=20, blank=True)
    bandeira_emoji = models.CharField(max_length=8, blank=True)
    bandeira_codigo = models.CharField(max_length=10, blank=True)
    codigo_album = models.CharField(max_length=5, blank=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = 'Selecao'
        verbose_name_plural = 'Selecoes'

    def __str__(self):
        return self.nome


class CategoriaFigurinha(models.Model):
    nome = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Categoria de figurinha'
        verbose_name_plural = 'Categorias de figurinhas'

    def __str__(self):
        return self.nome


class SecaoEspecial(models.Model):
    nome = models.CharField(max_length=80)
    codigo_album = models.CharField(max_length=8, unique=True)
    cor = models.CharField(max_length=20, default='#245b3d')
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = 'Secao especial'
        verbose_name_plural = 'Secoes especiais'

    def __str__(self):
        return self.nome


class Figurinha(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    nome = models.CharField(max_length=120)
    selecao = models.ForeignKey(Selecao, on_delete=models.CASCADE, related_name='figurinhas', null=True, blank=True)
    secao_especial = models.ForeignKey(SecaoEspecial, on_delete=models.CASCADE, related_name='figurinhas', null=True, blank=True)
    categoria = models.ForeignKey(CategoriaFigurinha, on_delete=models.PROTECT, related_name='figurinhas')
    descricao = models.TextField(blank=True)
    especial = models.BooleanField(default=False)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['selecao__ordem', 'ordem', 'numero']
        verbose_name = 'Figurinha'
        verbose_name_plural = 'Figurinhas'

    def __str__(self):
        return f'{self.numero} - {self.nome}'

    @property
    def codigo_album(self):
        if self.selecao_id:
            return self.selecao.codigo_album
        if self.secao_especial_id:
            return self.secao_especial.codigo_album
        return ''

    def get_absolute_url(self):
        return reverse('figurinha_detail', args=[self.pk])


class ColecaoFigurinha(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='colecao')
    figurinha = models.ForeignKey(Figurinha, on_delete=models.CASCADE, related_name='colecoes')
    quantidade = models.PositiveIntegerField(default=0)
    observacao = models.TextField(blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'figurinha')
        ordering = ['figurinha__numero']
        verbose_name = 'Colecao de figurinha'
        verbose_name_plural = 'Colecoes de figurinhas'

    def __str__(self):
        return f'{self.user} - {self.figurinha} ({self.quantidade})'

    @property
    def tem(self):
        return self.quantidade >= 1

    @property
    def repetida(self):
        return self.quantidade > 1

    @property
    def disponivel_troca(self):
        return max(self.quantidade - 1, 0)


class Troca(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trocas')
    nome_pessoa = models.CharField(max_length=120)
    data = models.DateField()
    observacao = models.TextField(blank=True)

    class Meta:
        ordering = ['-data', '-id']
        verbose_name = 'Troca'
        verbose_name_plural = 'Trocas'

    def __str__(self):
        return f'Troca com {self.nome_pessoa} em {self.data:%d/%m/%Y}'


class ItemTroca(models.Model):
    TIPO_DEI = 'dei'
    TIPO_RECEBI = 'recebi'
    TIPO_CHOICES = [
        (TIPO_DEI, 'Dei'),
        (TIPO_RECEBI, 'Recebi'),
    ]

    troca = models.ForeignKey(Troca, on_delete=models.CASCADE, related_name='itens')
    figurinha = models.ForeignKey(Figurinha, on_delete=models.PROTECT, related_name='itens_troca')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['tipo', 'figurinha__numero']
        verbose_name = 'Item de troca'
        verbose_name_plural = 'Itens de troca'

    def __str__(self):
        return f'{self.get_tipo_display()}: {self.figurinha} x{self.quantidade}'
