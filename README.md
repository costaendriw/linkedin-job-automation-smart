# LinkedIn Job Automation - Smart Edition

Sistema avançado de automação para LinkedIn com **filtragem inteligente** baseada no seu perfil, usando **Playwright** para compatibilidade total com **Chrome 140+**.

## Características Principais

- **Filtragem Inteligente**: Aproveita as recomendações do próprio LinkedIn
- **Playwright Engine**: Funciona nativamente com Chrome 140+ sem ChromeDriver
- **Anti-Detecção Avançada**: Configurações específicas para evitar detecção
- **Interface Moderna**: GUI intuitiva com logs coloridos e controles avançados
- **Performance Superior**: 2x mais rápido que soluções baseadas em Selenium
- **Estabilidade Total**: Sem problemas de compatibilidade de versão

## Sistema de Filtragem Inteligente

### Estratégia Dupla:
1. **Prioridade**: Vagas recomendadas pelo LinkedIn ("Vagas que mais combinam com seu perfil")
2. **Backup**: Busca tradicional com filtros personalizados

### Filtros Baseados no Seu Perfil:
- Skills Matching: Analisa suas competências vs requisitos da vaga
- Nível de Experiência: Evita vagas sênior se você é júnior
- Termos Indesejados: Pula vagas com termos que você quer evitar
- Modalidade de Trabalho: Filtra por remoto, presencial ou híbrido
- Compatibilidade Score: Sistema de pontuação inteligente

## Requisitos

- Python 3.8 ou superior
- Chrome/Chromium instalado (qualquer versão moderna)
- Conta no LinkedIn

## Instalação

### 1. Clone o projeto

```bash
git clone <repository-url>
cd linkedin-automation-smart
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Instale os navegadores do Playwright

```bash
playwright install chromium
```

## Como Usar

### 1. Execute o programa

```bash
python main.py
```

### 2. Configure seu perfil

Na seção **"Configuração do Seu Perfil"**:
- **Suas Skills**: Liste suas competências (ex: Python, Data Science, SQL)
- **Evitar termos**: Termos que você quer evitar (ex: Senior, Lead, Manager)
- **Priorizar recomendações**: Deixe marcado para usar filtragem inteligente

### 3. Configure suas credenciais

- Digite seu e-mail e senha do LinkedIn
- Configure palavras-chave de busca (backup)
- Selecione localização e filtros desejados

### 4. Teste e execute

- Clique em **"Testar Navegador"** primeiro
- Clique em **"Iniciar Automação Smart"**
- Acompanhe o progresso nos logs coloridos

## Como Funciona

### Estratégia Principal - Recomendações do LinkedIn:
1. **Login** no LinkedIn
2. **Acessa** a página inicial com vagas recomendadas
3. **Analisa** cada vaga recomendada usando seus critérios
4. **Filtra** baseado em suas skills e termos a evitar
5. **Salva** apenas vagas compatíveis

### Critérios de Compatibilidade:
- Pelo menos 1 skill match (suas competências vs requisitos)
- Zero termos indesejados (evita cargos sêniores se você é júnior)
- Nível apropriado (baseado na sua configuração)
- Modalidade de trabalho (remoto, presencial, híbrido)

## Estrutura do Projeto

```
linkedin-automation-smart/
├── src/
│   ├── __init__.py              # Inicialização do pacote
│   ├── automation_fixed.py     # Engine principal com Playwright
│   ├── gui.py                   # Interface gráfica com filtragem
│   └── utils.py                 # Funções utilitárias
├── main.py                      # Arquivo principal
├── requirements.txt             # Dependências
├── .gitignore                   # Exclusões Git
└── README.md                    # Esta documentação
```

## Configurações Avançadas

### Interface Otimizada:
- **Logs Coloridos**: Verde (sucesso), vermelho (erro), roxo (compatibilidade)
- **Controles de Log**: Limpar, salvar, auto-scroll
- **Scrollbar Inteligente**: Interface sempre acessível

### Modo Headless:
- Marque "Modo invisível" para execução mais rápida
- Recomendado para uso em segundo plano

## Exemplos de Configuração

### Para Desenvolvedor Júnior:
```
Suas Skills: Python, JavaScript, React, SQL, Git
Evitar termos: Senior, Lead, Manager, Diretor, Especialista
Nível: Júnior
Modalidade: Remoto
```

### Para Cientista de Dados:
```
Suas Skills: Python, Data Science, Machine Learning, SQL, Pandas
Evitar termos: Senior, Lead, Principal
Nível: Pleno
Modalidade: Híbrido
```

## Resolução de Problemas

### Erro de instalação do tkinter:
Se receber erro sobre tkinter, ignore-o. O tkinter já vem incluído no Python padrão.

### Problemas do Playwright:
```bash
# Se falhar, tente:
python -m playwright install chromium

