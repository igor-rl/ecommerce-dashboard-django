(function() {
  document.addEventListener("DOMContentLoaded", function () {

      const enterpriseSelect = document.getElementById("id_enterprise");

      if (!enterpriseSelect) return;

      enterpriseSelect.addEventListener("change", function () {
          const enterpriseId = this.value;
          const url = new URL(window.location.href);

          if (enterpriseId) {
              url.searchParams.set("enterprise_selected", enterpriseId);
          } else {
              url.searchParams.delete("enterprise_selected");
          }

          window.location.href = url.toString();
      });

  });
})();
