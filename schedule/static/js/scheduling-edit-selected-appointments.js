// static/js/scheduling-edit-selected-apointments.js

(function () {
    document.addEventListener("DOMContentLoaded", function () {

        const workerSelect = document.getElementById("id_worker");
        const clientSelect = document.getElementById("id_client");
        const dateInput = document.getElementById("id_date");
        const appointmentCheckboxes = document.querySelectorAll("#id_appointments input[type=checkbox]");

        // ------------------------------------------------------
        // 🔥 LIMPAR HORÁRIOS AO SELECIONAR O INPUT DE DATA
        // ------------------------------------------------------
        if (dateInput) {
            dateInput.addEventListener("focus", function () {
                const scheduleOption = document.getElementById("id_schedule_option");
                if (scheduleOption) {
                    scheduleOption.innerHTML = "";

                    const opt = document.createElement("option");
                    opt.value = "";
                    opt.textContent = "Selecione um horário";
                    scheduleOption.appendChild(opt);
                }
            });
        }

        // 🔥 Trocar profissional → zerar appointments
        if (workerSelect) {
            workerSelect.addEventListener("change", function () {
                appointmentCheckboxes.forEach(cb => cb.checked = false);

                const url = new URL(window.location.href);

                url.searchParams.set("worker", workerSelect.value);
                url.searchParams.set("appointments", "null");

                if (clientSelect && clientSelect.value)
                    url.searchParams.set("client", clientSelect.value);

                if (dateInput && dateInput.value)
                    url.searchParams.set("date", dateInput.value);

                window.location.href = url.toString();
            });
        }

        // 🔥 Função de reload usada por cliente e appointments
        function reload() {
            const selected = Array.from(appointmentCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);

            const workerId = workerSelect ? workerSelect.value : "";
            const clientId = clientSelect ? clientSelect.value : "";
            const dateVal = dateInput ? dateInput.value : "";

            const url = new URL(window.location.href);

            if (workerId)
                url.searchParams.set("worker", workerId);

            if (clientId)
                url.searchParams.set("client", clientId);

            if (dateVal)
                url.searchParams.set("date", dateVal);

            if (selected.length > 0) {
                url.searchParams.set("appointments", selected.join(","));
            } else {
                url.searchParams.delete("appointments");
            }

            window.location.href = url.toString();
        }

        // appointments → reload normal
        appointmentCheckboxes.forEach(cb => cb.addEventListener("change", reload));

        // client → reload normal
        if (clientSelect) clientSelect.addEventListener("change", reload);

        // data → reload via blur
        if (dateInput) {
            dateInput.addEventListener("blur", function () {
                if (dateInput.value) reload();
            });
        }

    });
})();
