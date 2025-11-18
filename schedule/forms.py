from django import forms
from .models import Appointment, Worker, WorkerAvailability
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


# WorkerAvailability

class WorkerAvailabilityForm(forms.ModelForm):
    # Campos de horário (turnos A e B)
    monday_start_at = forms.TimeField(label="Início", required=False)
    monday_finish_at = forms.TimeField(label="Fim", required=False)
    monday_start_at_b = forms.TimeField(label="Início", required=False)
    monday_finish_at_b = forms.TimeField(label="Fim", required=False)

    tuesday_start_at = forms.TimeField(label="Início", required=False)
    tuesday_finish_at = forms.TimeField(label="Fim", required=False)
    tuesday_start_at_b = forms.TimeField(label="Início", required=False)
    tuesday_finish_at_b = forms.TimeField(label="Fim", required=False)
    
    wednesday_start_at = forms.TimeField(label="Início", required=False)
    wednesday_finish_at = forms.TimeField(label="Fim", required=False)
    wednesday_start_at_b = forms.TimeField(label="Início", required=False)
    wednesday_finish_at_b = forms.TimeField(label="Fim", required=False)
    
    thursday_start_at = forms.TimeField(label="Início", required=False)
    thursday_finish_at = forms.TimeField(label="Fim", required=False)
    thursday_start_at_b = forms.TimeField(label="Início", required=False)
    thursday_finish_at_b = forms.TimeField(label="Fim", required=False)
    
    friday_start_at = forms.TimeField(label="Início", required=False)
    friday_finish_at = forms.TimeField(label="Fim", required=False)
    friday_start_at_b = forms.TimeField(label="Início", required=False)
    friday_finish_at_b = forms.TimeField(label="Fim", required=False)
    
    saturday_start_at = forms.TimeField(label="Início", required=False)
    saturday_finish_at = forms.TimeField(label="Fim", required=False)
    saturday_start_at_b = forms.TimeField(label="Início", required=False)
    saturday_finish_at_b = forms.TimeField(label="Fim", required=False)
    
    sunday_start_at = forms.TimeField(label="Início", required=False)
    sunday_finish_at = forms.TimeField(label="Fim", required=False)
    sunday_start_at_b = forms.TimeField(label="Início", required=False)
    sunday_finish_at_b = forms.TimeField(label="Fim", required=False)

    class Meta:
        model = WorkerAvailability
        fields = [
            "worker",
            "monday_start_at", "monday_finish_at", "monday_start_at_b", "monday_finish_at_b",
            "tuesday_start_at", "tuesday_finish_at", "tuesday_start_at_b", "tuesday_finish_at_b",
            "wednesday_start_at", "wednesday_finish_at", "wednesday_start_at_b", "wednesday_finish_at_b",
            "thursday_start_at", "thursday_finish_at", "thursday_start_at_b", "thursday_finish_at_b",
            "friday_start_at", "friday_finish_at", "friday_start_at_b", "friday_finish_at_b",
            "saturday_start_at", "saturday_finish_at", "saturday_start_at_b", "saturday_finish_at_b",
            "sunday_start_at", "sunday_finish_at", "sunday_start_at_b", "sunday_finish_at_b",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Garante que o campo "worker" exista no formulário
        if "worker" not in self.fields:
            self.fields["worker"] = forms.ModelChoiceField(
                queryset=Worker.objects.filter(availability__isnull=True),
                label="Agenda",
                required=True,
            )

        is_new = not self.instance.pk or getattr(self.instance._state, "adding", False)

        if is_new:
            # 🔹 Criação → mostra apenas workers sem disponibilidade
            self.fields["worker"].queryset = Worker.objects.exclude(
                pk__in=WorkerAvailability.objects.values('worker_id')
            )
        else:
            # 🔸 Edição → trava no worker atual
            self.fields["worker"].queryset = Worker.objects.filter(pk=self.instance.worker_id)




        # Função auxiliar para inicializar campos de turno com segurança
        def init_turno(field_prefix, valores):
            if not valores:
                return
            if len(valores) >= 1 and valores[0]:
                start, end = valores[0]
                self.fields[f"{field_prefix}_start_at"].initial = start
                self.fields[f"{field_prefix}_finish_at"].initial = end
            if len(valores) >= 2 and valores[1]:
                start, end = valores[1]
                self.fields[f"{field_prefix}_start_at_b"].initial = start
                self.fields[f"{field_prefix}_finish_at_b"].initial = end

        # Inicializa os campos para cada dia
        for dia in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            valores = getattr(self.instance, dia, None)
            init_turno(dia, valores)

    def save(self, commit=True):
        instance = super().save(commit=False)

        def fmt(field):
            val = self.cleaned_data.get(field)
            return val.strftime('%H:%M') if val else None

        def clean_day(turno_a, turno_b):
            turnos = [t for t in [turno_a, turno_b] if any(t)]
            return turnos if turnos else None

        instance.monday = clean_day([fmt("monday_start_at"), fmt("monday_finish_at")],
                                    [fmt("monday_start_at_b"), fmt("monday_finish_at_b")])
        instance.tuesday = clean_day([fmt("tuesday_start_at"), fmt("tuesday_finish_at")],
                                     [fmt("tuesday_start_at_b"), fmt("tuesday_finish_at_b")])
        instance.wednesday = clean_day([fmt("wednesday_start_at"), fmt("wednesday_finish_at")],
                                       [fmt("wednesday_start_at_b"), fmt("wednesday_finish_at_b")])
        instance.thursday = clean_day([fmt("thursday_start_at"), fmt("thursday_finish_at")],
                                      [fmt("thursday_start_at_b"), fmt("thursday_finish_at_b")])
        instance.friday = clean_day([fmt("friday_start_at"), fmt("friday_finish_at")],
                                    [fmt("friday_start_at_b"), fmt("friday_finish_at_b")])
        instance.saturday = clean_day([fmt("saturday_start_at"), fmt("saturday_finish_at")],
                                      [fmt("saturday_start_at_b"), fmt("saturday_finish_at_b")])
        instance.sunday = clean_day([fmt("sunday_start_at"), fmt("sunday_finish_at")],
                                    [fmt("sunday_start_at_b"), fmt("sunday_finish_at_b")])

        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        dias = [
            ("monday", "segunda-feira"), ("tuesday", "terça-feira"), ("wednesday", "quarta-feira"),
            ("thursday", "quinta-feira"), ("friday", "sexta-feira"), ("saturday", "sábado"), ("sunday", "domingo"),
        ]

        for dia, label_dia in dias:
            start_a = cleaned_data.get(f"{dia}_start_at")
            end_a = cleaned_data.get(f"{dia}_finish_at")
            start_b = cleaned_data.get(f"{dia}_start_at_b")
            end_b = cleaned_data.get(f"{dia}_finish_at_b")

            # Regras de validação
            if bool(start_a) != bool(end_a):
                self.add_error(f"{dia}_finish_at" if start_a else f"{dia}_start_at",
                               f"Preencha ambos os horários do {label_dia} (turno A).")
            if bool(start_b) != bool(end_b):
                self.add_error(f"{dia}_finish_at_b" if start_b else f"{dia}_start_at_b",
                               f"Preencha ambos os horários do {label_dia} (turno B).")
            if start_a and end_a and end_a <= start_a:
                self.add_error(f"{dia}_finish_at", f"O horário final deve ser maior que o inicial em {label_dia} (turno A).")
            if start_b and end_b and end_b <= start_b:
                self.add_error(f"{dia}_finish_at_b", f"O horário final deve ser maior que o inicial em {label_dia} (turno B).")
            if start_a and end_a and start_b and start_b <= end_a:
                self.add_error(f"{dia}_start_at_b", f"O início do turno B deve ser maior que o término do turno A em {label_dia}.")

        return cleaned_data
