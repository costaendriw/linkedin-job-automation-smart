#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Funções auxiliares para a automação do LinkedIn com Playwright
Versão atualizada com suporte para filtragem inteligente
"""

import time
import random
import re
import asyncio

def random_delay(min_seconds=1, max_seconds=3):
    """
    Executa um delay aleatório entre min_seconds e max_seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

async def async_random_delay(min_seconds=1, max_seconds=3):
    """
    Versão assíncrona do delay aleatório
    """
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)

def get_random_delay_ms(min_ms=100, max_ms=500):
    """
    Retorna um delay aleatório em milissegundos para uso com Playwright
    """
    return random.randint(min_ms, max_ms)

async def safe_click(locator, max_attempts=3):
    """
    Clica em um elemento de forma segura com Playwright
    """
    for attempt in range(max_attempts):
        try:
            await locator.wait_for(state="visible", timeout=5000)
            await locator.click()
            return True
        except Exception as e:
            if attempt == max_attempts - 1:
                return False
            await asyncio.sleep(0.5)
    
    return False

async def safe_fill(locator, text, clear_first=True, typing_delay=50):
    """
    Preenche um campo de forma segura com Playwright
    """
    try:
        await locator.wait_for(state="visible", timeout=5000)
        
        if clear_first:
            await locator.fill("")
            await asyncio.sleep(0.1)
        
        await locator.type(text, delay=typing_delay)
        return True
        
    except Exception:
        try:
            await locator.fill(text)
            return True
        except:
            return False

async def extract_job_info(job_element):
    """
    Extrai informações relevantes de um elemento de vaga
    """
    try:
        job_info = {
            'title': '',
            'company': '',
            'location': '',
            'description': '',
            'full_text': ''
        }
        
        # Extrair texto completo
        full_text = await job_element.text_content()
        job_info['full_text'] = full_text.lower() if full_text else ''
        
        # Tentar extrair título da vaga
        title_selectors = [
            ".job-card-list__title",
            ".job-title",
            "h3",
            ".job-card__title"
        ]
        
        for selector in title_selectors:
            try:
                title_element = job_element.locator(selector).first
                if await title_element.is_visible():
                    job_info['title'] = await title_element.text_content()
                    break
            except:
                continue
        
        # Tentar extrair empresa
        company_selectors = [
            ".job-card-container__company-name",
            ".company-name",
            ".job-card__company-name"
        ]
        
        for selector in company_selectors:
            try:
                company_element = job_element.locator(selector).first
                if await company_element.is_visible():
                    job_info['company'] = await company_element.text_content()
                    break
            except:
                continue
        
        return job_info
        
    except Exception as e:
        return {'full_text': '', 'title': '', 'company': '', 'location': '', 'description': ''}

def analyze_job_compatibility(job_text, user_skills, avoid_terms, experience_level):
    """
    Analisa compatibilidade de uma vaga baseada em critérios definidos
    """
    try:
        job_text_lower = job_text.lower()
        
        # Calcular pontuação de skills
        skill_score = 0
        matching_skills = []
        
        for skill in user_skills:
            if skill.lower() in job_text_lower:
                skill_score += 1
                matching_skills.append(skill)
        
        # Verificar termos a evitar
        avoid_score = 0
        found_avoid_terms = []
        
        for term in avoid_terms:
            if term.lower() in job_text_lower:
                avoid_score += 1
                found_avoid_terms.append(term)
        
        # Verificar compatibilidade de nível
        level_compatible = True
        if experience_level.lower() in ['júnior', 'junior', 'estágio']:
            senior_terms = ['senior', 'sênior', 'lead', 'manager', 'diretor', 'especialista']
            level_compatible = not any(term in job_text_lower for term in senior_terms)
        
        # Calcular pontuação final
        compatibility_score = skill_score - (avoid_score * 2)
        
        # Critérios de compatibilidade
        is_compatible = (
            skill_score >= 1 and           # Pelo menos 1 skill match
            avoid_score == 0 and          # Nenhum termo indesejado
            level_compatible              # Nível apropriado
        )
        
        return {
            'compatible': is_compatible,
            'score': compatibility_score,
            'matching_skills': matching_skills,
            'avoid_terms_found': found_avoid_terms,
            'level_compatible': level_compatible
        }
        
    except Exception as e:
        return {
            'compatible': False,
            'score': 0,
            'matching_skills': [],
            'avoid_terms_found': [],
            'level_compatible': True
        }

