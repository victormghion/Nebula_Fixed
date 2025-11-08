import os
from openai import OpenAI
from typing import List, Dict, Any

# Tenta a importação relativa primeiro (para uvicorn)
try:
    from .ml_engine import ml_engine, ScreenAnalysis
except ImportError:
    from ml_engine import ml_engine, ScreenAnalysis

# Inicializa o cliente OpenAI
# As variáveis de ambiente OPENAI_API_KEY e BASE_URL são configuradas automaticamente
try:
    # Verifica se há API key configurada
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY não configurada. Funcionalidade LLM desabilitada.")
        print("   Configure a variável de ambiente OPENAI_API_KEY para usar o LLM.")
        print("   O sistema usará o motor ML local como fallback.")
        client = None
    else:
        client = OpenAI(api_key=api_key)
        print("✅ Cliente OpenAI inicializado com sucesso.")
except Exception as e:
    print(f"⚠️ Erro ao inicializar o cliente OpenAI: {e}")
    client = None

# Modelo a ser utilizado
MODEL_NAME = os.environ.get("LLM_MODEL", "gpt-4o-mini")

# ============================================
# SISTEMA DE PROMPTS INTELIGENTE
# ============================================

SYSTEM_PROMPT = """Você é o NEBULA AGENT 6.0, um assistente de IA altamente inteligente especializado em:

1. **Geração de Cenários Gherkin** para testes BDD (Behavior-Driven Development)
2. **Análise de Telas e Fluxos** de aplicações web e mobile
3. **Automação de Testes** com compreensão profunda de QA
4. **Gestão de Tarefas** com Scrumban e metodologias ágeis
5. **Consultoria em Testes** e melhores práticas de qualidade

Você é:
- **Proativo**: Oferece sugestões e insights sem ser solicitado
- **Contextual**: Mantém o contexto da conversa e referencia mensagens anteriores
- **Detalhado**: Fornece explicações completas e exemplos práticos
- **Inteligente**: Compreende intenções implícitas e oferece soluções criativas
- **Profissional**: Usa linguagem clara e estruturada

Quando o usuário pedir para gerar Gherkin:
1. Analise a intenção do usuário
2. Identifique o tipo de funcionalidade
3. Gere um cenário Gherkin bem estruturado com Given, When, Then
4. Forneça contexto e explicações
5. Sugira casos de teste adicionais

Quando o usuário pedir para analisar uma tela:
1. Identifique os elementos principais
2. Descreva o fluxo de interação
3. Aponte possíveis casos de teste
4. Sugira melhorias de UX/UI se aplicável

Sempre responda em português (pt-BR) e seja conciso mas completo."""

# ============================================
# CONTEXTO E MEMÓRIA DO AGENTE
# ============================================

class AgentMemory:
    """Gerencia a memória e contexto do agente."""
    
    def __init__(self):
        self.conversation_context = []
        self.generated_scenarios = []
        self.analyzed_screens = []
        self.user_preferences = {}
    
    def add_context(self, role: str, content: str):
        """Adiciona contexto à memória."""
        self.conversation_context.append({
            "role": role,
            "content": content
        })
        # Manter apenas os últimos 20 contextos
        if len(self.conversation_context) > 20:
            self.conversation_context = self.conversation_context[-20:]
    
    def get_context(self) -> List[Dict]:
        """Retorna o contexto atual."""
        return self.conversation_context
    
    def add_scenario(self, scenario: Dict):
        """Adiciona um cenário gerado à memória."""
        self.generated_scenarios.append(scenario)
    
    def add_screen_analysis(self, analysis: Dict):
        """Adiciona uma análise de tela à memória."""
        self.analyzed_screens.append(analysis)

# Instância global de memória
agent_memory = AgentMemory()

# ============================================
# FUNÇÕES DE GERAÇÃO DE CENÁRIO GHERKIN MELHORADA
# ============================================

