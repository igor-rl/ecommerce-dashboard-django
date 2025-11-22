from django.shortcuts import render, redirect
from .forms import WorkerAvailabilityForm
from .models import WorkerAvailability


from django.http import JsonResponse
from schedule.domain.services.available_time_service import AvailableTimeService
from schedule.models import Appointment
from datetime import datetime

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



def get_available_hours(request):
    worker_id = request.GET.get("worker")
    date_str = request.GET.get("date")
    appointments_ids = request.GET.getlist("appointments[]")

    if not worker_id or not date_str:
        return JsonResponse({}, safe=False)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return JsonResponse({}, safe=False)

    appointments = Appointment.objects.filter(id__in=appointments_ids)

    result = AvailableTimeService.generate_time_ranges(
        worker_id,
        date,
        appointments,
    )

    return JsonResponse(result, safe=False)
