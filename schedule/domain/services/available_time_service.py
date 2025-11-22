from organization.models import SchedulingConfig
from schedule.models import SchedulingWindow, WorkerAvailability, Appointment
from datetime import datetime, timedelta
from django.db.models import Sum

from datetime import datetime, timedelta

class FinalTimeResponseBuilder:

    @staticmethod
    def build(date_obj, adjusted_windows, total_duration):
        now = datetime.now()
        today = now.date()

        # NOVO: agora + 10 minutos
        now_plus_10 = now + timedelta(minutes=10)

        response = {}
        index = 1

        for w in adjusted_windows:
            window_start = datetime.combine(date_obj, datetime.strptime(w["start"], "%H:%M").time())
            window_end   = datetime.combine(date_obj, datetime.strptime(w["end"], "%H:%M").time())

            # Se é hoje e a janela já acabou → ignora
            if date_obj == today and window_end <= now_plus_10:
                continue

            # Primeiro horário possível dentro da janela
            if date_obj == today:
                start_dt = max(window_start, now_plus_10)
            else:
                start_dt = window_start

            first_end = start_dt + timedelta(minutes=total_duration)

            # Se cabe a primeira opção
            if first_end <= window_end:
                response[index] = {
                    "horario_inicio": start_dt.strftime("%H:%M"),
                    "horario_fim": first_end.strftime("%H:%M"),
                }
                index += 1

            # Agora gerar horários em horas cheias: 11:00, 12:00, 13:00, etc.
            next_hour = (start_dt + timedelta(hours=1)).replace(
                minute=0, second=0, microsecond=0
            )

            while True:
                next_end = next_hour + timedelta(minutes=total_duration)
                if next_end > window_end:
                    break

                response[index] = {
                    "horario_inicio": next_hour.strftime("%H:%M"),
                    "horario_fim": next_end.strftime("%H:%M"),
                }

                index += 1
                next_hour += timedelta(hours=1)

        return response



class AvailableTimeService:

    @staticmethod
    def generate_time_ranges(worker_id, date, appointments, enterprise_id):

        try:
            date_obj = datetime.strptime(date, "%d/%m/%Y").date()
        except:
            return {}

        config = SchedulingConfig.objects.filter(
            enterprise_id=enterprise_id
        ).first()

        overlap_tolerance = config.overlap_tolerance if config else 0

        # =====================================================
        # 1️⃣ Calcular duração total dos appointments selecionados
        # =====================================================
        total_duration = Appointment.objects.filter(
            id__in=appointments
        ).aggregate(Sum("duration"))["duration__sum"] or 0

        # =====================================================
        # 2️⃣ Montar a janela (window ou availability)
        # =====================================================
        schedule_window = []

        window = SchedulingWindow.objects.filter(
            worker_id=worker_id,
            date=date_obj
        ).first()

        if window:
            for interval in window.intervals.all():
                schedule_window.append({
                    "start": interval.start_time.strftime("%H:%M"),
                    "end": interval.end_time.strftime("%H:%M"),
                    "duration": interval.duration,
                })
        else:
            availability = WorkerAvailability.objects.filter(
                worker_id=worker_id
            ).first()

            if availability:
                weekday_map = [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ]
                weekday_field = weekday_map[date_obj.weekday()]
                day_blocks = getattr(availability, weekday_field, [])

                for block in day_blocks:
                    start_str, end_str = block
                    start_dt = datetime.strptime(start_str, "%H:%M")
                    end_dt = datetime.strptime(end_str, "%H:%M")
                    duration = int((end_dt - start_dt).total_seconds() // 60)

                    schedule_window.append({
                        "start": start_str,
                        "end": end_str,
                        "duration": duration,
                    })

        # =====================================================
        # 3️⃣ Ajustar intervalo aplicando overlap_tolerance
        # =====================================================
        adjusted_windows = []

        for block in schedule_window:
            start_str = block["start"]
            end_str = block["end"]

            start_dt = datetime.strptime(start_str, "%H:%M")
            end_dt = datetime.strptime(end_str, "%H:%M")

            end_dt_adjusted = end_dt + timedelta(minutes=overlap_tolerance)
            new_duration = int((end_dt_adjusted - start_dt).total_seconds() // 60)

            adjusted_windows.append({
                "start": start_dt.strftime("%H:%M"),
                "end": end_dt_adjusted.strftime("%H:%M"),
                "duration": new_duration,
            })

        return FinalTimeResponseBuilder.build(date_obj, adjusted_windows, total_duration)