def get_smart_keywords_from_skills(user_skills):
    """
    Gera palavras-chave inteligentes baseadas nas skills do usuário
    """
    skill_keywords = []
    
    # Expandir skills comuns
    skill_mapping = {
        'python': ['python', 'django', 'flask', 'pandas'],
        'data science': ['data science', 'análise de dados', 'ciência de dados', 'analytics'],
        'sql': ['sql', 'mysql', 'postgresql', 'database'],
        'machine learning': ['machine learning', 'ml', 'ia', 'artificial intelligence'],
        'javascript': ['javascript', 'js', 'react', 'node.js'],
        'java': ['java', 'spring', 'hibernate'],
        'analytics': ['analytics', 'google analytics', 'dados', 'métricas']
    }
    
    for skill in user_skills:
        skill_lower = skill.lower().strip()
        skill_keywords.append(skill_lower)
        
        if skill_lower in skill_mapping:
            skill_keywords.extend(skill_mapping[skill_lower])
    
    return list(set(skill_keywords))  # Remove duplicatas

async def smart_job_search(page, keywords, location, max_results=20):
    """
    Busca inteligente de vagas combinando múltiplas estratégias
    """
    try:
        # Estratégia 1: Buscar na página inicial por recomendações
        recommended_jobs = await find_recommended_jobs(page)
        
        if recommended_jobs:
            return recommended_jobs[:max_results]
        
        # Estratégia 2: Busca tradicional
        return await traditional_job_search(page, keywords, location, max_results)
        
    except Exception as e:
        return []

async def find_recommended_jobs(page):
    """
    Encontra vagas recomendadas na página inicial do LinkedIn
    """
    try:
        # Navegar para feed se não estiver
        current_url = page.url
        if 'feed' not in current_url:
            await page.goto('https://www.linkedin.com/feed/')
            await page.wait_for_timeout(3000)
        
        # Procurar seção de vagas recomendadas
        recommendation_selectors = [
            "div:has-text('Vagas que mais combinam')",
            "div:has-text('Jobs recommendations')",
            "[data-view-name='job-recommendations']"
        ]
        
        jobs = []
        for selector in recommendation_selectors:
            try:
                section = page.locator(selector).first
                if await section.is_visible():
                    job_cards = section.locator('.job-card, [data-job-id]')
                    count = await job_cards.count()
                    
                    for i in range(count):
                        jobs.append(job_cards.nth(i))
                    
                    return jobs
            except:
                continue
        
        return []
        
    except Exception as e:
        return []

async def traditional_job_search(page, keywords, location, max_results):
    """
    Busca tradicional de vagas
    """
    try:
        await page.goto('https://www.linkedin.com/jobs/')
        await page.wait_for_timeout(3000)
        
        # Preencher campos de busca
        keyword_field = page.locator("input[placeholder*='Pesquisar']").first
        if await keyword_field.is_visible():
            await keyword_field.fill(keywords)
        
        location_field = page.locator("input[placeholder*='Localização']").first
        if await location_field.is_visible():
            await location_field.fill(location)
        
        # Executar busca
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(5000)
        
        # Coletar vagas
        job_cards = page.locator('div[data-job-id], .job-card')
        count = await job_cards.count()
        
        jobs = []
        for i in range(min(count, max_results)):
            jobs.append(job_cards.nth(i))
        
        return jobs
        
    except Exception as e:
        return []

