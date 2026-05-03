from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('selecoes/', views.selecoes_list, name='selecoes_list'),
    path('selecoes/<int:pk>/', views.selecao_detail, name='selecao_detail'),
    path('especiais/<str:codigo>/', views.secao_especial_detail, name='secao_especial_detail'),
    path('figurinhas/<int:pk>/', views.figurinha_detail, name='figurinha_detail'),
    path('figurinhas/<int:pk>/quantidade/', views.alterar_quantidade, name='alterar_quantidade'),
    path('faltantes/', views.figurinhas_faltantes, name='figurinhas_faltantes'),
    path('repetidas/', views.figurinhas_repetidas, name='figurinhas_repetidas'),
    path('trocas/', views.trocas_list, name='trocas_list'),
    path('trocas/nova/', views.troca_nova, name='troca_nova'),
]
