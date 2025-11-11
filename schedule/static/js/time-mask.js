document.addEventListener('DOMContentLoaded', () => {
  const timeInputs = document.querySelectorAll(
    'input[type="time"], ' +
    'input[name$="_start_at"], input[name$="_finish_at"], ' +
    'input[name$="_start_at_b"], input[name$="_finish_at_b"]'
  );

  timeInputs.forEach((input) => {
    input.setAttribute('placeholder', '00:00');
    input.setAttribute('inputmode', 'numeric');
    input.setAttribute('autocomplete', 'off');
    input.style.direction = 'rtl';
    input.style.textAlign = 'right';

    const mask = (raw) => {
      if (!raw) return ''; // 👈 permite apagar tudo sem erro
      let v = raw.replace(/\D/g, '').slice(0, 4);
      if (v.length >= 3) v = v.slice(0, 2) + ':' + v.slice(2);
      return v;
    };

    input.addEventListener('input', (e) => {
      const value = e.target.value;
      const masked = mask(value);
      e.target.value = masked;
    });

    input.addEventListener('keydown', (e) => {
      const allowed = [
        'Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab', 'Home', 'End'
      ];
      if (allowed.includes(e.key)) return;
      if (/^\d$/.test(e.key)) return;
      if (e.key === ':' && !e.target.value.includes(':')) return;
      e.preventDefault();
    });

    input.addEventListener('blur', (e) => {
      let raw = e.target.value.replace(/\D/g, '');
      if (raw.length === 0) return; // 👈 deixa vazio se apagar tudo
      if (raw.length === 1) raw = '0' + raw + '00';
      if (raw.length === 2) raw = raw + '00';
      if (raw.length >= 3) raw = raw.slice(0, 4);

      const hh = Math.min(parseInt(raw.slice(0, 2)) || 0, 23);
      const mm = Math.min(parseInt(raw.slice(2, 4)) || 0, 59);
      e.target.value = String(hh).padStart(2, '0') + ':' + String(mm).padStart(2, '0');
    });
  });
});
