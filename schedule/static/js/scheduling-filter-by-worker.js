(function() {
    document.addEventListener("DOMContentLoaded", function () {
  
        const workerSelect = document.getElementById("id_worker");
  
        if (!workerSelect) return;
  
        workerSelect.addEventListener("change", function () {
            const workerId = this.value;
            const url = new URL(window.location.href);
  
            if (workerId) {
                url.searchParams.set("worker", workerId);
            } else {
                url.searchParams.delete("worker");
            }
  
            window.location.href = url.toString();
        });
  
    });
  })();
  