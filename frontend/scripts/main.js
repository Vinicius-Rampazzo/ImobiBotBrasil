document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const messageInput = document.getElementById("message-input");
  const chatMessages = document.getElementById("chat-messages");
  const propertiesContainer = document.getElementById("properties-container");
  const typingIndicator = document.getElementById("typing-indicator");
  const suggestionChips = document.querySelectorAll(".suggestion-chip");

  // URL da API do chatbot (ajustar se necessário)
  const CHATBOT_API_URL = "http://127.0.0.1:8080/api/chatbot";

  // Função para adicionar mensagem ao chat
  function addMessage(content, isUser = false) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${isUser ? "user" : "bot"}`;

    // Avatar
    const avatarDiv = document.createElement("div");
    avatarDiv.className = "avatar";
    const avatarIcon = document.createElement("i");
    avatarIcon.className = isUser ? "fas fa-user" : "fas fa-robot";
    avatarDiv.appendChild(avatarIcon);

    // Conteúdo da mensagem
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    if (!isUser) {
      const nameSpan = document.createElement("span");
      nameSpan.className = "bot-name";
      nameSpan.textContent = "Louis";
      contentDiv.appendChild(nameSpan);
    }

    const contentP = document.createElement("p");
    contentP.textContent = content;
    contentDiv.appendChild(contentP);

    // Montar a mensagem
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    // Adicionar ao chat
    chatMessages.appendChild(messageDiv);

    // Rolar para a última mensagem
    scrollToBottom();
  }

  // Função para mostrar o indicador de digitação
  function showTypingIndicator() {
    typingIndicator.classList.remove("hidden");
  }

  // Função para esconder o indicador de digitação
  function hideTypingIndicator() {
    typingIndicator.classList.add("hidden");
  }

  // Função para rolar o chat para o final
  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Função para formatar valores monetários
  function formatCurrency(value) {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(value);
  }

  // Função para exibir os imóveis
  // function displayProperties(properties) {
  //   // Limpar o container de imóveis
  //   propertiesContainer.innerHTML = "";

  //   if (!properties || properties.length === 0) {
  //     propertiesContainer.innerHTML = `
  //       <div class="properties-placeholder">
  //         <i class="fas fa-search"></i>
  //         <p>Nenhum imóvel encontrado com esses critérios</p>
  //       </div>
  //     `;
  //     return;
  //   }

  //   // Criar grid de propriedades
  //   const propertiesGrid = document.createElement("div");
  //   propertiesGrid.className = "properties-grid";

  //   properties.forEach((property) => {
  //     const card = createPropertyCard(property);
  //     propertiesGrid.appendChild(card);
  //   });

  //   propertiesContainer.appendChild(propertiesGrid);
  // }

  const louisPlaceholder = document.getElementById("louis-placeholder");
  const propertiesGridContainer = document.getElementById(
    "properties-grid-container"
  );
  const propertiesTitleText = document.getElementById("properties-title-text");

  showLouisPlaceholder();

  // Função para adicionar mensagem ao chat
  function addMessage(content, isUser = false) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${isUser ? "user" : "bot"}`;

    // Avatar
    const avatarDiv = document.createElement("div");
    avatarDiv.className = "avatar";
    const avatarIcon = document.createElement("i");
    avatarIcon.className = isUser ? "fas fa-user" : "fas fa-robot";
    avatarDiv.appendChild(avatarIcon);

    // Conteúdo da mensagem
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    if (!isUser) {
      const nameSpan = document.createElement("span");
      nameSpan.className = "bot-name";
      nameSpan.textContent = "Louis";
      contentDiv.appendChild(nameSpan);
    }

    const contentP = document.createElement("p");
    contentP.textContent = content;
    contentDiv.appendChild(contentP);

    // Montar a mensagem
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    // Adicionar ao chat
    chatMessages.appendChild(messageDiv);

    // Rolar para a última mensagem
    scrollToBottom();
  }

  // Função para mostrar o indicador de digitação
  function showTypingIndicator() {
    typingIndicator.classList.remove("hidden");
  }

  // Função para esconder o indicador de digitação
  function hideTypingIndicator() {
    typingIndicator.classList.add("hidden");
  }

  // Função para rolar o chat para o final
  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Função para formatar valores monetários
  function formatCurrency(value) {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(value);
  }

  // Função para mostrar o placeholder do Louis
  function showLouisPlaceholder() {
    // Definir o título correto
    if (propertiesTitleText.textContent !== "Converse com Louis") {
      propertiesTitleText.textContent = "Converse com Louis";
    }

    // Esconde o container de grid
    propertiesGridContainer.classList.remove("active");
    propertiesGridContainer.classList.add("hidden");

    // Remove a classe exit, caso exista
    louisPlaceholder.classList.remove("exit");

    // Após um pequeno delay, mostra o placeholder do Louis
    setTimeout(() => {
      louisPlaceholder.classList.add("active");
    }, 300);
  }

  // Função para esconder o placeholder do Louis com animação melhorada
  function hideLouisPlaceholder() {
    // Adiciona a classe exit para animar a saída para cima
    louisPlaceholder.classList.add("exit");
    louisPlaceholder.classList.remove("active");

    // Após a animação terminar, esconde completamente
    setTimeout(() => {
      // Mudando o título para "Imóveis Encontrados"
      propertiesTitleText.textContent = "Imóveis Encontrados";

      // Preparando para mostrar os imóveis
      propertiesGridContainer.classList.remove("hidden");

      setTimeout(() => {
        propertiesGridContainer.classList.add("active");
      }, 100);
    }, 400); // Tempo ajustado para a duração da animação de saída
  }

  // Função para exibir os imóveis - Versão melhorada
  function displayProperties(properties) {
    if (!properties || properties.length === 0) {
      // Se não houver imóveis, mostra o placeholder do Louis
      showLouisPlaceholder();
      return;
    }

    // Limpar o container de imóveis
    propertiesGridContainer.innerHTML = "";

    // Criar grid de propriedades
    const propertiesGrid = document.createElement("div");
    propertiesGrid.className = "properties-grid";

    properties.forEach((property) => {
      const card = createPropertyCard(property);
      propertiesGrid.appendChild(card);
    });

    propertiesGridContainer.appendChild(propertiesGrid);

    // Esconder o placeholder do Louis e mostrar os imóveis
    hideLouisPlaceholder();
  }

  // Função para criar o card de um imóvel
  function createPropertyCard(property) {
    const card = document.createElement("div");
    card.className = "property-card";

    // Definir a classe de status
    const statusClass =
      property.status === "disponivel" ? "status-disponivel" : "status-locado";

    // Determinar texto baseado na finalidade
    const finalidadeText =
      property.finalidade === "locacao" ? "Aluguel" : "Venda";

    // Criar estrutura HTML do card
    card.innerHTML = `
      <div class="property-image">
        ${
          property.imagem
            ? `<img src="${property.imagem}" alt="${property.titulo}">`
            : '<i class="fas fa-home"></i>'
        }
      </div>
      <div class="property-info">
        <div class="property-title">${property.titulo || "Imóvel"}</div>
        <div class="property-price">${formatCurrency(property.preco)} ${
      property.finalidade === "locacao" ? "/mês" : ""
    }</div>
        <div><span class="property-status ${statusClass}">${
      property.status
    }</span> <span style="font-size: 0.8rem;">${finalidadeText}</span></div>
        <div class="property-meta">
          ${
            property.quartos !== undefined
              ? `
            <span><i class="fas fa-bed"></i> ${property.quartos} quarto${
                  property.quartos !== 1 ? "s" : ""
                }</span>
          `
              : ""
          }
          ${
            property.banheiros !== undefined
              ? `
            <span><i class="fas fa-bath"></i> ${property.banheiros} banheiro${
                  property.banheiros !== 1 ? "s" : ""
                }</span>
          `
              : ""
          }
        </div>
        <div class="property-ref">Ref: ${property.codigo_referencia}</div>
      </div>
    `;

    return card;
  }

  // Função para enviar mensagem para o chatbot
  async function sendMessage(message) {
    try {
      showTypingIndicator();

      const response = await fetch(CHATBOT_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ mensagem: message }),
      });

      if (!response.ok) {
        throw new Error(`Erro de servidor: ${response.status}`);
      }

      const data = await response.json();

      hideTypingIndicator();

      // Adicionar a resposta do bot
      addMessage(data.resposta, false);

      // Exibir os imóveis, se houver
      if (data.imoveis && data.imoveis.length > 0) {
        displayProperties(data.imoveis);
      }
    } catch (error) {
      console.error("Erro ao enviar mensagem:", error);
      hideTypingIndicator();
      addMessage(
        "Desculpe, tive um problema ao processar sua solicitação. Por favor, tente novamente mais tarde.",
        false
      );
    }
  }

  // Evento de envio do formulário
  chatForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const message = messageInput.value.trim();

    if (message) {
      // Adicionar a mensagem do usuário
      addMessage(message, true);

      // Enviar mensagem para o chatbot
      sendMessage(message);

      // Limpar o input
      messageInput.value = "";
    }
  });

  // Focar no input ao carregar a página
  messageInput.focus();

  // Função para animar a mudança de título
  function animateTitleChange(newTitle) {
    propertiesTitleText.classList.add("title-changing");

    setTimeout(() => {
      propertiesTitleText.textContent = newTitle;
    }, 250);

    setTimeout(() => {
      propertiesTitleText.classList.remove("title-changing");
    }, 500);
  }

  // Função para exibir os imóveis - Versão modificada
  function displayProperties(properties) {
    if (!properties || properties.length === 0) {
      // Se não houver imóveis, mostra o placeholder do Louis
      if (propertiesTitleText.textContent !== "Converse com Louis") {
        animateTitleChange("Converse com Louis");
      }
      showLouisPlaceholder();
      return;
    }

    // Se houver imóveis, esconde o placeholder e mostra os imóveis
    if (propertiesTitleText.textContent !== "Imóveis Encontrados") {
      animateTitleChange("Imóveis Encontrados");
    }

    // Limpar o container de imóveis
    propertiesGridContainer.innerHTML = "";

    // Criar grid de propriedades
    const propertiesGrid = document.createElement("div");
    propertiesGrid.className = "properties-grid";

    properties.forEach((property) => {
      const card = createPropertyCard(property);
      propertiesGrid.appendChild(card);
    });

    propertiesGridContainer.appendChild(propertiesGrid);

    // Esconder o placeholder do Louis e mostrar os imóveis
    hideLouisPlaceholder();
  }

  // Função para criar o card de um imóvel
  function createPropertyCard(property) {
    const card = document.createElement("div");
    card.className = "property-card";

    // Definir a classe de status
    const statusClass =
      property.status === "disponivel" ? "status-disponivel" : "status-locado";

    // Determinar texto baseado na finalidade
    const finalidadeText =
      property.finalidade === "locacao" ? "Aluguel" : "Venda";

    // Criar estrutura HTML do card
    card.innerHTML = `
      <div class="property-image">
        ${
          property.imagem
            ? `<img src="${property.imagem}" alt="${property.titulo}">`
            : '<i class="fas fa-home"></i>'
        }
      </div>
      <div class="property-info">
        <div class="property-title">${property.titulo || "Imóvel"}</div>
        <div class="property-price">${formatCurrency(property.preco)} ${
      property.finalidade === "locacao" ? "/mês" : ""
    }</div>
        <div><span class="property-status ${statusClass}">${
      property.status
    }</span> <span style="font-size: 0.8rem;">${finalidadeText}</span></div>
        <div class="property-meta">
          ${
            property.quartos !== undefined
              ? `
            <span><i class="fas fa-bed"></i> ${property.quartos} quarto${
                  property.quartos !== 1 ? "s" : ""
                }</span>
          `
              : ""
          }
          ${
            property.banheiros !== undefined
              ? `
            <span><i class="fas fa-bath"></i> ${property.banheiros} banheiro${
                  property.banheiros !== 1 ? "s" : ""
                }</span>
          `
              : ""
          }
        </div>
        <div class="property-ref">Ref: ${property.codigo_referencia}</div>
      </div>
    `;

    return card;
  }

  // Função para enviar mensagem para o chatbot
  async function sendMessage(message) {
    try {
      showTypingIndicator();

      const response = await fetch(CHATBOT_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ mensagem: message }),
      });

      if (!response.ok) {
        throw new Error(`Erro de servidor: ${response.status}`);
      }

      const data = await response.json();

      hideTypingIndicator();

      // Adicionar a resposta do bot
      addMessage(data.resposta, false);

      // Exibir os imóveis, se houver
      if (data.imoveis && data.imoveis.length > 0) {
        displayProperties(data.imoveis);
      }
    } catch (error) {
      console.error("Erro ao enviar mensagem:", error);
      hideTypingIndicator();
      addMessage(
        "Desculpe, tive um problema ao processar sua solicitação. Por favor, tente novamente mais tarde.",
        false
      );
    }
  }

  // Evento de envio do formulário
  chatForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const message = messageInput.value.trim();

    if (message) {
      // Adicionar a mensagem do usuário
      addMessage(message, true);

      // Enviar mensagem para o chatbot
      sendMessage(message);

      // Limpar o input
      messageInput.value = "";
    }
  });

  // Eventos para os chips de sugestão
  suggestionChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const message = chip.textContent.trim();

      // Simular o envio da mensagem como se fosse do usuário
      messageInput.value = message;
      chatForm.dispatchEvent(new Event("submit"));
    });
  });

  // Focar no input ao carregar a página
  messageInput.focus();
});
