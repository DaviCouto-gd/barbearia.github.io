// Mural de mensagens: a cada 5 segundos pergunta ao servidor se chegou algo novo.
(function () {
  var lista = document.getElementById('lista-mensagens');
  if (!lista) return;
 
  var urlApi = lista.getAttribute('data-api');
  var statusBox = document.getElementById('status-ao-vivo');
  var statusTexto = document.getElementById('status-texto');
  var vazio = document.getElementById('sem-mensagens');
  var avisoErro = document.getElementById('aviso-erro');
  var INTERVALO = 5000;
 
  var idsNaTela = [];
  lista.querySelectorAll('[data-id]').forEach(function (el) {
    idsNaTela.push(el.getAttribute('data-id'));
  });
 
  // Cria um elemento com texto. Usa textContent, então nenhum HTML digitado
  // por um visitante é interpretado pelo navegador.
  function el(tag, classe, texto) {
    var e = document.createElement(tag);
    if (classe) e.className = classe;
    if (texto) e.textContent = texto;
    return e;
  }
 
  function criarCartao(m, nova) {
    var card = el('article', 'msg-card' + (nova ? ' nova' : ''));
    card.setAttribute('data-id', m.id);
 
    var topo = el('header', 'msg-topo');
    topo.appendChild(el('strong', 'msg-nome', m.nome));
    topo.appendChild(el('time', 'msg-hora', m.hora));
    card.appendChild(topo);
 
    if (m.servico) card.appendChild(el('span', 'msg-tag', m.servico));
    if (m.dia) card.appendChild(el('p', 'msg-dia', 'Dia preferido: ' + m.dia));
    if (m.mensagem) card.appendChild(el('p', 'msg-texto', m.mensagem));
    return card;
  }
 
  function desenhar(mensagens) {
    var antigos = idsNaTela.slice();
    var frag = document.createDocumentFragment();
    mensagens.forEach(function (m) {
      var nova = antigos.indexOf(String(m.id)) === -1;
      frag.appendChild(criarCartao(m, nova));
    });
    lista.replaceChildren(frag);
    idsNaTela = mensagens.map(function (m) { return String(m.id); });
    vazio.hidden = mensagens.length > 0;
  }
 
  function mostrarStatus(ok) {
    statusBox.classList.toggle('offline', !ok);
    if (ok) {
      var agora = new Date().toLocaleTimeString('pt-BR');
      statusTexto.textContent = 'Ao vivo · atualizado às ' + agora;
    } else {
      statusTexto.textContent = 'Sem conexão com o servidor. Tentando de novo...';
    }
    if (avisoErro) avisoErro.hidden = true;
  }
 
  function atualizar() {
    fetch(urlApi, { cache: 'no-store' })
      .then(function (resp) {
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        return resp.json();
      })
      .then(function (dados) {
        var novosIds = dados.mensagens.map(function (m) { return String(m.id); });
        if (novosIds.join(',') !== idsNaTela.join(',')) {
          desenhar(dados.mensagens);
        }
        mostrarStatus(true);
      })
      .catch(function () {
        mostrarStatus(false);
      });
  }
 
  // Não gasta o banco à toa: só consulta quando a aba está visível.
  setInterval(function () {
    if (!document.hidden) atualizar();
  }, INTERVALO);
 
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) atualizar();
  });
})();