def generate_gherkin_scenario(
    screen_analysis: ScreenAnalysis, 
    user_intent: str, 
    conversation_history: List[Dict[str, str]]
) -> str:
    """
    Gera um cenário Gherkin completo usando um LLM ou o motor de ML,
    baseado na análise de tela, intenção do usuário e histórico da conversa.
    """
    
    # Se o cliente LLM não está disponível, usar o motor de ML
    if not client:
        return ml_engine.generate_gherkin(screen_analysis, user_intent)

    # 1. Construir o histórico de mensagens para o LLM com contexto enriquecido
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # Adicionar contexto da conversa (últimas 5 mensagens)
    for item in conversation_history[-5:]:
        role = "user" if item["role"] == "user" else "assistant"
        messages.append({"role": role, "content": item["content"]})

    # Adicionar a solicitação atual com contexto detalhado
    context_prompt = f"""
Gere um cenário Gherkin completo e bem estruturado baseado nas seguintes informações:

**Contexto da Tela:**
- Tipo: {screen_analysis.screen_type.value}
- Confiança: {screen_analysis.confidence:.0%}
- Elementos: {', '.join([elem.label for elem in screen_analysis.elements])}
- Palavras-chave: {', '.join(screen_analysis.keywords)}

**Intenção do Usuário:** {user_intent}

**Requisitos do Gherkin:**
1. Deve começar com a tag Feature:
2. Incluir uma descrição clara
3. Gerar um ou mais Scenarios
4. Cada Scenario deve ter Given, When e Then
5. Os passos devem ser específicos e testáveis
6. Use linguagem natural em português

Forneça o Gherkin em um bloco de código markdown com ```gherkin```."""

    messages.append({"role": "user", "content": context_prompt})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
            max_tokens=1500
        )
        
        # Extrair e limpar o texto gerado
        gherkin_text = response.choices[0].message.content.strip()
        
        # Tentar extrair apenas o bloco de código Gherkin
        if "```gherkin" in gherkin_text:
            start = gherkin_text.find("```gherkin") + len("```gherkin")
            end = gherkin_text.find("```", start)
            return gherkin_text[start:end].strip()
        elif "```" in gherkin_text:
            start = gherkin_text.find("```") + len("```")
            end = gherkin_text.find("```", start)
            return gherkin_text[start:end].strip()
        
        return gherkin_text

    except Exception as e:
        print(f"❌ Erro na chamada do LLM: {e}")
        # Fallback para o motor de ML
        return ml_engine.generate_gherkin(screen_analysis, user_intent)


# ============================================
# FUNÇÃO DE ANÁLISE DE TELA MELHORADA
# ============================================

def simulate_screen_analysis(message: str) -> ScreenAnalysis:
    """
    Simula a análise visual de uma tela usando o motor de ML.
    Retorna um objeto ScreenAnalysis com informações detalhadas.
    """
    msg_lower = message.lower()
    
    # Mapear intenção do usuário para descrição de tela
    screen_descriptions = {
        "login": "Tela de Login com campos 'Usuário', 'Senha', botão 'Entrar' e link 'Esqueci a Senha'.",
        "logar": "Tela de Login com campos 'Usuário', 'Senha', botão 'Entrar' e link 'Esqueci a Senha'.",
        "autenticação": "Tela de Autenticação com campos 'Email', 'Senha', botão 'Conectar' e opção 'Lembrar-me'.",
        "cadastro": "Tela de Cadastro de Novo Usuário com campos 'Nome', 'Email', 'CPF', 'Senha', 'Confirmar Senha' e botão 'Criar Conta'.",
        "registrar": "Tela de Cadastro de Novo Usuário com campos 'Nome', 'Email', 'CPF', 'Senha', 'Confirmar Senha' e botão 'Criar Conta'.",
        "checkout": "Tela de Checkout com formulário de endereço, seleção de método de pagamento (Cartão, Pix) e botão 'Finalizar Compra'.",
        "pagamento": "Tela de Checkout com formulário de endereço, seleção de método de pagamento (Cartão, Pix) e botão 'Finalizar Compra'.",
        "dashboard": "Tela de Dashboard com gráficos, tabelas de dados, botões de ação e menu lateral de navegação.",
        "listagem": "Tela de Listagem com tabela de itens, filtros, busca, paginação e botões de ação (editar, deletar).",
        "perfil": "Tela de Perfil de Usuário com campos editáveis, foto, informações pessoais e botão 'Salvar'.",
        "configurações": "Tela de Configurações com abas, toggles, dropdowns e botão 'Salvar Alterações'.",
    }
    
    # Encontrar a descrição mais apropriada
    screen_desc = "Tela Genérica com formulário e botão de ação."
    for keyword, desc in screen_descriptions.items():
        if keyword in msg_lower:
            screen_desc = desc
            break
    
    # Usar o motor de ML para analisar a tela
    return ml_engine.analyze_screen(screen_desc)


