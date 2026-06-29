document.addEventListener('click', function (event) {
  const target = event.target.closest('.confirm-action');
  if (!target) {
    return;
  }

  const message = target.getAttribute('data-confirm') || 'Are you sure?';
  if (!window.confirm(message)) {
    event.preventDefault();
  }
});

document.addEventListener('DOMContentLoaded', function () {
  const appointmentForm = document.querySelector('.appointment-form');
  if (!appointmentForm) {
    return;
  }

  const dateInput = appointmentForm.querySelector('input[type="date"]');
  const timeSelect = appointmentForm.querySelector('select[name="time"]');

  if (!dateInput || !timeSelect) {
    return;
  }

  const loadSlots = async () => {
    const dateValue = dateInput.value;
    if (!dateValue) {
      timeSelect.innerHTML = '<option value="">Select a date first</option>';
      return;
    }

    timeSelect.disabled = true;
    timeSelect.innerHTML = '<option value="">Loading slots...</option>';

    try {
      const response = await fetch(`/slots/?date=${encodeURIComponent(dateValue)}`);
      const data = await response.json();
      const slots = data.slots || [];

      timeSelect.innerHTML = '';
      if (!slots.length) {
        timeSelect.innerHTML = '<option value="">No slots available</option>';
      } else {
        timeSelect.innerHTML = '<option value="">Select a time slot</option>';
        slots.forEach((slot) => {
          const option = document.createElement('option');
          option.value = slot.value;
          option.textContent = slot.label;
          timeSelect.appendChild(option);
        });
      }
    } catch (error) {
      timeSelect.innerHTML = '<option value="">Unable to load slots</option>';
    } finally {
      timeSelect.disabled = false;
    }
  };

  dateInput.addEventListener('change', loadSlots);
});
