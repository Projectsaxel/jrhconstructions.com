(function () {
  var ENDPOINT = '/api/contact-form.php';

  function fieldValue(form, selector) {
    var input = form.querySelector(selector);
    return input ? String(input.value || '').trim() : '';
  }

  function setStatus(form, type, text) {
    var wrapper = form.closest('.elementor-widget-form') || form.parentElement;
    if (!wrapper) {
      return;
    }

    var existing = wrapper.querySelector('.jrh-form-status');
    if (existing) {
      existing.remove();
    }

    var status = document.createElement('div');
    status.className = 'jrh-form-status elementor-message elementor-message-' + type;
    status.setAttribute('role', 'alert');
    status.textContent = text;
    form.insertAdjacentElement('afterend', status);
  }

  function setSubmitting(form, isSubmitting) {
    var button = form.querySelector('button[type="submit"]');
    if (!button) {
      return;
    }

    if (isSubmitting) {
      button.dataset.jrhOriginalText = button.textContent.trim();
      button.disabled = true;
      button.textContent = 'Sending...';
      return;
    }

    button.disabled = false;
    if (button.dataset.jrhOriginalText) {
      button.textContent = button.dataset.jrhOriginalText;
      delete button.dataset.jrhOriginalText;
    }
  }

  function handleSubmit(event) {
    var form = event.target;
    if (!form.matches('.elementor-form')) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();

    if (form.dataset.jrhSubmitting === '1') {
      return;
    }

    form.dataset.jrhSubmitting = '1';
    setSubmitting(form, true);

    var payload = new FormData();
    payload.append('name', fieldValue(form, '[name="form_fields[name]"]'));
    payload.append('phone', fieldValue(form, '[name="form_fields[field_7f8d006]"]'));
    payload.append('email', fieldValue(form, '[name="form_fields[email]"]'));
    payload.append('city_state', fieldValue(form, '[name="form_fields[field_4d94fd8]"]'));
    payload.append('message', fieldValue(form, '[name="form_fields[field_988c5cd]"]'));
    payload.append('form_name', form.getAttribute('name') || form.getAttribute('aria-label') || '');
    payload.append('page_title', document.title || '');
    payload.append('page_url', window.location.href || '');

    fetch(ENDPOINT, {
      method: 'POST',
      body: payload,
      credentials: 'same-origin',
    })
      .then(function (response) {
        return response.json().then(function (data) {
          return { ok: response.ok, data: data };
        });
      })
      .then(function (result) {
        if (result.ok && result.data && result.data.success) {
          setStatus(form, 'success', result.data.message);
          form.reset();
          return;
        }

        var message =
          (result.data && result.data.message) ||
          'We could not send your message. Please try again or call us.';
        setStatus(form, 'danger', message);
      })
      .catch(function () {
        setStatus(form, 'danger', 'We could not send your message. Please try again or call us.');
      })
      .finally(function () {
        delete form.dataset.jrhSubmitting;
        setSubmitting(form, false);
      });
  }

  document.addEventListener('submit', handleSubmit, true);
})();