def format_job_count(count):
    """
    Formata o número de vagas para exibição
    """
    if count == 0:
        return "Nenhuma vaga"
    elif count == 1:
        return "1 vaga"
    else:
        return f"{count} vagas"

def validate_email(email):
    """
    Valida formato básico de e-mail
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

async def safe_select_option(locator, value):
    """
    Seleciona uma opção de forma segura
    
    Args:
        locator: Locator do Playwright
        value (str): Valor para selecionar
    
    Returns:
        bool: True se foi bem-sucedido, False caso contrário
    """
    try:
        await locator.wait_for(state="visible", timeout=5000)
        await locator.select_option(value)
        return True
    except Exception:
        return False

async def wait_for_element(page, selector, timeout=10000):
    """
    Aguarda um elemento aparecer na página
    
    Args:
        page: Página do Playwright
        selector (str): Seletor CSS/XPath
        timeout (int): Timeout em milissegundos
    
    Returns:
        Locator or None: Elemento encontrado ou None
    """
    try:
        locator = page.locator(selector)
        await locator.wait_for(state="visible", timeout=timeout)
        return locator
    except:
        return None

async def scroll_to_element(locator):
    """
    Faz scroll até um elemento específico
    
    Args:
        locator: Locator do Playwright
    """
    try:
        await locator.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)
    except:
        pass

async def scroll_page(page, direction="down", amount=3, pixels=300):
    """
    Faz scroll na página
    
    Args:
        page: Página do Playwright
        direction (str): "up" ou "down"
        amount (int): Quantidade de scrolls
        pixels (int): Pixels por scroll
    """
    try:
        for _ in range(amount):
            if direction == "down":
                await page.evaluate(f"window.scrollBy(0, {pixels});")
            else:
                await page.evaluate(f"window.scrollBy(0, -{pixels});")
            await asyncio.sleep(0.3)
    except:
        pass

async def wait_for_page_load(page, timeout=10):
    """
    Aguarda a página carregar completamente
    
    Args:
        page: Página do Playwright
        timeout (int): Timeout em segundos
    
    Returns:
        bool: True se a página carregou, False se timeout
    """
    try:
        # Aguarda todos os recursos carregarem
        await page.wait_for_load_state("networkidle", timeout=timeout * 1000)
        return True
    except:
        return False

async def get_element_text_safe(locator):
    """
    Obtém o texto de um elemento de forma segura
    
    Args:
        locator: Locator do Playwright
    
    Returns:
        str: Texto do elemento ou string vazia se falhar
    """
    try:
        text = await locator.text_content()
        return text.strip() if text else ""
    except:
        try:
            text = await locator.inner_text()
            return text.strip() if text else ""
        except:
            return ""

async def is_element_visible(locator):
    """
    Verifica se um elemento está visível na tela
    
    Args:
        locator: Locator do Playwright
    
    Returns:
        bool: True se visível, False caso contrário
    """
    try:
        return await locator.is_visible()
    except:
        return False

async def human_like_hover(locator):
    """
    Move o mouse de forma mais humana até um elemento
    
    Args:
        locator: Locator do Playwright
    """
    try:
        await locator.hover()
        await asyncio.sleep(random.uniform(0.1, 0.3))
    except:
        pass

def get_random_user_agent():
    """
    Retorna um User-Agent aleatório para Chrome moderno
    
    Returns:
        str: User-Agent string
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ]
    return random.choice(user_agents)

def format_job_count(count):
    """
    Formata o número de vagas para exibição
    
    Args:
        count (int): Número de vagas
    
    Returns:
        str: String formatada
    """
    if count == 0:
        return "Nenhuma vaga"
    elif count == 1:
        return "1 vaga"
    else:
        return f"{count} vagas"

