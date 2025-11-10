from django import forms
from decimal import Decimal, InvalidOperation
from .models import Product


class ProductForm(forms.ModelForm):
    """Formulário com máscara de preço diretamente no campo `price`."""

    price = forms.CharField(
        label='Preço',
        widget=forms.TextInput(attrs={'placeholder': 'R$ 0,00', 'class': 'price-input'})
    )

    class Meta:
        model = Product
        fields = "__all__"

    def clean_price(self):
        price_str = self.cleaned_data['price']
        # Remove R$, espaços e converte vírgula para ponto
        price_str = price_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
        try:
            return Decimal(price_str)
        except InvalidOperation:
            raise forms.ValidationError("Preço inválido. Use o formato R$ 1.234,56")
