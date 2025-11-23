from organization.models import SchedulingConfig
from schedule.models import Scheduling, WorkerAvailability, Appointment
from datetime import datetime, timedelta
from django.db.models import Sum


class AvailableTimeService:

    # ---------------------------------------------------------
    # Helpers simples
    # ---------------------------------------------------------
    @staticmethod
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except:
            return None

    @staticmethod
    def to_minutes(hm):
        h, m = map(int, hm.split(":"))
        return h * 60 + m

    @staticmethod
    def to_str(mins):
        return f"{mins//60:02d}:{mins%60:02d}"

    # ---------------------------------------------------------
    # 1. Duração total dos appointments
    # ---------------------------------------------------------
    @staticmethod
    def get_total_duration(appointments):
        return Appointment.objects.filter(
            id__in=appointments
        ).aggregate(Sum("duration"))["duration__sum"] or 0

    # ---------------------------------------------------------
    # 2. Disponibilidade semanal do trabalhador
    # ---------------------------------------------------------
    @staticmethod
    def get_schedule_window(worker_id, date_obj):
        availability = WorkerAvailability.objects.filter(worker_id=worker_id).first()
        if not availability:
            return []

        weekday_map = [
            "monday", "tuesday", "wednesday", "thursday",
            "friday", "saturday", "sunday"
        ]

        weekday_field = weekday_map[date_obj.weekday()]
        blocks = getattr(availability, weekday_field, [])

        return [{"start": start, "end": end} for start, end in blocks]

    # ---------------------------------------------------------
    # 3. Buscar agendamentos existentes do dia
    # ---------------------------------------------------------
    @staticmethod
    def get_existing_schedulings(worker_id, date_obj, enterprise_id):
        return Scheduling.objects.filter(
            worker_id=worker_id,
            date=date_obj,
            enterprise_id=enterprise_id
        ).order_by("start_time")

    # ---------------------------------------------------------
    # 4. Filtrar agendamentos expirados
    # ---------------------------------------------------------
    @staticmethod
    def not_expired(sched, date_obj):
        now = datetime.now()
        today = now.date()

        if date_obj < today:
            return False

        if date_obj == today and sched.end_time <= now.time():
            return False

        return True

    # ---------------------------------------------------------
    # 5. Subtrair agendamentos das janelas disponíveis
    # ---------------------------------------------------------
    @staticmethod
    def subtract_busy(available_windows, scheduled_items):

        def to_minutes(hm):
            h, m = map(int, hm.split(":"))
            return h * 60 + m

        def to_str(mins):
            return f"{mins//60:02d}:{mins%60:02d}"

        window_intervals = [(to_minutes(w["start"]), to_minutes(w["end"])) for w in available_windows]
        busy_intervals   = [(to_minutes(s["start"]), to_minutes(s["end"])) for s in scheduled_items]

        busy_intervals.sort()
        free = []

        for win_start, win_end in window_intervals:
            current = win_start

            for busy_start, busy_end in busy_intervals:

                if busy_end <= current:
                    continue

                if busy_start >= win_end:
                    break

                if busy_start > current:
                    free.append((current, busy_start))

                current = max(current, busy_end)

                if current >= win_end:
                    break

            if current < win_end:
                free.append((current, win_end))

        return [{"start": to_str(s), "end": to_str(e)} for s, e in free]

    # ---------------------------------------------------------
    # 6. Ajustar janelas com overlap_tolerance
    # ---------------------------------------------------------
    @staticmethod
    def apply_overlap_tolerance(free_windows, enterprise_id):
        config = SchedulingConfig.objects.filter(enterprise_id=enterprise_id).first()
        overlap_tolerance = config.overlap_tolerance if config else 0

        adjusted = []
        for w in free_windows:
            start_dt = datetime.strptime(w["start"], "%H:%M")
            end_dt   = datetime.strptime(w["end"], "%H:%M") + timedelta(minutes=overlap_tolerance)

            adjusted.append({
                "start": start_dt.strftime("%H:%M"),
                "end":   end_dt.strftime("%H:%M")
            })

        return adjusted

    # ---------------------------------------------------------
    # 7. Gerar horários a partir das janelas ajustadas
    # ---------------------------------------------------------
    @staticmethod
    def build_final_response(date_obj, adjusted_windows, total_duration):
        now = datetime.now()
        today = now.date()
        now_plus_10 = now + timedelta(minutes=10)

        response = {}
        index = 1

        for w in adjusted_windows:

            window_start = datetime.combine(
                date_obj,
                datetime.strptime(w["start"], "%H:%M").time()
            )
            window_end = datetime.combine(
                date_obj,
                datetime.strptime(w["end"], "%H:%M").time()
            )

            # Ignorar janelas expiradas hoje
            if date_obj == today and window_end <= now_plus_10:
                continue

            # Primeiro horário válido
            start_dt = max(window_start, now_plus_10) if date_obj == today else window_start

            # Primeiro slot da janela
            first_end = start_dt + timedelta(minutes=total_duration)
            if first_end <= window_end:
                response[index] = {
                    "horario_inicio": start_dt.strftime("%H:%M"),
                    "horario_fim": first_end.strftime("%H:%M")
                }
                index += 1

            # Slots em hora cheia
            next_hour = (start_dt + timedelta(hours=1)).replace(
                minute=0, second=0, microsecond=0
            )

            while True:
                next_end = next_hour + timedelta(minutes=total_duration)
                if next_end > window_end:
                    break

                response[index] = {
                    "horario_inicio": next_hour.strftime("%H:%M"),
                    "horario_fim": next_end.strftime("%H:%M")
                }
                index += 1
                next_hour += timedelta(hours=1)

        return response

    # ---------------------------------------------------------
    # MÉTODO PRINCIPAL — orquestra tudo
    # ---------------------------------------------------------
    @staticmethod
    def generate_time_ranges(worker_id, date, appointments, enterprise_id):

        date_obj = AvailableTimeService.parse_date(date)
        if not date_obj:
            return {}

        total_duration = AvailableTimeService.get_total_duration(appointments)

        schedule_window = AvailableTimeService.get_schedule_window(worker_id, date_obj)

        existing = AvailableTimeService.get_existing_schedulings(
            worker_id, date_obj, enterprise_id
        )

        valid_schedulings = filter(
            lambda s: AvailableTimeService.not_expired(s, date_obj),
            existing
        )

        scheduled_items = [
            {"start": s.start_time.strftime("%H:%M"),
             "end":   s.end_time.strftime("%H:%M")}
            for s in valid_schedulings
        ]

        free_windows = AvailableTimeService.subtract_busy(schedule_window, scheduled_items)

        adjusted_windows = AvailableTimeService.apply_overlap_tolerance(
            free_windows, enterprise_id
        )

        return AvailableTimeService.build_final_response(
            date_obj, adjusted_windows, total_duration
        )
