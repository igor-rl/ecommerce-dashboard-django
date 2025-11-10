document.addEventListener("DOMContentLoaded", function () {
    const priceInputs = document.querySelectorAll(".price-input");
  
    priceInputs.forEach((input) => {
      // Valor inicial padrão
      if (!input.value || input.value === "0") input.value = "0,00";
  
      input.addEventListener("input", (e) => {
        let value = e.target.value;
  
        // Remove tudo que não for número
        value = value.replace(/\D/g, "");
  
        if (!value) {
          e.target.value = "0,00";
          return;
        }
  
        // Converte em centavos e formata
        let intValue = parseInt(value, 10);
        let formatted = (intValue / 100).toFixed(2);
        formatted = formatted.replace(".", ",");
        formatted = formatted.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  
        e.target.value = formatted;
      });
    });
  });
  