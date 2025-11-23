from datetime import datetime
from django.db import transaction
from core.utils.redis_lock import redis_lock
from schedule.models import Scheduling
from schedule.domain.services.available_time_service import AvailableTimeService


class SchedulingService:

    @staticmethod
    def _parse_date(date_value):
        if hasattr(date_value, "year"):  # já é date
            return date_value
        if isinstance(date_value, str):
            for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
        raise ValueError("Data inválida.")

    @staticmethod
    def _parse_time(time_value):
        if hasattr(time_value, "hour"):  # já é time
            return time_value
        if isinstance(time_value, str):
            return datetime.strptime(time_value, "%H:%M").time()
        raise ValueError("Horário inválido.")

    @staticmethod
    @transaction.atomic
    def create(worker_id, client_id, appointments, date, start_time, enterprise_id, notes=None):

        # normalizar tipos (Admin pode mandar string)
        date_obj = SchedulingService._parse_date(date)
        start_time_obj = SchedulingService._parse_time(start_time)

        lock_key = f"worker:{worker_id}"

        with redis_lock(lock_key):

            available = AvailableTimeService.generate_time_ranges(
                worker_id=worker_id,
                date=date_obj.strftime("%d/%m/%Y"),  # seu AvailableTimeService espera string BR
                appointments=appointments,
                enterprise_id=enterprise_id,
            )

            is_valid = any(
                slot["horario_inicio"] == start_time_obj.strftime("%H:%M")
                for slot in available.values()
            )

            if not is_valid:
                raise ValueError("Este horário não está mais disponível.")

            scheduling = Scheduling.objects.create(
                worker_id=worker_id,
                enterprise_id=enterprise_id,
                client_id=client_id,
                date=date_obj,
                start_time=start_time_obj,
                notes=notes,
            )

            scheduling.appointments.set(appointments)

            # mantém sua lógica original do model (recalcula e salva)
            scheduling.update_duration_and_end_time()
            scheduling.save(update_fields=["duration", "end_time"])

            return scheduling