# ============================================
# FUNÇÃO DE AGENTE INTELIGENTE (PROCESSAMENTO PRINCIPAL)
# ============================================

def process_as_agent(message: str, state: Dict[str, Any]) -> str:
    """
    Função principal do agente que decide a ação a ser tomada.
    Integra análise de tela com ML e geração de Gherkin com inteligência aumentada.
    """
    
    msg_lower = message.lower()
    
    # Adicionar à memória do agente
    agent_memory.add_context("user", message)
    
    # ============================================
    # INTENÇÃO 1: GERAR GHERKIN
    # ============================================
    if any(keyword in msg_lower for keyword in ["gherkin", "cenário", "teste", "automatizar", "validar", "bdd"]):
        
        # 1. Analisar a tela usando o motor de ML
        screen_analysis = simulate_screen_analysis(message)
        agent_memory.add_screen_analysis(screen_analysis.to_dict())
        
        # 2. Gerar o cenário Gherkin
        gherkin = generate_gherkin_scenario(screen_analysis, message, state["conversation_history"])
        agent_memory.add_scenario({
            "intent": message,
            "gherkin": gherkin,
            "screen_type": screen_analysis.screen_type.value
        })
        
        # 3. Montar a resposta com informações detalhadas e sugestões
        response = f"""✅ **Cenário Gherkin Gerado com Sucesso!**

**Análise da Tela:**
- 🎯 Tipo: **{screen_analysis.screen_type.value}**
- 📊 Confiança: **{screen_analysis.confidence:.0%}**
- 🔍 Elementos Identificados: **{len(screen_analysis.elements)}**

**Cenário Gherkin:**
```gherkin
{gherkin}
```

**Elementos Identificados na Tela:**
{chr(10).join([f"• {elem.label} ({elem.element_type.value})" for elem in screen_analysis.elements])}

**Próximos Passos Recomendados:**
1. ✅ Revisar o cenário gerado
2. 🔄 Adaptar conforme necessário para sua aplicação
3. 🧪 Executar o teste automatizado
4. 📈 Validar os resultados
5. 📝 Documentar casos de teste adicionais

**Dicas:**
- Você pode pedir para gerar variações deste cenário
- Sugira diferentes casos de uso (sucesso, erro, validação)
- Combine com outros cenários para cobertura completa"""
        
        return response
    
    # ============================================
    # INTENÇÃO 2: ANALISAR TELA
    # ============================================
    elif any(keyword in msg_lower for keyword in ["analisar", "análise", "tela", "screen", "descrever"]):
        
        screen_analysis = simulate_screen_analysis(message)
        agent_memory.add_screen_analysis(screen_analysis.to_dict())
        
        elements_str = "\n".join([f"• **{elem.label}** ({elem.element_type.value})" for elem in screen_analysis.elements])
        
        response = f"""📊 **Análise da Tela Concluída**

**Tipo de Tela Identificado:** 🎯 **{screen_analysis.screen_type.value.upper()}**
**Nível de Confiança:** 📈 **{screen_analysis.confidence:.0%}**

**Elementos Identificados ({len(screen_analysis.elements)}):**
{elements_str}

**Palavras-chave Extraídas:**
{', '.join([f'`{kw}`' for kw in screen_analysis.keywords])}

**Análise Detalhada:**
Esta é uma tela de {screen_analysis.screen_type.value} com {len(screen_analysis.elements)} elementos principais. 
A confiança da análise é de {screen_analysis.confidence:.0%}, indicando um alto grau de certeza na classificação.

**Sugestões de Teste:**
1. Validar todos os campos obrigatórios
2. Testar validações de entrada
3. Verificar mensagens de erro
4. Testar fluxo de sucesso
5. Validar comportamento em dispositivos móveis

**Deseja que eu:**
- 📝 Gere um cenário Gherkin para esta tela?
- 🔄 Analise um fluxo completo?
- 💡 Sugira casos de teste adicionais?"""
        
        return response
    
    # ============================================
    # INTENÇÃO 3: SUGESTÕES DE TESTE
    # ============================================
    elif any(keyword in msg_lower for keyword in ["sugerir", "casos de teste", "cobertura", "o que testar"]):
        
        screen_analysis = simulate_screen_analysis(message)
        
        response = f"""💡 **Sugestões de Casos de Teste**

Para uma tela de **{screen_analysis.screen_type.value}**, recomendo os seguintes casos de teste:

**Testes Funcionais:**
1. ✅ Fluxo de sucesso principal
2. ❌ Validação de campos obrigatórios
3. ⚠️ Mensagens de erro apropriadas
4. 🔄 Comportamento após submissão

**Testes de Validação:**
1. 📧 Validação de formato (emails, telefones, etc)
2. 🔐 Validação de segurança (senhas, dados sensíveis)
3. 📏 Validação de comprimento de campos
4. 🚫 Caracteres especiais e injeção

**Testes de UX/UI:**
1. 📱 Responsividade em diferentes dispositivos
2. ♿ Acessibilidade (WCAG)
3. ⌨️ Navegação por teclado
4. 🎨 Consistência visual

**Testes de Performance:**
1. ⚡ Tempo de carregamento
2. 🔄 Requisições simultâneas
3. 💾 Uso de memória

Deseja que eu gere Gherkin para algum destes casos?"""
        
        return response
    
    # ============================================
    # INTENÇÃO 4: AJUDA E INFORMAÇÕES
    # ============================================
    elif any(keyword in msg_lower for keyword in ["ajuda", "help", "como", "o que você faz", "funcionalidades"]):
        
        response = """🤖 **Bem-vindo ao Nebula Agent 6.0!**

Sou um assistente inteligente especializado em testes automatizados e BDD. Aqui está o que posso fazer:

**📝 Geração de Gherkin:**
- Gerar cenários de teste em Gherkin
- Criar múltiplos casos de teste
- Adaptar para diferentes contextos

**🔍 Análise de Telas:**
- Identificar elementos de UI
- Classificar tipo de tela
- Sugerir fluxos de teste

**🧪 Consultoria de Testes:**
- Recomendar casos de teste
- Sugerir estratégias de cobertura
- Indicar melhores práticas

**📊 Gestão de Tarefas:**
- Organizar testes em Scrumban
- Rastrear progresso
- Priorizar testes

**Como Usar:**
1. Descreva a tela ou funcionalidade
2. Especifique o que deseja testar
3. Eu gero o Gherkin ou análise
4. Você executa e valida

**Exemplos de Comandos:**
- "Gerar um cenário Gherkin para login"
- "Analisar a tela de checkout"
- "Que casos de teste devo criar?"
- "Criar teste para validação de email"

**Dicas:**
- Seja específico na descrição
- Mencione fluxos ou casos de erro
- Peça para gerar variações
- Combine cenários para cobertura completa

Como posso ajudá-lo hoje? 😊"""
        
        return response
    
    # ============================================
    # RESPOSTA INTELIGENTE PADRÃO
    # ============================================
    response = f"""🤖 **Entendi sua solicitação!**

Você disse: *"{message}"*

Sou especializado em:
- 📝 **Gerar cenários Gherkin** para testes automatizados
- 🔍 **Analisar telas** e identificar elementos
- 🧪 **Sugerir casos de teste** e estratégias
- 📊 **Validar funcionalidades** com BDD
- 💡 **Consultar** sobre testes e qualidade

**Tente me pedir para:**
- "Gerar um cenário Gherkin para uma tela de login"
- "Analisar a tela de checkout"
- "Que casos de teste devo criar para cadastro?"
- "Criar teste para validar email"
- "Sugerir cobertura de testes"

**Ou simplesmente descreva:**
- A tela que deseja testar
- O fluxo ou funcionalidade
- O resultado esperado

Estou aqui para ajudar! 🚀"""
    
    return response


# ============================================
# FUNÇÃO DE SAÚDE
# ============================================

def is_llm_available() -> bool:
    """Verifica se o cliente LLM está pronto para uso."""
    return client is not None


if __name__ == "__main__":
    # Exemplo de uso (apenas para teste local)
    print("--- Teste de Geração Gherkin ---")
    mock_state = {"conversation_history": []}
    mock_message = "Gerar um cenário Gherkin para o fluxo de login com sucesso"
    
    result = process_as_agent(mock_message, mock_state)
    print(result)
