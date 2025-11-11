from django.shortcuts import render, redirect
from .forms import WorkerAvailabilityForm
from .models import WorkerAvailability

def criar_evento(request):
    if request.method == 'POST':
        form = WorkerAvailabilityForm(request.POST)
        if form.is_valid():
            monday_start_at = form.cleaned_data['monday_start_at'].strftime('%H:%M')
            monday_finish_at = form.cleaned_data['monday_finish_at'].strftime('%H:%M')
            monday_start_at_b = form.cleaned_data['monday_start_at_b'].strftime('%H:%M')
            monday_finish_at_b = form.cleaned_data['monday_finish_at_b'].strftime('%H:%M')
            
            tuesday_start_at = form.cleaned_data['tuesday_start_at'].strftime('%H:%M')
            tuesday_finish_at = form.cleaned_data['tuesday_finish_at'].strftime('%H:%M')
            tuesday_start_at_b = form.cleaned_data['tuesday_start_at_b'].strftime('%H:%M')
            tuesday_finish_at_b = form.cleaned_data['tuesday_finish_at_b'].strftime('%H:%M')
            
            wednesday_start_at = form.cleaned_data['wednesday_start_at'].strftime('%H:%M')
            wednesday_finish_at = form.cleaned_data['wednesday_finish_at'].strftime('%H:%M')
            wednesday_start_at_b = form.cleaned_data['wednesday_start_at_b'].strftime('%H:%M')
            wednesday_finish_at_b = form.cleaned_data['wednesday_finish_at_b'].strftime('%H:%M')
            
            thursday_start_at = form.cleaned_data['thursday_start_at'].strftime('%H:%M')
            thursday_finish_at = form.cleaned_data['thursday_finish_at'].strftime('%H:%M')
            thursday_start_at_b = form.cleaned_data['thursday_start_at_b'].strftime('%H:%M')
            thursday_finish_at_b = form.cleaned_data['thursday_finish_at_b'].strftime('%H:%M')
            
            friday_start_at = form.cleaned_data['friday_start_at'].strftime('%H:%M')
            friday_finish_at = form.cleaned_data['friday_finish_at'].strftime('%H:%M')
            friday_start_at_b = form.cleaned_data['friday_start_at_b'].strftime('%H:%M')
            friday_finish_at_b = form.cleaned_data['friday_finish_at_b'].strftime('%H:%M')
            
            saturday_start_at = form.cleaned_data['saturday_start_at'].strftime('%H:%M')
            saturday_finish_at = form.cleaned_data['saturday_finish_at'].strftime('%H:%M')
            saturday_start_at_b = form.cleaned_data['saturday_start_at_b'].strftime('%H:%M')
            saturday_finish_at_b = form.cleaned_data['saturday_finish_at_b'].strftime('%H:%M')
            
            sunday_start_at = form.cleaned_data['sunday_start_at'].strftime('%H:%M')
            sunday_finish_at = form.cleaned_data['sunday_finish_at'].strftime('%H:%M')
            sunday_start_at_b = form.cleaned_data['sunday_start_at_b'].strftime('%H:%M')
            sunday_finish_at_b = form.cleaned_data['sunday_finish_at_b'].strftime('%H:%M')
            
            WorkerAvailability.objects.create(monday=[
              [monday_start_at, monday_finish_at],
              [monday_start_at_b, monday_finish_at_b]
            ])

            WorkerAvailability.objects.create(tuesday=[
              [tuesday_start_at, tuesday_finish_at],
              [tuesday_start_at_b, tuesday_finish_at_b]
            ])

            WorkerAvailability.objects.create(wednesday=[
              [wednesday_start_at, wednesday_finish_at],
              [wednesday_start_at_b, wednesday_finish_at_b]
            ])

            WorkerAvailability.objects.create(thursday=[
              [thursday_start_at, thursday_finish_at],
              [thursday_start_at_b, thursday_finish_at_b]
            ])

            WorkerAvailability.objects.create(friday=[
              [friday_start_at, friday_finish_at],
              [friday_start_at_b, friday_finish_at_b]
            ])

            WorkerAvailability.objects.create(saturday=[
              [saturday_start_at, saturday_finish_at],
              [saturday_start_at_b, saturday_finish_at_b]
            ])

            WorkerAvailability.objects.create(sunday=[
              [sunday_start_at, sunday_finish_at],
              [sunday_start_at_b, sunday_finish_at_b]
            ])

            return redirect('sucesso')
    else:
        form = WorkerAvailabilityForm()
    return render(request, 'availability_form.html', {'form': form})