def validate_email(email):
    """
    Valida formato básico de e-mail
    
    Args:
        email (str): E-mail para validar
    
    Returns:
        bool: True se válido, False caso contrário
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def clean_text(text):
    """
    Limpa texto removendo caracteres especiais e espaços extras
    
    Args:
        text (str): Texto para limpar
    
    Returns:
        str: Texto limpo
    """
    if not text:
        return ""
    
    # Remove quebras de linha e espaços extras
    text = re.sub(r'\s+', ' ', text)
    # Remove caracteres especiais problemáticos
    text = re.sub(r'[^\w\s\-.,!?áàâãéèêíïóôõöúçñü]', '', text, flags=re.IGNORECASE)
    return text.strip()

def log_performance(func):
    """
    Decorator para medir tempo de execução de funções
    
    Args:
        func: Função para decorar
    
    Returns:
        function: Função decorada
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"⏱️ {func.__name__} executou em {execution_time:.2f} segundos")
        return result
    return wrapper

def async_log_performance(func):
    """
    Decorator assíncrono para medir tempo de execução
    
    Args:
        func: Função assíncrona para decorar
    
    Returns:
        function: Função decorada
    """
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"⏱️ {func.__name__} executou em {execution_time:.2f} segundos")
        return result
    return wrapper

async def take_screenshot(page, filename=None):
    """
    Tira um screenshot da página atual
    
    Args:
        page: Página do Playwright
        filename (str): Nome do arquivo (opcional)
    
    Returns:
        str: Caminho do arquivo criado
    """
    try:
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        await page.screenshot(path=filename, full_page=True)
        return filename
    except Exception as e:
        print(f"Erro ao tirar screenshot: {e}")
        return None

async def wait_and_click(page, selector, timeout=5000):
    """
    Aguarda um elemento e clica nele
    
    Args:
        page: Página do Playwright
        selector (str): Seletor CSS/XPath
        timeout (int): Timeout em milissegundos
    
    Returns:
        bool: True se sucesso, False se falhou
    """
    try:
        locator = page.locator(selector)
        await locator.wait_for(state="visible", timeout=timeout)
        await locator.click()
        return True
    except:
        return False

def create_anti_detection_script():
    """
    Cria script JavaScript para evitar detecção de automação
    
    Returns:
        str: Script JavaScript
    """
    return """
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        
        // Mock plugins array
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Mock languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['pt-BR', 'pt', 'en-US', 'en'],
        });
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Mock chrome object
        if (!window.chrome) {
            window.chrome = {};
        }
        
        if (!window.chrome.runtime) {
            window.chrome.runtime = {};
        }
        
        // Override toString to hide automation
        const originalToString = Function.prototype.toString;
        Function.prototype.toString = function() {
            if (this === navigator.webdriver) {
                return 'function webdriver() { [native code] }';
            }
            return originalToString.apply(this, arguments);
        };
        
        // Hide automation indicators
        delete navigator.__proto__.webdriver;
        
        // Mock screen resolution
        Object.defineProperty(screen, 'width', {
            get: () => 1920
        });
        Object.defineProperty(screen, 'height', {
            get: () => 1080
        });
        
        // Add realistic timing
        const now = Date.now();
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
        
        // Mock device memory
        if (!navigator.deviceMemory) {
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
        }
    """

async def setup_stealth_context(context):
    """
    Configura contexto do navegador com configurações anti-detecção
    
    Args:
        context: BrowserContext do Playwright
    """
    try:
        # Adicionar script anti-detecção
        await context.add_init_script(create_anti_detection_script())
        
        # Configurar permissões
        await context.grant_permissions(['geolocation', 'notifications'])
        
        # Definir timezone
        await context.set_extra_http_headers({
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document'
        })
        
    except Exception as e:
        print(f"Erro ao configurar stealth: {e}")