# Ou instale manualmente:
pip install playwright --upgrade
python -m playwright install
```

### Problemas de Login:
1. Verifique suas credenciais
2. Complete verificações de segurança manualmente
3. Use autenticação de dois fatores se necessário

### Vagas Não Compatíveis:
1. Revise suas skills na configuração
2. Ajuste os termos a evitar
3. Verifique se as recomendações estão ativadas

## Considerações Éticas

Este projeto é para fins **educacionais e de automação pessoal**. Use com responsabilidade:

- Respeite os termos de serviço do LinkedIn
- Não abuse da automação (use delays adequados)
- Mantenha suas credenciais seguras
- Use para otimizar SUA busca de emprego

## Teste de Funcionamento

1. Use o botão **"Testar Navegador"** para verificar se o Playwright está funcionando
2. Verifique se aparecem logs coloridos indicando sucesso
3. Confirme que o navegador abre corretamente

## Logs e Debug

Os logs mostram em tempo real:
- **Azul**: Informações gerais
- **Verde**: Sucessos e vagas salvas
- **Roxo**: Análises de compatibilidade
- **Vermelho**: Erros
- **Laranja**: Avisos

## Resultados Esperados

Com esta ferramenta você pode:
- Encontrar vagas altamente compatíveis com seu perfil
- Economizar tempo significativo na busca manual
- Salvar 10-30 vagas relevantes por execução
- Evitar automaticamente vagas inadequadas
- Focar apenas em oportunidades reais

---

**Desenvolvido com Playwright e inteligência baseada no seu perfil LinkedIn.**

## 📂 Estrutura do Projeto

```
linkedin-automation-playwright/
├── src/
│   ├── __init__.py
│   ├── automation_fixed.py    # Engine principal com Playwright
│   ├── gui.py                 # Interface gráfica
│   └── utils.py               # Funções utilitárias
├── main.py                    # Arquivo principal
├── requirements.txt           # Dependências
└── README.md                  # Esta documentação
```

## ⚙️ Configurações Avançadas

### Modo Headless
- Marque "Modo invisível (headless)" para execução mais rápida sem janela do navegador
- Recomendado para execuções em servidor ou background

### Anti-Detecção
- Deixe "Anti-detecção avançada" marcado para melhor stealth
- Remove indicadores de automação do navegador

### Filtros de Busca

#### Níveis de Experiência:
- Estágio
- Júnior 
- Pleno
- Sênior
- Diretor
- Executivo

#### Modalidades de Trabalho:
- Remoto
- Presencial
- Híbrido

#### Tipos de Contrato:
- CLT
- PJ
- Temporário
- Freelancer
- Estágio
- Trainee

## 🔍 Funcionalidades

### Principais Features:
- ✅ Login automático no LinkedIn
- ✅ Busca inteligente por palavras-chave
- ✅ Aplicação automática de filtros
- ✅ Salvamento de vagas em massa
- ✅ Navegação entre páginas de resultados
- ✅ Logs detalhados em tempo real
- ✅ Sistema de pausa/retomada

### Recursos de Segurança:
- 🔒 Delays aleatórios entre ações
- 🔒 Simulação de comportamento humano
- 🔒 User-Agent dinâmico
- 🔒 Anti-fingerprinting
- 🔒 Rotação de cabeçalhos HTTP

## 🐛 Resolução de Problemas

### Erro comum de instalação:

Se você receber o erro `ERROR: No matching distribution found for tkinter`, ignore-o. O tkinter já vem incluído no Python padrão e não precisa ser instalado via pip.

### Problemas de instalação do Playwright:

```bash
# Se "playwright install" falhar, tente:
python -m playwright install chromium

# Ou instale manualmente:
pip install playwright --upgrade
python -m playwright install
```

### Problemas de Login
1. Verifique suas credenciais
2. Complete verificações de segurança manualmente
3. Use autenticação de dois fatores se necessário

### Performance Lenta
1. Ative o modo headless
2. Reduza o delay entre ações
3. Limite o número de vagas

## 📊 Comparação: Playwright vs Selenium

| Recurso | Playwright | Selenium |
|---------|------------|----------|
| Compatibilidade Chrome 140+ | ✅ Nativa | ❌ Precisa ChromeDriver |
| Velocidade | ✅ Muito rápido | ⚠️ Médio |
| Anti-detecção | ✅ Avançada | ⚠️ Básica |
| Configuração | ✅ Automática | ❌ Manual |
| Estabilidade | ✅ Alta | ⚠️ Média |
| Manutenção | ✅ Baixa | ❌ Alta |

## 🔒 Considerações Éticas

Este projeto é para fins **educacionais e de automação pessoal**. Use com responsabilidade:

- ⚠️ Respeite os termos de serviço do LinkedIn
- ⚠️ Não abuse da automação (use delays adequados)
- ⚠️ Mantenha suas credenciais seguras
- ⚠️ Use para otimizar SUA busca de emprego

## 🆘 Teste de Funcionamento

Use o botão "Testar Navegador" na interface para verificar se o Playwright está funcionando corretamente.

## 📝 Logs e Debug

Os logs mostram em tempo real:
- Status da conexão
- Ações executadas
- Vagas encontradas e salvas
- Erros e soluções

## 🔄 Atualizações Futuras

Roadmap de melhorias:
- [ ] Suporte a múltiplos navegadores
- [ ] Sistema de relatórios
- [ ] Integração com APIs de emprego
- [ ] Dashboard web
- [ ] Notificações por email

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs na interface
2. Teste o navegador com o botão de teste
3. Consulte a documentação do Playwright

## 🏆 Vantagens desta Versão

1. **Compatibilidade Total**: Funciona com qualquer versão moderna do Chrome
2. **Zero Configuração**: Não precisa baixar ou gerenciar drivers
3. **Performance Superior**: Playwright é mais rápido que Selenium
4. **Mais Confiável**: Menos falhas e timeouts
5. **Anti-Detecção**: Muito mais difícil de detectar como bot
6. **Futuro-Proof**: Sempre compatível com atualizações do Chrome

## 🎯 Resultados Esperados

Com esta ferramenta você pode:
- Salvar 20-100 vagas por execução
- Economizar horas de busca manual
- Aplicar filtros precisos automaticamente
- Manter histórico organizado de vagas

---

**Desenvolvido com Playwright para máxima compatibilidade e performance.**
