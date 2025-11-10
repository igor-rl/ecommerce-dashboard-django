from django import forms
from .models import Appointment
from decimal import Decimal, InvalidOperation

class AppointmentForm(forms.ModelForm):
    
    price = forms.CharField(
        label='Preço',
        widget=forms.TextInput(attrs={'placeholder': 'R$ 0,00', 'class': 'price-input'})
    )
    
    class Meta:
        model = Appointment
        fields = "__all__"

    def clean_price(self):
        price_str = self.cleaned_data['price']
        # Remove R$, espaços e converte vírgula para ponto
        price_str = price_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
        try:
            return Decimal(price_str)
        except InvalidOperation:
            raise forms.ValidationError("Preço inválido. Use o formato R$ 1.234,56")
