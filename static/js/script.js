// Espera o DOM carregar para começar a executar o script
document.addEventListener("DOMContentLoaded", () => {
  
  // Seleciona os elementos principais da interface
  const chatForm = document.getElementById("chatForm");
  const inputMsg = document.getElementById("inputMsg");
  const sendBtn = document.getElementById("sendBtn");
  const messagesContainer = document.getElementById("messages");
  const typingIndicator = document.getElementById("typing");
  const messageTemplate = document.getElementById("msg-template");
  const clearChatBtn = document.getElementById("clearLocal");
  const navButtons = document.querySelectorAll(".nav-btn");

  // Função para rolar o chat para a última mensagem
  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Função para criar e adicionar uma nova mensagem (seja do usuário ou do bot)
  function createMessage(text, sender) {
    // Clona o template de mensagem
    const templateClone = messageTemplate.content.cloneNode(true);
    const messageGroup = templateClone.querySelector(".message-group");
    const avatar = templateClone.querySelector(".avatar");
    const bubbleInner = templateClone.querySelector(".bubble-inner");

    // Define o conteúdo e o remetente
    bubbleInner.textContent = text;
    
    if (sender === "user") {
      messageGroup.classList.add("user");
      avatar.textContent = "U"; // Você pode mudar para a inicial do usuário
    } else {
      avatar.textContent = "N"; // 'N' de Nebula
    }

    // Adiciona a mensagem ao container e rola para baixo
    messagesContainer.appendChild(templateClone);
    scrollToBottom();
  }

  // (Função getBotResponse removida, pois não é mais necessária)

  // 
  // ESTA É A FUNÇÃO ATUALIZADA
  // 
  // Função principal para lidar com o envio de mensagens
  async function handleChatSubmit(event) {
    event.preventDefault(); // Impede o recarregamento da página
    
    const userText = inputMsg.value.trim();
    if (userText === "") return; // Não envia mensagens vazias

    // 
    // ⚠️ MUDE ESSA LINHA com a URL do seu backend do Render
    // 
    const backendUrl = 'https://seu-backend.onrender.com/api/chat';

    // 1. Adiciona a mensagem do usuário à interface
    createMessage(userText, "user");

    // 2. Limpa o campo de input
    inputMsg.value = "";

    // 3. Mostra o indicador "digitando"
    typingIndicator.style.display = "flex";
    scrollToBottom();

    // 4. Envia a mensagem para o seu backend
    try {
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userText }),
      });

      if (!response.ok) {
        throw new Error('Erro na resposta do servidor.');
      }

      const data = await response.json();
      const botText = data.reply;
      
      // 7. Adiciona a mensagem do bot à interface
      createMessage(botText, "bot");

    } catch (error) {
      console.error("Erro ao contatar o backend:", error);
      // 7b. Mostra uma mensagem de erro
      createMessage("Desculpe, não consegui me conectar ao meu cérebro. Tente novamente.", "bot");
    } finally {
      // 6. Esconde o indicador "digitando" (sempre)
      typingIndicator.style.display = "none";
    }
  }

  // --- Adiciona os Event Listeners ---

  // Envio do formulário (clique no botão ou Enter)
  chatForm.addEventListener("submit", handleChatSubmit);

  // Botão de limpar chat
  clearChatBtn.addEventListener("click", () => {
    messagesContainer.innerHTML = ""; // Limpa todas as mensagens
  });

  // Navegação (apenas alterna a classe 'active')
  navButtons.forEach(button => {
    button.addEventListener("click", () => {
      // Remove 'active' de todos os botões
      document.querySelector(".nav-btn.active")?.classList.remove("active");
      // Adiciona 'active' ao botão clicado
      button.classList.add("active");
      
      // (No futuro, você pode adicionar lógica aqui para mudar o view, 
      // por ex: mostrar/esconder o .chat-container vs .scrumban-container)
    });
  });

  // Adiciona uma mensagem inicial do bot
  setTimeout(() => {
     createMessage("Olá! Eu sou a Nebula. Como posso ajudar você hoje?", "bot");
  }, 500);

});