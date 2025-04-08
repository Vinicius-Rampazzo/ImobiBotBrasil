document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const messageInput = document.getElementById("message-input");
  const chatMessages = document.getElementById("chat-messages");
  const typingIndicator = document.getElementById("typing-indicator");
  const suggestionChips = document.querySelectorAll(".suggestion-chip");
  const louisPlaceholder = document.getElementById("louis-placeholder");
  const propertiesGridContainer = document.getElementById(
    "properties-grid-container"
  );
  const propertiesTitleText = document.getElementById("properties-title-text");
  const louisMessage = document.querySelector(".louis-message");

  // Estado para controle de paginação
  let paginationState = {
    currentPage: 1,
    totalPages: 1,
    itemsPerPage: 10,
    totalItems: 0,
  };

  // NOVA SOLUÇÃO: Armazenar os filtros aplicados pelo chatbot
  let activeFilters = {
    tipo: null,
    finalidade: null,
    min_preco: null,
    max_preco: null,
    min_quartos: null,
    status: null // Importante: deve ser null inicialmente, não "disponivel"
  };

  // Indicador de consulta inicial vs. paginação
  let isFirstQuery = true;

  // URLs da API
  const CHATBOT_API_URL = "/api/chatbot";
  const IMOVEIS_BUSCAR_API_URL = "/api/imoveis/buscar";

  // Controle de estado da conversa usando sessionStorage
  const hasInteractedBefore =
    sessionStorage.getItem("louisHasInteracted") === "true";
  let isFirstInteraction = !hasInteractedBefore;

  // Mostrar o placeholder do Louis ao carregar a página
  showLouisPlaceholder();

  // Função para efeito de digitação
  function typeText(element, text, speed = 20, callback) {
    let index = 0;

    // Limpa o conteúdo atual
    element.innerHTML = "";

    // Adiciona um cursor
    const cursor = document.createElement("span");
    cursor.className = "typing-cursor";
    element.appendChild(cursor);

    // Função para adicionar um caractere por vez
    function typeCharacter() {
      if (index < text.length) {
        // Insere o texto antes do cursor
        const textNode = document.createTextNode(text.charAt(index));
        element.insertBefore(textNode, cursor);
        index++;
        setTimeout(typeCharacter, speed);
      } else {
        // Remove o cursor quando terminar
        setTimeout(() => {
          cursor.remove();
          if (callback) callback();
        }, 1000);
      }
    }

    // Inicia a digitação
    setTimeout(typeCharacter, 100);
  }

  if (louisMessage) {
    // Primeiro, mostra o balão vazio (sem o texto)
    const messageText = louisMessage.querySelector("p").textContent;
    louisMessage.querySelector("p").textContent = "";

    // Inicia o efeito de digitação após o balão aparecer
    setTimeout(() => {
      typeText(louisMessage.querySelector("p"), messageText, 35);
    }, 100);
  }

  // ===== FUNÇÕES PRINCIPAIS =====

  // Função para enviar mensagem para o chatbot
  async function sendMessage(message) {
    try {
      showTypingIndicator();

      console.log("É primeira interação?", isFirstInteraction); // Debug

      const response = await fetch(CHATBOT_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mensagem: message,
          isFirstInteraction: isFirstInteraction,
        }),
      });

      if (!response.ok) {
        throw new Error(`Erro de servidor: ${response.status}`);
      }

      const data = await response.json();
      hideTypingIndicator();

      // Adicionar a resposta do bot
      addMessage(data.resposta, false);

      // Registrar que o Louis já interagiu pelo menos uma vez
      if (isFirstInteraction) {
        sessionStorage.setItem("louisHasInteracted", "true");
        isFirstInteraction = false;
        console.log(
          "Primeira interação concluída, próximas serão respondidas diretamente"
        );
      }

      // Exibir os imóveis, se houver
      if (data.imoveis && data.imoveis.length > 0) {
        // Estamos em uma nova consulta
        isFirstQuery = true;
        
        // Verificar se há informações de paginação
        displayProperties(data.imoveis, data.paginacao, true);
        
        // IMPORTANTE: Resetar e extrair os novos filtros
        resetFilters(); // Limpa filtros anteriores
        
        // Se o servidor incluir os filtros usados, ótimo!
        if (data.filtros) {
          console.log("Filtros recebidos do servidor:", data.filtros);
          // Atualiza os filtros ativos
          Object.keys(data.filtros).forEach(key => {
            if (activeFilters.hasOwnProperty(key)) {
              activeFilters[key] = data.filtros[key];
            }
          });
        } else {
          // Tentar extrair filtros do texto da consulta (abordagem simplificada)
          const lowerMessage = message.toLowerCase();
          
          // Detecção de tipo de imóvel
          if (lowerMessage.includes("apartamento")) {
            activeFilters.tipo = "apartamento";
          } else if (lowerMessage.includes("casa")) {
            activeFilters.tipo = "casa";
          }
          
          // Detecção de finalidade
          if (lowerMessage.includes("aluguel") || lowerMessage.includes("alugar")) {
            activeFilters.finalidade = "locacao";
          } else if (lowerMessage.includes("comprar") || lowerMessage.includes("venda")) {
            activeFilters.finalidade = "venda";
          }
          
          // IMPORTANTE: NÃO defina o status como "disponivel" automaticamente
          // Observe o status atual dos imóveis retornados para determinar o filtro
          if (detectFilterFromResults(data.imoveis)) {
            console.log("Filtro de status detectado a partir dos resultados");
          }
        }
        
        console.log("Filtros ativos após processamento:", activeFilters);
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
  
  // Nova função para detectar filtros a partir dos resultados retornados
  function detectFilterFromResults(imoveis) {
    if (!imoveis || imoveis.length === 0) return false;
    
    // Verifica se todos os imóveis têm o mesmo status
    const allSameStatus = imoveis.every(imovel => imovel.status === imoveis[0].status);
    
    if (allSameStatus) {
      // Se todos têm o mesmo status, definimos esse como o filtro
      activeFilters.status = imoveis[0].status;
      return true;
    } else {
      // Se há mistura de status, significa que não há filtro de status
      activeFilters.status = null;
      return false;
    }
  }

  // Função para resetar filtros
  function resetFilters() {
    Object.keys(activeFilters).forEach(key => {
      activeFilters[key] = null;
    });
  }

  // Função para adicionar mensagem ao chat
  function addMessage(content, isUser = false) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${isUser ? "user" : "bot"}`;

    // Avatar
    const avatarDiv = document.createElement("div");
    avatarDiv.className = "avatar";

    if (isUser) {
      // Para o usuário, mantém o ícone
      const avatarIcon = document.createElement("i");
      avatarIcon.className = "fas fa-user";
      avatarDiv.appendChild(avatarIcon);
    } else {
      // Para o Louis, usa a imagem personalizada
      const avatarImg = document.createElement("img");
      avatarImg.src = "./assets/images/louis-chatbot.png";
      avatarImg.alt = "Louis - Chatbot";
      avatarDiv.appendChild(avatarImg);
    }

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

  // Função para exibir os imóveis
  function displayProperties(
    properties,
    paginationInfo = null,
    updateChat = true
  ) {
    console.log("Exibindo propriedades:", properties.length);
    console.log("Informações de paginação:", paginationInfo);

    if (!properties || properties.length === 0) {
      // Se não houver imóveis, mostra o placeholder do Louis
      if (propertiesTitleText.textContent !== "Converse com Louis") {
        animateTitleChange("Converse com Louis");
      }
      showLouisPlaceholder();
      return;
    }

    // Atualizar o estado da paginação se as informações forem fornecidas
    if (paginationInfo) {
      paginationState = {
        currentPage: paginationInfo.pagina_atual,
        totalPages: paginationInfo.total_paginas,
        itemsPerPage: paginationInfo.itens_por_pagina,
        totalItems: paginationInfo.total_imoveis,
      };
      console.log("Estado de paginação atualizado:", paginationState);
    }

    // Se houver imóveis, esconde o placeholder e mostra os imóveis
    if (propertiesTitleText.textContent !== "Imóveis Encontrados") {
      animateTitleChange("Imóveis Encontrados");
    }

    // Limpar o container de imóveis
    propertiesGridContainer.innerHTML = "";

    // Adicionar contador de resultados
    const totalCount = document.createElement("div");
    totalCount.className = "properties-count";
    totalCount.textContent = `${paginationState.totalItems} imóveis encontrados (Página ${paginationState.currentPage} de ${paginationState.totalPages})`;
    propertiesGridContainer.appendChild(totalCount);

    // Criar grid de propriedades
    const propertiesGrid = document.createElement("div");
    propertiesGrid.className = "properties-grid";

    properties.forEach((property) => {
      const card = createPropertyCard(property);
      propertiesGrid.appendChild(card);
    });

    propertiesGridContainer.appendChild(propertiesGrid);

    // Adicionar controles de paginação se houver mais de uma página
    if (paginationState.totalPages > 1) {
      const paginationControls = createPaginationControls();
      propertiesGridContainer.appendChild(paginationControls);
    }

    // Esconder o placeholder do Louis e mostrar os imóveis apenas se for uma nova consulta
    if (updateChat) {
      hideLouisPlaceholder();
    } else if (louisPlaceholder.classList.contains("active")) {
      // Se o placeholder do Louis estiver ativo, escondemos mesmo na navegação
      hideLouisPlaceholder();
    }

    // Garantir que o grid de imóveis esteja visível
    propertiesGridContainer.classList.remove("hidden");
    propertiesGridContainer.classList.add("active");
  }

  // Função para criar controles de paginação
  function createPaginationControls() {
    console.log("Criando controles de paginação");

    const paginationContainer = document.createElement("div");
    paginationContainer.className = "pagination-container";

    // Informações sobre a paginação
    const paginationInfo = document.createElement("div");
    paginationInfo.className = "pagination-info";
    paginationInfo.textContent = `Página ${paginationState.currentPage} de ${paginationState.totalPages}`;
    paginationContainer.appendChild(paginationInfo);

    // Botões de paginação
    const paginationButtons = document.createElement("div");
    paginationButtons.className = "pagination-buttons";

    // Botão Primeira Página
    const firstButton = document.createElement("button");
    firstButton.className = "pagination-button";
    firstButton.innerHTML = '<i class="fas fa-angle-double-left"></i>';
    firstButton.title = "Primeira página";
    firstButton.disabled = paginationState.currentPage <= 1;
    firstButton.addEventListener("click", () => {
      if (paginationState.currentPage > 1) {
        fetchProperties(1);
      }
    });
    paginationButtons.appendChild(firstButton);

    // Botão Anterior
    const prevButton = document.createElement("button");
    prevButton.className = "pagination-button";
    prevButton.innerHTML = '<i class="fas fa-angle-left"></i>';
    prevButton.title = "Página anterior";
    prevButton.disabled = paginationState.currentPage <= 1;
    prevButton.addEventListener("click", () => {
      if (paginationState.currentPage > 1) {
        fetchProperties(paginationState.currentPage - 1);
      }
    });
    paginationButtons.appendChild(prevButton);

    // Números de páginas
    const createPageButton = (pageNum) => {
      const pageButton = document.createElement("button");
      pageButton.className = "pagination-button page-number";
      if (pageNum === paginationState.currentPage) {
        pageButton.classList.add("active");
      }
      pageButton.textContent = pageNum;
      pageButton.addEventListener("click", () => {
        if (pageNum !== paginationState.currentPage) {
          fetchProperties(pageNum);
        }
      });
      return pageButton;
    };

    // Lógica para mostrar os números de página
    const maxPageButtons = 3; // Máximo de botões numéricos a mostrar
    let startPage = Math.max(
      1,
      paginationState.currentPage - Math.floor(maxPageButtons / 2)
    );
    let endPage = Math.min(
      paginationState.totalPages,
      startPage + maxPageButtons - 1
    );

    // Ajusta o início se não tiver suficientes páginas no final
    if (endPage - startPage + 1 < maxPageButtons) {
      startPage = Math.max(1, endPage - maxPageButtons + 1);
    }

    // Adiciona botões de página
    for (let i = startPage; i <= endPage; i++) {
      paginationButtons.appendChild(createPageButton(i));
    }

    // Botão Próximo
    const nextButton = document.createElement("button");
    nextButton.className = "pagination-button";
    nextButton.innerHTML = '<i class="fas fa-angle-right"></i>';
    nextButton.title = "Próxima página";
    nextButton.disabled =
      paginationState.currentPage >= paginationState.totalPages;
    nextButton.addEventListener("click", () => {
      if (paginationState.currentPage < paginationState.totalPages) {
        fetchProperties(paginationState.currentPage + 1);
      }
    });
    paginationButtons.appendChild(nextButton);

    // Botão Última Página
    const lastButton = document.createElement("button");
    lastButton.className = "pagination-button";
    lastButton.innerHTML = '<i class="fas fa-angle-double-right"></i>';
    lastButton.title = "Última página";
    lastButton.disabled =
      paginationState.currentPage >= paginationState.totalPages;
    lastButton.addEventListener("click", () => {
      if (paginationState.currentPage < paginationState.totalPages) {
        fetchProperties(paginationState.totalPages);
      }
    });
    paginationButtons.appendChild(lastButton);

    paginationContainer.appendChild(paginationButtons);

    return paginationContainer;
  }

  // Função para buscar imóveis em uma página específica - FUNÇÃO CORREÇÃO FINAL
  function fetchProperties(page = 1) {
    console.log("DEPURAÇÃO: Requisitando página", page);
    
    // Não é mais a primeira consulta quando estamos navegando
    isFirstQuery = false;

    // Mostra indicador de carregamento somente na seção de imóveis
    const loadingIndicator = document.createElement("div");
    loadingIndicator.className = "loading-indicator";
    loadingIndicator.innerHTML =
      '<i class="fas fa-spinner fa-spin"></i> Carregando imóveis (página ' + page + ')...';

    // Limpa somente o container de imóveis
    propertiesGridContainer.innerHTML = "";
    propertiesGridContainer.appendChild(loadingIndicator);

    // Esta é a chave da correção: usar a API de busca com os filtros corretos
    // Criar objeto de parâmetros para a URL
    const params = new URLSearchParams();
    params.append('pagina', page);
    params.append('itens_por_pagina', paginationState.itemsPerPage);
    
    // CORREÇÃO: preservar exatamente os mesmos filtros entre páginas
    // Adicionar os filtros ativos à query
    Object.keys(activeFilters).forEach(key => {
      if (activeFilters[key] !== null) {
        params.append(key, activeFilters[key]);
      }
    });
    
    // Usar a API de busca que suporta múltiplos filtros
    const filteredUrl = `${IMOVEIS_BUSCAR_API_URL}?${params.toString()}`;
    
    console.log("DEPURAÇÃO - URL de busca com filtros:", filteredUrl);
    console.log("DEPURAÇÃO - Parâmetros:", Object.fromEntries(params.entries()));

    fetch(filteredUrl)
      .then((response) => {
        console.log("DEPURAÇÃO - Status da resposta:", response.status);
        if (!response.ok) {
          throw new Error("Erro ao buscar imóveis: " + response.statusText);
        }
        return response.json();
      })
      .then((data) => {
        console.log("DEPURAÇÃO - Dados recebidos:", data);
        console.log("DEPURAÇÃO - Página atual recebida:", data.paginacao ? data.paginacao.pagina_atual : "N/A");
        console.log("DEPURAÇÃO - Quantidade de imóveis recebidos:", data.imoveis ? data.imoveis.length : 0);
        
        // Se for navegação de página, vamos verificar se os resultados parecem consistentes
        if (!isFirstQuery && data.imoveis) {
          // Verificar se há consistência entre os resultados da navegação
          const allSameStatus = data.imoveis.every(
            imovel => activeFilters.status === null || imovel.status === activeFilters.status
          );
          
          console.log("DEPURAÇÃO - Todos imóveis têm status consistente?", allSameStatus);
          
          if (!allSameStatus) {
            console.warn("ATENÇÃO: Os imóveis recebidos não têm o mesmo status do filtro ativo!");
          }
        }

        // Exibe os imóveis com a paginação
        if (data.imoveis && data.paginacao) {
          // false como terceiro parâmetro para não afetar o chat
          displayProperties(data.imoveis, data.paginacao, false);
        } else {
          console.error("Formato de dados inválido:", data);
          propertiesGridContainer.innerHTML = `
            <div class="error-message">
              <i class="fas fa-exclamation-triangle"></i>
              <p>Formato de dados inválido recebido do servidor.</p>
            </div>
          `;
        }
      })
      .catch((error) => {
        console.error("Erro ao buscar propriedades:", error);
        
        // Mostrar mensagem de erro para o usuário
        propertiesGridContainer.innerHTML = `
          <div class="error-message">
            <i class="fas fa-exclamation-triangle"></i>
            <p>Ocorreu um erro ao buscar os imóveis: ${error.message}</p>
          </div>
        `;
      });
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
            ? `<img src="${property.imagem}" alt="${property.titulo}" onerror="this.onerror=null; this.src='./assets/images/placeholder-property.jpg';">`
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

  // ===== FUNÇÕES DE SUPORTE =====

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

  // ===== EVENT LISTENERS =====

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

  // Adicionamos logs para depuração
  console.log("Script inicializado com sucesso - VERSÃO CORRIGIDA FINAL");
});