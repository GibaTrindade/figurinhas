from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Troca


class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ObservacaoFigurinhaForm(forms.Form):
    quantidade = forms.IntegerField(min_value=0, label='Quantidade')
    observacao = forms.CharField(
        label='Observacao',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class TrocaForm(forms.ModelForm):
    figurinhas_dei = forms.CharField(
        label='Figurinhas que dei',
        required=False,
        help_text='Digite os numeros separados por virgula. Ex: 1, 2, 15',
    )
    figurinhas_recebi = forms.CharField(
        label='Figurinhas que recebi',
        required=False,
        help_text='Digite os numeros separados por virgula. Ex: 3, 8, 21',
    )

    class Meta:
        model = Troca
        fields = ('nome_pessoa', 'data', 'observacao')
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'observacao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].initial = timezone.localdate()
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_figurinhas_dei(self):
        return self._limpar_numeros('figurinhas_dei')

    def clean_figurinhas_recebi(self):
        return self._limpar_numeros('figurinhas_recebi')

    def _limpar_numeros(self, campo):
        valor = self.cleaned_data.get(campo, '')
        if not valor:
            return []

        numeros = []
        for item in valor.replace(';', ',').split(','):
            item = item.strip()
            if not item:
                continue
            if not item.isdigit():
                raise forms.ValidationError('Use apenas numeros separados por virgula.')
            numeros.append(int(item))
        return numeros
