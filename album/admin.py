from django.contrib import admin

from .models import (
    CategoriaFigurinha,
    ColecaoFigurinha,
    Figurinha,
    ItemTroca,
    Selecao,
    Troca,
)


@admin.register(Selecao)
class SelecaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo_album', 'bandeira_codigo', 'grupo', 'ordem')
    list_editable = ('ordem',)
    search_fields = ('nome',)


@admin.register(CategoriaFigurinha)
class CategoriaFigurinhaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(Figurinha)
class FigurinhaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nome', 'selecao', 'categoria', 'especial', 'ordem')
    list_filter = ('selecao', 'categoria', 'especial')
    list_editable = ('ordem',)
    search_fields = ('numero', 'nome', 'selecao__nome')
    autocomplete_fields = ('selecao', 'categoria')


@admin.register(ColecaoFigurinha)
class ColecaoFigurinhaAdmin(admin.ModelAdmin):
    list_display = ('user', 'figurinha', 'quantidade', 'atualizado_em')
    list_filter = ('user', 'figurinha__selecao')
    search_fields = ('user__username', 'figurinha__numero', 'figurinha__nome')
    autocomplete_fields = ('user', 'figurinha')


class ItemTrocaInline(admin.TabularInline):
    model = ItemTroca
    extra = 1
    autocomplete_fields = ('figurinha',)


@admin.register(Troca)
class TrocaAdmin(admin.ModelAdmin):
    list_display = ('nome_pessoa', 'user', 'data')
    list_filter = ('data', 'user')
    search_fields = ('nome_pessoa', 'user__username', 'observacao')
    inlines = [ItemTrocaInline]


@admin.register(ItemTroca)
class ItemTrocaAdmin(admin.ModelAdmin):
    list_display = ('troca', 'tipo', 'figurinha', 'quantidade')
    list_filter = ('tipo', 'figurinha__selecao')
    autocomplete_fields = ('troca', 'figurinha')