def get_browser_options(headless=False):
    """
    Retorna opções otimizadas para o navegador
    
    Args:
        headless (bool): Se deve executar em modo headless
    
    Returns:
        dict: Opções do navegador
    """
    return {
        "headless": headless,
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--disable-features=VizDisplayCompositor",
            "--disable-ipc-flooding-protection",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-field-trial-config",
            "--disable-back-forward-cache",
            "--enable-features=NetworkService,NetworkServiceLogging",
            "--force-color-profile=srgb",
            "--metrics-recording-only",
            "--use-mock-keychain",
            "--disable-extensions-except=",
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-popup-blocking"
        ],
        "ignore_default_args": [
            "--enable-blink-features=AutomationControlled",
            "--enable-automation"
        ],
        "slow_mo": 50 if not headless else 0  # Adiciona delay natural
    } 
    return bool(re.match(pattern, email))

def clean_text(text):
    """
    Limpa texto removendo caracteres especiais e espaços extras
    """
    if not text:
        return ""
    
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\-.,!?áàâãéèêíïóôõöúçñü]', '', text, flags=re.IGNORECASE)
    return text.strip()

def parse_user_skills(skills_string):
    """
    Processa string de skills do usuário em lista limpa
    """
    if not skills_string:
        return []
    
    skills = [skill.strip() for skill in skills_string.split(',')]
    return [skill for skill in skills if skill]

def parse_avoid_terms(terms_string):
    """
    Processa string de termos a evitar em lista limpa
    """
    if not terms_string:
        return []
    
    terms = [term.strip() for term in terms_string.split(',')]
    return [term for term in terms if term]

async def take_screenshot(page, filename=None):
    """
    Tira um screenshot da página atual
    """
    try:
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_automation_{timestamp}.png"
        
        await page.screenshot(path=filename, full_page=True)
        return filename
    except Exception as e:
        return None

def create_anti_detection_script():
    """
    Cria script JavaScript para evitar detecção de automação
    """
    return """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['pt-BR', 'pt', 'en-US', 'en'],
        });
        
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        if (!window.chrome) {
            window.chrome = {};
        }
        
        if (!window.chrome.runtime) {
            window.chrome.runtime = {};
        }
        
        const originalToString = Function.prototype.toString;
        Function.prototype.toString = function() {
            if (this === navigator.webdriver) {
                return 'function webdriver() { [native code] }';
            }
            return originalToString.apply(this, arguments);
        };
        
        delete navigator.__proto__.webdriver;
        
        Object.defineProperty(screen, 'width', {
            get: () => 1920
        });
        Object.defineProperty(screen, 'height', {
            get: () => 1080
        });
        
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
        
        if (!navigator.deviceMemory) {
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
        }
    """

def get_browser_options(headless=False):
    """
    Retorna opções otimizadas para o navegador
    """
    return {
        "headless": headless,
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--disable-features=VizDisplayCompositor",
            "--disable-ipc-flooding-protection",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-field-trial-config",
            "--disable-back-forward-cache",
            "--enable-features=NetworkService,NetworkServiceLogging",
            "--force-color-profile=srgb",
            "--metrics-recording-only",
            "--use-mock-keychain",
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-popup-blocking"
        ],
        "ignore_default_args": [
            "--enable-blink-features=AutomationControlled",
            "--enable-automation"
        ],
        "slow_mo": 50 if not headless else 0
    }

