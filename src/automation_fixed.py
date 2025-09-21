import time
import random
import asyncio
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from utils import random_delay

class LinkedInAutomation:
    """
    Classe principal para automação do LinkedIn usando Playwright - Versão 2024
    Com sistema de filtragem inteligente baseado nas recomendações do LinkedIn
    """
    
    def __init__(self, email, password, keywords, location, max_jobs, delay, log_callback, 
                 job_type="Todos", experience_level="Todos", work_type="Todas", 
                 contract_type="Todos", apply_filters=True, user_skills="", 
                 avoid_terms="", use_recommendations=True):
        """
        Inicializa a automação com os parâmetros fornecidos
        
        Args:
            email (str): Email para login no LinkedIn
            password (str): Senha para login no LinkedIn
            keywords (str): Palavras-chave para busca de vagas
            location (str): Localização das vagas
            max_jobs (int): Número máximo de vagas para salvar
            delay (int): Delay entre ações em segundos
            log_callback (function): Função para logging
            job_type (str): Tipo de vaga (compatibilidade)
            experience_level (str): Nível de experiência
            work_type (str): Modalidade de trabalho
            contract_type (str): Tipo de contrato
            apply_filters (bool): Se deve aplicar filtros avançados
            user_skills (str): Skills do usuário separadas por vírgula
            avoid_terms (str): Termos a evitar separados por vírgula
            use_recommendations (bool): Priorizar recomendações do LinkedIn
        """
        self.email = email
        self.password = password
        self.keywords = keywords
        self.location = location
        self.job_type = job_type
        self.max_jobs = max_jobs
        self.delay = delay
        self.log = log_callback
        
        self.experience_level = experience_level
        self.work_type = work_type
        self.contract_type = contract_type
        self.apply_filters = apply_filters
        
        # Novos parâmetros para filtragem inteligente
        self.user_skills = [skill.strip().lower() for skill in user_skills.split(',') if skill.strip()]
        self.avoid_terms = [term.strip().lower() for term in avoid_terms.split(',') if term.strip()]
        self.use_recommendations = use_recommendations
        
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_running = False
        self.saved_jobs_count = 0

    async def setup_browser(self):
        """
        Configura e inicializa o navegador Playwright
        """
        self.log("Configurando navegador com Playwright...")
        
        try:
            # Inicializar Playwright
            self.playwright = await async_playwright().start()
            
            # Configurar opções do navegador
            browser_options = {
                "headless": False,
                "args": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--allow-running-insecure-content",
                    "--disable-features=VizDisplayCompositor",
                ],
                "ignore_default_args": ["--enable-blink-features=AutomationControlled"],
            }
            
            # Lançar navegador Chrome
            self.browser = await self.playwright.chromium.launch(**browser_options)
            
            # Criar contexto com configurações anti-detecção
            context_options = {
                "viewport": {"width": 1366, "height": 768},
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
                "locale": "pt-BR",
                "timezone_id": "America/Sao_Paulo",
                "extra_http_headers": {
                    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
                }
            }
            
            self.context = await self.browser.new_context(**context_options)
            
            # Configurações avançadas anti-detecção
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['pt-BR', 'pt', 'en-US', 'en'],
                });
            """)
            
            # Criar nova página
            self.page = await self.context.new_page()
            
            # Teste básico
            self.log("Testando navegação...")
            await self.page.goto("https://www.google.com", wait_until="domcontentloaded")
            
            if "Google" in await self.page.title():
                self.log("Navegador Playwright configurado com sucesso!")
                return True
            else:
                raise Exception("Teste de navegação falhou")
            
        except Exception as e:
            self.log(f"Erro ao configurar navegador: {e}")
            await self.cleanup()
            raise

    async def login(self):
        """
        Realiza login no LinkedIn
        """
        self.log("Fazendo login no LinkedIn...")
        
        try:
            # Navegar para página de login
            await self.page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
            await self.page.wait_for_timeout(random.randint(2000, 4000))
            
            # Preencher campo de e-mail
            email_field = self.page.locator("#username")
            await email_field.wait_for(state="visible")
            await email_field.fill(self.email)
            await self.page.wait_for_timeout(random.randint(500, 1500))
            
            # Preencher campo de senha
            password_field = self.page.locator("#password")
            await password_field.fill(self.password)
            await self.page.wait_for_timeout(random.randint(500, 1500))
            
            # Clicar no botão de login
            login_button = self.page.locator("button[type='submit']")
            await login_button.click()
            
            self.log("Credenciais enviadas, aguardando...")
            await self.page.wait_for_timeout(random.randint(5000, 8000))
            
            # Verificar sucesso do login
            current_url = self.page.url
            if "feed" in current_url or "/in/" in current_url:
                self.log("Login realizado com sucesso!")
                return True
            elif "challenge" in current_url or "checkpoint" in current_url:
                self.log("Verificação adicional necessária. Complete manualmente.")
                await self.page.wait_for_url("**/feed/**", timeout=300000)
                return True
            else:
                self.log("Falha no login. Verifique suas credenciais.")
                return False
                
        except Exception as e:
            self.log(f"Erro durante login: {e}")
            return False

    async def save_recommended_jobs(self):
        """
        Salva vagas da seção "Vagas que mais combinam com seu perfil"
        Aproveitando o algoritmo do próprio LinkedIn
        """
        self.log("Processando vagas recomendadas pelo LinkedIn...")
        
        try:
            # Navegar para página inicial se não estiver
            await self.page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)
            
            # Procurar seção de vagas recomendadas
            recommended_selectors = [
                "div:has-text('Vagas que mais combinam com seu perfil')",
                "div:has-text('Jobs recommendations')",
                ".job-card-container",
                "[data-view-name='job-recommendations']"
            ]
            
            section_found = False
            for selector in recommended_selectors:
                try:
                    section = self.page.locator(selector).first
                    if await section.is_visible():
                        await section.scroll_into_view_if_needed()
                        section_found = True
                        self.log(f"Seção de vagas recomendadas encontrada!")
                        break
                except:
                    continue
            
            if not section_found:
                self.log("Vagas recomendadas não encontradas, indo para busca normal...")
                return await self.search_jobs()
            
            # Encontrar vagas recomendadas
            job_cards = self.page.locator(".job-card, .job-recommendation-card, [data-job-id]")
            count = await job_cards.count()
            
            if count == 0:
                self.log("Nenhuma vaga recomendada encontrada, fazendo busca normal...")
                return await self.search_jobs()
            
            self.log(f"Encontradas {count} vagas recomendadas pelo LinkedIn")
            saved_count = 0
            
            # Processar cada vaga recomendada
            for i in range(min(count, self.max_jobs)):
                if not self.is_running:
                    break
                    
                try:
                    job_card = job_cards.nth(i)
                    await job_card.scroll_into_view_if_needed()
                    await self.page.wait_for_timeout(1000)
                    
                    # Verificar se a vaga é compatível
                    if await self.is_job_compatible(job_card):
                        await job_card.click()
                        await self.page.wait_for_timeout(2000)
                        
                        # Tentar salvar a vaga
                        if await self.save_current_job():
                            saved_count += 1
                            self.saved_jobs_count = saved_count
                            self.log(f"Vaga recomendada {saved_count} salva com sucesso!")
                        
                        await self.page.wait_for_timeout(self.delay * 1000)
                    else:
                        self.log(f"Vaga {i+1} não atende aos critérios, pulando...")
                        
                except Exception as e:
                    self.log(f"Erro ao processar vaga recomendada {i+1}: {e}")
                    continue
            
            self.log(f"Processamento concluído! {saved_count} vagas recomendadas salvas.")
            return saved_count
            
        except Exception as e:
            self.log(f"Erro ao processar vagas recomendadas: {e}")
            return await self.search_jobs()

    async def is_job_compatible(self, job_card):
        """
        Verifica se a vaga é compatível com critérios definidos
        """
        try:
            # Extrair informações da vaga
            job_text = await job_card.text_content()
            job_text_lower = job_text.lower()
            
            # Verificar skills do usuário
            skill_matches = 0
            if self.user_skills:
                skill_matches = sum(1 for skill in self.user_skills if skill in job_text_lower)
            else:
                # Skills padrão baseadas nas palavras-chave
                default_skills = [word.strip().lower() for word in self.keywords.split(',')]
                skill_matches = sum(1 for skill in default_skills if skill in job_text_lower)
            
            # Verificar termos a evitar
            has_unwanted = any(term in job_text_lower for term in self.avoid_terms)
            
            # Verificar nível de experiência
            level_ok = True
            if self.experience_level == "Júnior" or self.experience_level == "Estágio":
                senior_terms = ["senior", "sênior", "lead", "manager", "diretor", "especialista"]
                has_senior_terms = any(term in job_text_lower for term in senior_terms)
                level_ok = not has_senior_terms
            
            # Verificar modalidade de trabalho
            work_mode_ok = True
            if self.work_type != "Todas":
                work_terms = {
                    "Remoto": ["remoto", "remote", "home office", "trabalho remoto"],
                    "Presencial": ["presencial", "escritório", "office", "local"],
                    "Híbrido": ["híbrido", "hybrid", "misto"]
                }
                
                if self.work_type in work_terms:
                    work_mode_ok = any(term in job_text_lower for term in work_terms[self.work_type])
            
            # Critério final de compatibilidade
            compatible = (
                skill_matches >= 1 and     # Pelo menos 1 skill match
                not has_unwanted and       # Sem termos indesejados
                level_ok and              # Nível apropriado
                work_mode_ok              # Modalidade OK
            )
            
            if compatible:
                self.log(f"Vaga compatível! Skills: {skill_matches}, Nível: OK, Modalidade: OK")
            
            return compatible
            
        except Exception as e:
            self.log(f"Erro na verificação de compatibilidade: {e}")
            return True

    async def save_current_job(self):
        """
        Salva a vaga atualmente aberta
        """
        try:
            # Procurar botão salvar
            save_selectors = [
                "button:has-text('Salvar')",
                "button[aria-label*='Salvar']",
                "[data-control-name*='save']",
                ".jobs-save-button"
            ]
            
            for selector in save_selectors:
                try:
                    save_button = self.page.locator(selector).first
                    if await save_button.is_visible() and await save_button.is_enabled():
                        # Verificar se já está salva
                        button_text = await save_button.text_content() or ""
                        if "salva" in button_text.lower():
                            return False
                        
                        await save_button.click()
                        await self.page.wait_for_timeout(1000)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.log(f"Erro ao salvar vaga: {e}")
            return False

    async def search_jobs(self):
        """
        Busca vagas com base nos filtros fornecidos (método tradicional)
        """
        self.log(f"Buscando vagas: '{self.keywords}' em '{self.location}'")
        
        try:
            # Navegar para página de vagas
            await self.page.goto("https://www.linkedin.com/jobs/", wait_until="domcontentloaded")
            await self.page.wait_for_timeout(random.randint(2000, 4000))
            
            # Buscar campo de palavras-chave
            keyword_selectors = [
                "input[placeholder*='Pesquisar']",
                "input[data-job-search-box='true']",
                ".jobs-search-box__text-input:first-of-type"
            ]
            
            keyword_field = None
            for selector in keyword_selectors:
                try:
                    keyword_field = self.page.locator(selector).first
                    await keyword_field.wait_for(state="visible", timeout=5000)
                    break
                except:
                    continue
            
            if not keyword_field:
                raise Exception("Campo de pesquisa não encontrado")
            
            # Limpar e preencher palavras-chave
            await keyword_field.fill("")
            await keyword_field.type(self.keywords, delay=50)
            await self.page.wait_for_timeout(random.randint(500, 1500))
            
            # Buscar campo de localização
            location_selectors = [
                "input[placeholder*='Localização']",
                ".jobs-search-box__text-input:nth-of-type(2)"
            ]
            
            location_field = None
            for selector in location_selectors:
                try:
                    location_field = self.page.locator(selector).first
                    if await location_field.is_visible():
                        break
                except:
                    continue
            
            if location_field:
                await location_field.fill("")
                await location_field.type(self.location, delay=50)
                await self.page.wait_for_timeout(random.randint(500, 1500))
            
            # Executar busca
            await self.page.keyboard.press("Enter")
            
            self.log("Executando busca tradicional...")
            await self.page.wait_for_timeout(random.randint(3000, 6000))
            
            # Aguardar resultados carregarem
            await self.page.wait_for_selector(
                "div[data-job-id], .job-card, .result-card", 
                timeout=20000
            )
            
            # Aplicar filtros avançados se solicitado
            if self.apply_filters:
                await self.apply_advanced_filters()
            
            self.log("Resultados de busca carregados!")
            return True
            
        except Exception as e:
            self.log(f"Erro durante busca: {e}")
            return False

    async def apply_advanced_filters(self):
        """
        Aplica filtros avançados
        """
        try:
            self.log("Aplicando filtros avançados...")
            
            filter_selectors = [
                "button:has-text('Todos os filtros')",
                "button:has-text('Filtros')",
                "[data-control-name*='filter']"
            ]
            
            filter_button = None
            for selector in filter_selectors:
                try:
                    filter_button = self.page.locator(selector).first
                    if await filter_button.is_visible():
                        break
                except:
                    continue
            
            if filter_button:
                await filter_button.click()
                await self.page.wait_for_timeout(random.randint(2000, 3000))
                
                # Aplicar filtros específicos
                await self.apply_work_type_filter()
                await self.apply_experience_filter()
                await self.apply_contract_filter()
                
                # Aplicar filtros
                apply_selectors = [
                    "button:has-text('Aplicar')",
                    "button:has-text('Mostrar')",
                    "[data-control-name='filter_show_results']"
                ]
                
                for selector in apply_selectors:
                    try:
                        apply_button = self.page.locator(selector).first
                        if await apply_button.is_visible() and await apply_button.is_enabled():
                            await apply_button.click()
                            self.log("Filtros aplicados!")
                            await self.page.wait_for_timeout(random.randint(3000, 5000))
                            return
                    except:
                        continue
            else:
                self.log("Botão de filtros não encontrado")
                
        except Exception as e:
            self.log(f"Erro ao aplicar filtros avançados: {e}")

    async def apply_work_type_filter(self):
        """
        Aplica filtro de modalidade de trabalho
        """
        if self.work_type == "Todas":
            return
            
        try:
            work_type_mapping = {
                "Remoto": ["Remoto", "Remote", "Home office"],
                "Presencial": ["Presencial", "On-site", "No local"],
                "Híbrido": ["Híbrido", "Hybrid", "Misto"]
            }
            
            search_terms = work_type_mapping.get(self.work_type, [self.work_type])
            
            for term in search_terms:
                try:
                    checkbox = self.page.locator(f"input[type='checkbox'] + label:has-text('{term}')").first
                    if await checkbox.is_visible():
                        await checkbox.click()
                        self.log(f"Filtro aplicado: {term}")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.log(f"Erro ao aplicar filtro de modalidade: {e}")

    async def apply_experience_filter(self):
        """
        Aplica filtro de nível de experiência
        """
        if self.experience_level == "Todos":
            return
            
        try:
            experience_mapping = {
                "Estágio": ["Estágio", "Internship", "Estagiário"],
                "Júnior": ["Júnior", "Junior", "Entry level", "Iniciante"],
                "Pleno": ["Pleno", "Mid-level", "Intermediário", "Associate"],
                "Sênior": ["Sênior", "Senior", "Experiente"],
                "Diretor": ["Diretor", "Director", "Gerente"],
                "Executivo": ["Executivo", "Executive", "C-level"]
            }
            
            search_terms = experience_mapping.get(self.experience_level, [self.experience_level])
            
            for term in search_terms:
                try:
                    checkbox = self.page.locator(f"input[type='checkbox'] + label:has-text('{term}')").first
                    if await checkbox.is_visible():
                        await checkbox.click()
                        self.log(f"Filtro de experiência aplicado: {term}")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.log(f"Erro ao aplicar filtro de experiência: {e}")

    async def apply_contract_filter(self):
        """
        Aplica filtro de tipo de contrato
        """
        if self.contract_type == "Todos":
            return
            
        try:
            contract_mapping = {
                "CLT": ["CLT", "Tempo integral", "Full-time", "Efetivo"],
                "PJ": ["PJ", "Freelance", "Autônomo", "Contractor"],
                "Temporário": ["Temporário", "Temporary", "Contract", "Contrato"],
                "Freelancer": ["Freelancer", "Freelance", "Autônomo"],
                "Estágio": ["Estágio", "Internship", "Estagiário"],
                "Trainee": ["Trainee", "Programa trainee", "Graduate"]
            }
            
            search_terms = contract_mapping.get(self.contract_type, [self.contract_type])
            
            for term in search_terms:
                try:
                    checkbox = self.page.locator(f"input[type='checkbox'] + label:has-text('{term}')").first
                    if await checkbox.is_visible():
                        await checkbox.click()
                        self.log(f"Filtro de contrato aplicado: {term}")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.log(f"Erro ao aplicar filtro de contrato: {e}")

    async def save_jobs(self):
        """
        Salva as vagas encontradas - versão tradicional para busca normal
        """
        self.log(f"Iniciando salvamento de até {self.max_jobs} vagas...")
        
        saved_count = 0
        attempts = 0
        max_attempts = 50
        
        while saved_count < self.max_jobs and attempts < max_attempts and self.is_running:
            try:
                attempts += 1
                
                job_selectors = [
                    "div[data-job-id]",
                    ".job-card",
                    ".result-card"
                ]
                
                job_cards = None
                for selector in job_selectors:
                    job_cards = self.page.locator(selector)
                    count = await job_cards.count()
                    if count > 0:
                        break
                
                if not job_cards or await job_cards.count() == 0:
                    self.log("Nenhuma vaga encontrada na página")
                    break
                
                count = await job_cards.count()
                self.log(f"Processando {count} vagas...")
                
                for i in range(min(count, self.max_jobs - saved_count)):
                    if saved_count >= self.max_jobs or not self.is_running:
                        break
                    
                    try:
                        job_card = job_cards.nth(i)
                        
                        # Scroll até a vaga
                        await job_card.scroll_into_view_if_needed()
                        await self.page.wait_for_timeout(random.randint(1000, 2000))
                        
                        # Verificar compatibilidade antes de clicar
                        if await self.is_job_compatible(job_card):
                            # Clicar na vaga
                            await job_card.click()
                            await self.page.wait_for_timeout(random.randint(2000, 3000))
                            
                            # Tentar salvar
                            if await self.save_current_job():
                                saved_count += 1
                                self.saved_jobs_count = saved_count
                                self.log(f"Vaga {saved_count} salva!")
                            
                            await self.page.wait_for_timeout(random.randint(
                                self.delay * 1000, (self.delay + 2) * 1000
                            ))
                        else:
                            self.log(f"Vaga {i+1} não compatível, pulando...")
                        
                    except Exception as e:
                        self.log(f"Erro ao processar vaga {i + 1}: {e}")
                        continue
                
                # Ir para próxima página se necessário
                if saved_count < self.max_jobs and self.is_running:
                    if not await self.go_to_next_page():
                        break
                
            except Exception as e:
                self.log(f"Erro durante salvamento: {e}")
                break
        
        self.log(f"Processo concluído! {saved_count} vagas salvas no total.")
        return saved_count

    async def go_to_next_page(self):
        """
        Navega para a próxima página de resultados
        """
        try:
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(random.randint(2000, 3000))
            
            next_selectors = [
                "button[aria-label='Próxima']",
                "button:has-text('Próxima')",
                "button[aria-label='Next']",
                "a[aria-label*='Next']"
            ]
            
            for selector in next_selectors:
                try:
                    next_button = self.page.locator(selector).first
                    if await next_button.is_visible() and await next_button.is_enabled():
                        await next_button.click()
                        self.log("Próxima página...")
                        await self.page.wait_for_timeout(random.randint(3000, 5000))
                        return True
                except:
                    continue
            
            return False
            
        except:
            return False

    async def run_async(self):
        """
        Executa todo o processo de automação de forma assíncrona
        """
        self.is_running = True
        
        try:
            # 1. Configurar navegador
            if not await self.setup_browser():
                return False
            
            # 2. Fazer login
            if not await self.login():
                return False
            
            # 3. Escolher estratégia baseada nas configurações
            if self.use_recommendations:
                self.log("Priorizando vagas recomendadas pelo LinkedIn...")
                saved_count = await self.save_recommended_jobs()
            else:
                self.log("Usando busca tradicional...")
                if not await self.search_jobs():
                    return False
                saved_count = await self.save_jobs()
            
            self.log(f"Automação finalizada! {saved_count} vagas salvas.")
            return True
            
        except Exception as e:
            self.log(f"Erro geral na automação: {e}")
            return False
        finally:
            self.is_running = False
            await self.cleanup()

    def run(self):
        """
        Método síncrono para compatibilidade com a GUI existente
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.run_async())
        except Exception as e:
            self.log(f"Erro na execução: {e}")
            return False

    def stop(self):
        """
        Para a automação
        """
        self.is_running = False
        self.log("Parando automação...")

    async def cleanup(self):
        """
        Limpa recursos do navegador
        """
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.log("Navegador fechado")
        except:
            pass

    def quit(self):
        """
        Método síncrono para limpeza (compatibilidade)
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.cleanup())
            else:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(self.cleanup())
        except:
            pass