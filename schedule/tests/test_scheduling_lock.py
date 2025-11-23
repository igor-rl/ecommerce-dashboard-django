import time
import threading
import pytest
from unittest.mock import patch, MagicMock

from schedule.domain.services.scheduling_service import SchedulingService


@pytest.mark.django_db(transaction=False)
def test_redis_lock_blocks_concurrent_creates():
    """
    Teste sem tocar no banco:
    - Simula dois salvamentos simultâneos para o mesmo worker
    - O Redis lock deve bloquear um até o outro terminar.
    """

    # dado falso
    worker_id = "worker-123"
    enterprise_id = "enterprise-abc"
    client_id = "client-xyz"
    appointments = ["appt-1"]
    date = "24/11/2025"
    start_time = "10:00"

    # captura de timestamps para validar ordem de execução
    execution_order = []

    # mock de retorno do generate_time_ranges
    fake_ranges = {
        1: {"horario_inicio": "10:00", "horario_fim": "10:30"}
    }

    # simula delay no agendamento para que o lock faça efeito
    def fake_create_side_effect(*args, **kwargs):
        execution_order.append("enter")
        time.sleep(1)  # simula operação longa
        execution_order.append("exit")
        mock_sched = MagicMock()
        mock_sched.appointments.set = MagicMock()
        return mock_sched

    with patch(
        "schedule.domain.services.scheduling_service.AvailableTimeService.generate_time_ranges",
        return_value=fake_ranges
    ), patch(
        "schedule.models.Scheduling.objects.create",
        side_effect=fake_create_side_effect
    ):

        # --- THREAD 1 ---
        def t1():
            SchedulingService.create(
                worker_id, client_id, appointments,
                date, start_time, enterprise_id
            )

        # --- THREAD 2 ---
        def t2():
            SchedulingService.create(
                worker_id, client_id, appointments,
                date, start_time, enterprise_id
            )

        thread1 = threading.Thread(target=t1)
        thread2 = threading.Thread(target=t2)

        start = time.time()

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        end = time.time()
        elapsed = end - start

    # ==========================
    #  ASSERTS IMPORTANTES
    # ==========================

    # 1) Ambas as operações entraram e saíram
    assert execution_order.count("enter") == 2
    assert execution_order.count("exit") == 2

    # 2) A ordem deve ser SEQUENCIAL — nunca paralela
    #    Isso prova que uma esperou a outra
    assert execution_order == ["enter", "exit", "enter", "exit"], \
        f"Execução concorrente detectada! {execution_order}"

    # 3) O tempo total deve ser > 2 segundos (2 execuções x sleep(1))
    #    Se fosse paralelo teria terminado em ~1s.
    assert elapsed >= 2, \
        f"O lock não funcionou. Execução foi paralela (elapsed={elapsed}s)."