def log_performance(func):
    """
    Decorator para medir tempo de execução de funções
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"⏱️ {func.__name__} executou em {execution_time:.2f} segundos")
        return result
    return wrapper

def async_log_performance(func):
    """
    Decorator assíncrono para medir tempo de execução
    """
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"⏱️ {func.__name__} executou em {execution_time:.2f} segundos")
        return result
    return wrapper

async def safe_select_option(locator, value):
    """
    Seleciona uma opção de forma segura
    
    Args:
        locator: Locator do Playwright
        value (str): Valor para selecionar
    
    Returns:
        bool: True se foi bem-sucedido, False caso contrário
    """
    try:
        await locator.wait_for(state="visible", timeout=5000)
        await locator.select_option(value)
        return True
    except Exception:
        return False

async def wait_for_element(page, selector, timeout=10000):
    """
    Aguarda um elemento aparecer na página
    
    Args:
        page: Página do Playwright
        selector (str): Seletor CSS/XPath
        timeout (int): Timeout em milissegundos
    
    Returns:
        Locator or None: Elemento encontrado ou None
    """
    try:
        locator = page.locator(selector)
        await locator.wait_for(state="visible", timeout=timeout)
        return locator
    except:
        return None

async def scroll_to_element(locator):
    """
    Faz scroll até um elemento específico
    
    Args:
        locator: Locator do Playwright
    """
    try:
        await locator.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)
    except:
        pass

async def scroll_page(page, direction="down", amount=3, pixels=300):
    """
    Faz scroll na página
    
    Args:
        page: Página do Playwright
        direction (str): "up" ou "down"
        amount (int): Quantidade de scrolls
        pixels (int): Pixels por scroll
    """
    try:
        for _ in range(amount):
            if direction == "down":
                await page.evaluate(f"window.scrollBy(0, {pixels});")
            else:
                await page.evaluate(f"window.scrollBy(0, -{pixels});")
            await asyncio.sleep(0.3)
    except:
        pass

async def wait_for_page_load(page, timeout=10):
    """
    Aguarda a página carregar completamente
    
    Args:
        page: Página do Playwright
        timeout (int): Timeout em segundos
    
    Returns:
        bool: True se a página carregou, False se timeout
    """
    try:
        # Aguarda todos os recursos carregarem
        await page.wait_for_load_state("networkidle", timeout=timeout * 1000)
        return True
    except:
        return False

async def get_element_text_safe(locator):
    """
    Obtém o texto de um elemento de forma segura
    
    Args:
        locator: Locator do Playwright
    
    Returns:
        str: Texto do elemento ou string vazia se falhar
    """
    try:
        text = await locator.text_content()
        return text.strip() if text else ""
    except:
        try:
            text = await locator.inner_text()
            return text.strip() if text else ""
        except:
            return ""

async def is_element_visible(locator):
    """
    Verifica se um elemento está visível na tela
    
    Args:
        locator: Locator do Playwright
    
    Returns:
        bool: True se visível, False caso contrário
    """
    try:
        return await locator.is_visible()
    except:
        return False

async def human_like_hover(locator):
    """
    Move o mouse de forma mais humana até um elemento
    
    Args:
        locator: Locator do Playwright
    """
    try:
        await locator.hover()
        await asyncio.sleep(random.uniform(0.1, 0.3))
    except:
        pass

def get_random_user_agent():
    """
    Retorna um User-Agent aleatório para Chrome moderno
    
    Returns:
        str: User-Agent string
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ]
    return random.choice(user_agents)

def format_job_count(count):
    """
    Formata o número de vagas para exibição
    
    Args:
        count (int): Número de vagas
    
    Returns:
        str: String formatada
    """
    if count == 0:
        return "Nenhuma vaga"
    elif count == 1:
        return "1 vaga"
    else:
        return f"{count} vagas"

def validate_email(email):
    """
    Valida formato básico de e-mail
    
    Args:
        email (str): E-mail para validar
    
    Returns:
        bool: True se válido, False caso contrário
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def clean_text(text):
    """
    Limpa texto removendo caracteres especiais e espaços extras
    
    Args:
        text (str): Texto para limpar
    
    Returns:
        str: Texto limpo
    """
    if not text:
        return ""
    
    # Remove quebras de linha e espaços extras
    text = re.sub(r'\s+', ' ', text)
    # Remove caracteres especiais problemáticos
    text = re.sub(r'[^\w\s\-.,!?áàâãéèêíïóôõöúçñü]', '', text, flags=re.IGNORECASE)
    return text.strip()

def log_performance(func):
    """
    Decorator para medir tempo de execução de funções
    
    Args:
        func: Função para decorar
    
    Returns:
        function: Função decorada
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"⏱️ {func.__name__} executou em {execution_time:.2f} segundos")
        return result
    return wrapper

