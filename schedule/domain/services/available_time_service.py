class AvailableTimeService:

    @staticmethod
    def generate_time_ranges(worker_id, date, appointments):
        """
        worker_id: ID do profissional
        date: string YYYY-MM-DD
        appointments: lista de IDs dos atendimentos selecionados
        """

        print("WORKER:", worker_id)
        print("DATE:", date)
        print("APPOINTMENTS:", appointments)

        # Aqui você vai montar a lógica real depois
        return {
            1: {"horario_inicio": "08:00", "horario_fim": "10:00"},
            2: {"horario_inicio": "09:00", "horario_fim": "12:00"},
            3: {"horario_inicio": "13:00", "horario_fim": "15:00"},
        }
