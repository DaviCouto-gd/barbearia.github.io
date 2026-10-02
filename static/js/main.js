// A Tupi Barber — interações leves
document.addEventListener('DOMContentLoaded', function () {
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');

  if (toggle && header) {
    toggle.addEventListener('click', function () {
      var isOpen = header.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Fecha o menu ao clicar em um link (mobile)
    document.querySelectorAll('.main-nav a').forEach(function (link) {
      link.addEventListener('click', function () {
        header.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Ano dinâmico no rodapé
  var yearEl = document.getElementById('current-year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // Validação simples do formulário de contato (sem envio real ainda)
  var form = document.querySelector('.contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = form.querySelector('#nome');
      var msg = form.querySelector('#mensagem');
      if (name && !name.value.trim()) {
        name.focus();
        return;
      }
      var feedback = form.querySelector('.form-feedback');
      if (feedback) {
        feedback.textContent = 'Mensagem pronta! Envie também pelo WhatsApp ou Instagram para uma resposta mais rápida.';
        feedback.style.display = 'block';
      }
      form.reset();
    });
  }
});