def async_log_performance(func):
    """
    Decorator assíncrono para medir tempo de execução
    
    Args:
        func: Função assíncrona para decorar
    
    Returns:
        function: Função decorada
    """
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"⏱️ {func.__name__} executou em {execution_time:.2f} segundos")
        return result
    return wrapper

async def take_screenshot(page, filename=None):
    """
    Tira um screenshot da página atual
    
    Args:
        page: Página do Playwright
        filename (str): Nome do arquivo (opcional)
    
    Returns:
        str: Caminho do arquivo criado
    """
    try:
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        await page.screenshot(path=filename, full_page=True)
        return filename
    except Exception as e:
        print(f"Erro ao tirar screenshot: {e}")
        return None

async def wait_and_click(page, selector, timeout=5000):
    """
    Aguarda um elemento e clica nele
    
    Args:
        page: Página do Playwright
        selector (str): Seletor CSS/XPath
        timeout (int): Timeout em milissegundos
    
    Returns:
        bool: True se sucesso, False se falhou
    """
    try:
        locator = page.locator(selector)
        await locator.wait_for(state="visible", timeout=timeout)
        await locator.click()
        return True
    except:
        return False

def create_anti_detection_script():
    """
    Cria script JavaScript para evitar detecção de automação
    
    Returns:
        str: Script JavaScript
    """
    return """
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        
        // Mock plugins array
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Mock languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['pt-BR', 'pt', 'en-US', 'en'],
        });
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Mock chrome object
        if (!window.chrome) {
            window.chrome = {};
        }
        
        if (!window.chrome.runtime) {
            window.chrome.runtime = {};
        }
        
        // Override toString to hide automation
        const originalToString = Function.prototype.toString;
        Function.prototype.toString = function() {
            if (this === navigator.webdriver) {
                return 'function webdriver() { [native code] }';
            }
            return originalToString.apply(this, arguments);
        };
        
        // Hide automation indicators
        delete navigator.__proto__.webdriver;
        
        // Mock screen resolution
        Object.defineProperty(screen, 'width', {
            get: () => 1920
        });
        Object.defineProperty(screen, 'height', {
            get: () => 1080
        });
        
        // Add realistic timing
        const now = Date.now();
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
        
        // Mock device memory
        if (!navigator.deviceMemory) {
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
        }
    """

async def setup_stealth_context(context):
    """
    Configura contexto do navegador com configurações anti-detecção
    
    Args:
        context: BrowserContext do Playwright
    """
    try:
        # Adicionar script anti-detecção
        await context.add_init_script(create_anti_detection_script())
        
        # Configurar permissões
        await context.grant_permissions(['geolocation', 'notifications'])
        
        # Definir timezone
        await context.set_extra_http_headers({
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document'
        })
        
    except Exception as e:
        print(f"Erro ao configurar stealth: {e}")

def get_browser_options(headless=False):
    """
    Retorna opções otimizadas para o navegador
    
    Args:
        headless (bool): Se deve executar em modo headless
    
    Returns:
        dict: Opções do navegador
    """
    return {
        "headless": headless,
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--disable-features=VizDisplayCompositor",
            "--disable-ipc-flooding-protection",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-field-trial-config",
            "--disable-back-forward-cache",
            "--enable-features=NetworkService,NetworkServiceLogging",
            "--force-color-profile=srgb",
            "--metrics-recording-only",
            "--use-mock-keychain",
            "--disable-extensions-except=",
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-popup-blocking"
        ],
        "ignore_default_args": [
            "--enable-blink-features=AutomationControlled",
            "--enable-automation"
        ],
        "slow_mo": 50 if not headless else 0  # Adiciona delay natural
    }