import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from threading import Thread
import time
from automation_fixed import LinkedInAutomation

class LinkedInGUI:
    """
    Classe responsável pela interface gráfica da aplicação
    Versão atualizada com filtragem inteligente de vagas
    """
    
    def __init__(self):
        """
        Inicializa a interface gráfica
        """
        self.root = tk.Tk()
        self.automation = None
        self.is_running = False
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """
        Configura a janela principal
        """
        self.root.title("LinkedIn Job Automation Tool - Smart Edition")
        self.root.geometry("750x900")
        self.root.resizable(True, True)
        
        # Centraliza a janela na tela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (750 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"750x900+{x}+{y}")
        
        # Configura o ícone (opcional)
        try:
            self.root.iconbitmap('assets/icon.ico')
        except:
            pass
    
    def create_widgets(self):
        """
        Cria todos os widgets da interface com scrollbar
        """
        # Frame principal com scrollbar
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame principal com padding
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        row = 0
        
        # Título
        title_label = ttk.Label(main_frame, text="LinkedIn Job Automation - Smart Edition", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=row, column=0, pady=(0, 10))
        row += 1
        
        # Indicador de versão
        version_label = ttk.Label(main_frame, text="🎯 Filtragem Inteligente + Compatível Chrome 140+", 
                                 font=('Arial', 9), foreground='green')
        version_label.grid(row=row, column=0, pady=(0, 20))
        row += 1
        
        # Seção de Login
        self.create_login_section(main_frame, row)
        row += 3
        
        # Seção de Configuração de Perfil
        self.create_profile_section(main_frame, row)
        row += 4
        
        # Seção de Filtros
        self.create_filters_section(main_frame, row)
        row += 9
        
        # Seção de Configurações Avançadas
        self.create_advanced_section(main_frame, row)
        row += 5
        
        # Seção de Controle
        self.create_control_section(main_frame, row)
        row += 2
        
        # Seção de Status/Log
        self.create_status_section(main_frame, row)
    
    def create_login_section(self, parent, start_row):
        """
        Cria a seção de login
        """
        login_label = ttk.Label(parent, text="Credenciais do LinkedIn", 
                               font=('Arial', 12, 'bold'))
        login_label.grid(row=start_row, column=0, sticky=tk.W, pady=(10, 5))
        
        login_frame = ttk.LabelFrame(parent, text="Login", padding="10")
        login_frame.grid(row=start_row+1, column=0, sticky=(tk.W, tk.E), pady=5)
        login_frame.columnconfigure(1, weight=1)
        
        # Campo de e-mail
        ttk.Label(login_frame, text="E-mail:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(login_frame, textvariable=self.email_var, width=50)
        self.email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Campo de senha
        ttk.Label(login_frame, text="Senha:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(login_frame, textvariable=self.password_var, 
                                      show="*", width=50)
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
    
    def create_profile_section(self, parent, start_row):
        """
        Cria a seção de configuração de perfil para filtragem inteligente
        """
        profile_label = ttk.Label(parent, text="Configuração do Seu Perfil", 
                                 font=('Arial', 12, 'bold'))
        profile_label.grid(row=start_row, column=0, sticky=tk.W, pady=(20, 5))
        
        profile_frame = ttk.LabelFrame(parent, text="Filtragem Inteligente", padding="10")
        profile_frame.grid(row=start_row+1, column=0, sticky=(tk.W, tk.E), pady=5)
        profile_frame.columnconfigure(1, weight=1)
        
        # Suas skills principais
        ttk.Label(profile_frame, text="Suas Skills:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.user_skills_var = tk.StringVar(value="Python, Data Science, SQL, Analytics, Machine Learning")
        skills_entry = ttk.Entry(profile_frame, textvariable=self.user_skills_var, width=47)
        skills_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Termos a evitar
        ttk.Label(profile_frame, text="Evitar termos:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.avoid_terms_var = tk.StringVar(value="Senior, Lead, Manager, Diretor")
        avoid_entry = ttk.Entry(profile_frame, textvariable=self.avoid_terms_var, width=47)
        avoid_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Priorizar recomendações do LinkedIn
        self.use_recommendations_var = tk.BooleanVar(value=True)
        recommendations_check = ttk.Checkbutton(
            profile_frame, 
            text="🎯 Priorizar vagas recomendadas pelo LinkedIn (mais inteligente)", 
            variable=self.use_recommendations_var
        )
        recommendations_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Dica explicativa
        tip_label = ttk.Label(profile_frame, 
                             text="💡 Dica: O LinkedIn analisa seu perfil e mostra vagas compatíveis automaticamente",
                             font=('Arial', 8), foreground='gray')
        tip_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
    
    def create_filters_section(self, parent, start_row):
        """
        Cria a seção de filtros de busca
        """
        filters_label = ttk.Label(parent, text="Filtros de Busca (Backup)", 
                                 font=('Arial', 12, 'bold'))
        filters_label.grid(row=start_row, column=0, sticky=tk.W, pady=(20, 5))
        
        filters_frame = ttk.LabelFrame(parent, text="Busca Tradicional (se recomendações não funcionarem)", padding="10")
        filters_frame.grid(row=start_row+1, column=0, sticky=(tk.W, tk.E), pady=5)
        filters_frame.columnconfigure(1, weight=1)
        
        # Palavras-chave
        ttk.Label(filters_frame, text="Palavras-chave:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.keywords_var = tk.StringVar(value="Python, Data Science")
        self.keywords_entry = ttk.Entry(filters_frame, textvariable=self.keywords_var, width=47)
        self.keywords_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Localização
        ttk.Label(filters_frame, text="Localização:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.location_var = tk.StringVar()
        location_combo = ttk.Combobox(filters_frame, textvariable=self.location_var, width=44)
        location_combo['values'] = ('Brasil', 'São Paulo', 'Rio de Janeiro', 'Remoto', 
                                   'Belo Horizonte', 'Brasília', 'Porto Alegre', 'Recife')
        location_combo.set('Brasil')
        location_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Nível de experiência
        ttk.Label(filters_frame, text="Nível:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.experience_level_var = tk.StringVar()
        experience_combo = ttk.Combobox(filters_frame, textvariable=self.experience_level_var, width=44)
        experience_combo['values'] = ('Todos', 'Estágio', 'Júnior', 'Pleno', 'Sênior', 'Diretor', 'Executivo')
        experience_combo.set('Júnior')
        experience_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Modalidade de trabalho
        ttk.Label(filters_frame, text="Modalidade:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        self.work_type_var = tk.StringVar()
        work_type_combo = ttk.Combobox(filters_frame, textvariable=self.work_type_var, width=44)
        work_type_combo['values'] = ('Todas', 'Remoto', 'Presencial', 'Híbrido')
        work_type_combo.set('Remoto')
        work_type_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Tipo de contrato
        ttk.Label(filters_frame, text="Contrato:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10))
        self.contract_type_var = tk.StringVar()
        contract_combo = ttk.Combobox(filters_frame, textvariable=self.contract_type_var, width=44)
        contract_combo['values'] = ('Todos', 'CLT', 'PJ', 'Temporário', 'Freelancer', 'Estágio', 'Trainee')
        contract_combo.set('Todos')
        contract_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Número máximo de vagas
        ttk.Label(filters_frame, text="Max. Vagas:").grid(row=5, column=0, sticky=tk.W, padx=(0, 10))
        self.max_jobs_var = tk.StringVar(value="10")
        max_jobs_spinbox = ttk.Spinbox(filters_frame, textvariable=self.max_jobs_var, 
                                      from_=1, to=50, width=44)
        max_jobs_spinbox.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Delay entre ações
        ttk.Label(filters_frame, text="Delay (seg):").grid(row=6, column=0, sticky=tk.W, padx=(0, 10))
        self.delay_var = tk.StringVar(value="3")
        delay_spinbox = ttk.Spinbox(filters_frame, textvariable=self.delay_var, 
                                   from_=1, to=10, width=44)
        delay_spinbox.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Aplicar filtros avançados
        self.apply_filters_var = tk.BooleanVar(value=True)
        filters_check = ttk.Checkbutton(filters_frame, text="Aplicar filtros avançados na busca tradicional", 
                                       variable=self.apply_filters_var)
        filters_check.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def create_advanced_section(self, parent, start_row):
        """
        Cria a seção de configurações avançadas
        """
        advanced_label = ttk.Label(parent, text="Configurações Avançadas", 
                                  font=('Arial', 12, 'bold'))
        advanced_label.grid(row=start_row, column=0, sticky=tk.W, pady=(20, 5))
        
        advanced_frame = ttk.LabelFrame(parent, text="Configurações do Navegador", padding="10")
        advanced_frame.grid(row=start_row+1, column=0, sticky=(tk.W, tk.E), pady=5)
        advanced_frame.columnconfigure(1, weight=1)
        
        # Modo headless
        self.headless_var = tk.BooleanVar(value=False)
        headless_check = ttk.Checkbutton(advanced_frame, text="Modo invisível (headless) - mais rápido", 
                                        variable=self.headless_var)
        headless_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Anti-detecção
        self.stealth_var = tk.BooleanVar(value=True)
        stealth_check = ttk.Checkbutton(advanced_frame, text="Anti-detecção avançada (recomendado)", 
                                       variable=self.stealth_var)
        stealth_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Estratégia de automação
        strategy_label = ttk.Label(advanced_frame, text="Estratégia:", font=('Arial', 10, 'bold'))
        strategy_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        strategy_info = ttk.Label(advanced_frame, 
                                 text="1º: Tenta vagas recomendadas\n2º: Se falhar, usa busca tradicional",
                                 font=('Arial', 8), foreground='blue')
        strategy_info.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
    
    def create_control_section(self, parent, start_row):
        """
        Cria a seção de controle (botões)
        """
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=start_row, column=0, pady=20)
        
        # Botão para testar navegador
        self.test_button = ttk.Button(control_frame, text="🧪 Testar Navegador", 
                                     command=self.test_browser)
        self.test_button.grid(row=0, column=0, padx=10)
        
        # Botão para iniciar automação
        self.start_button = ttk.Button(control_frame, text="🚀 Iniciar Automação Smart", 
                                      command=self.start_automation)
        self.start_button.grid(row=0, column=1, padx=10)
        
        # Botão para parar automação
        self.stop_button = ttk.Button(control_frame, text="⏹️ Parar", 
                                     command=self.stop_automation, state='disabled')
        self.stop_button.grid(row=0, column=2, padx=10)
    
    def create_status_section(self, parent, start_row):
        """
        Cria a seção de status e logs
        """
        status_label = ttk.Label(parent, text="Status e Logs", 
                                font=('Arial', 12, 'bold'))
        status_label.grid(row=start_row, column=0, sticky=tk.W, pady=(20, 5))
        
        # Frame de informações
        info_frame = ttk.Frame(parent)
        info_frame.grid(row=start_row+1, column=0, sticky=(tk.W, tk.E), pady=5)
        info_frame.columnconfigure(0, weight=1)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(info_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Label de status
        self.status_label = ttk.Label(info_frame, text="Pronto para iniciar automação inteligente", 
                                     foreground='blue')
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Frame para controles dos logs
        log_controls_frame = ttk.Frame(parent)
        log_controls_frame.grid(row=start_row+2, column=0, sticky=(tk.W, tk.E), pady=(10, 5))
        log_controls_frame.columnconfigure(0, weight=1)
        
        # Botões de controle dos logs
        buttons_frame = ttk.Frame(log_controls_frame)
        buttons_frame.grid(row=0, column=0, sticky=tk.W)
        
        self.clear_logs_button = ttk.Button(buttons_frame, text="🗑️ Limpar Logs", 
                                          command=self.clear_logs)
        self.clear_logs_button.grid(row=0, column=0, padx=(0, 10))
        
        self.save_logs_button = ttk.Button(buttons_frame, text="💾 Salvar Logs", 
                                         command=self.save_logs)
        self.save_logs_button.grid(row=0, column=1, padx=(0, 10))
        
        # Checkbox para auto-scroll
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = ttk.Checkbutton(buttons_frame, text="Auto-scroll", 
                                          variable=self.auto_scroll_var)
        auto_scroll_check.grid(row=0, column=2)
        
        # Frame para logs com altura fixa
        logs_frame = ttk.LabelFrame(parent, text="Logs da Execução", padding="5")
        logs_frame.grid(row=start_row+3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        
        # Text widget para logs
        self.log_text = scrolledtext.ScrolledText(
            logs_frame, 
            height=12,
            width=85, 
            wrap=tk.WORD, 
            state='disabled',
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar tags de cores
        self.log_text.tag_configure("info", foreground="blue")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("timestamp", foreground="gray")
        self.log_text.tag_configure("smart", foreground="purple")
        
        # Expansão do frame de logs
        parent.rowconfigure(start_row+3, weight=1)
    
    def log_message(self, message):
        """
        Adiciona uma mensagem no log com formatação colorida
        """
        timestamp = time.strftime("%H:%M:%S")
        
        # Determinar tipo de log e cor
        message_lower = message.lower()
        if "erro" in message_lower or "error" in message_lower or "❌" in message:
            tag = "error"
        elif "sucesso" in message_lower or "success" in message_lower or "✅" in message:
            tag = "success"
        elif "aviso" in message_lower or "warning" in message_lower or "⚠️" in message:
            tag = "warning"
        elif "compatível" in message_lower or "inteligente" in message_lower or "🎯" in message:
            tag = "smart"
        else:
            tag = "info"
        
        self.log_text.config(state='normal')
        
        # Inserir timestamp
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Inserir mensagem
        self.log_text.insert(tk.END, f"{message}\n", tag)
        
        # Auto-scroll se habilitado
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
            
        self.log_text.config(state='disabled')
        self.root.update_idletasks()
    
    def clear_logs(self):
        """
        Limpa todos os logs
        """
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        self.log_message("Logs limpos")
    
    def save_logs(self):
        """
        Salva os logs em um arquivo
        """
        try:
            import tkinter.filedialog as filedialog
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            default_filename = f"linkedin_smart_automation_logs_{timestamp}.txt"
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialvalue=default_filename
            )
            
            if filename:
                content = self.log_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("Sucesso", f"Logs salvos em:\n{filename}")
                self.log_message(f"Logs salvos em: {filename}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar logs:\n{e}")
            self.log_message(f"Erro ao salvar logs: {e}")
    
    def update_status(self, message, color='blue'):
        """
        Atualiza o label de status
        """
        self.status_label.config(text=message, foreground=color)
        self.root.update_idletasks()
    
    def validate_inputs(self):
        """
        Valida os campos de entrada
        """
        if not self.email_var.get().strip():
            messagebox.showerror("Erro", "Por favor, insira seu e-mail.")
            return False
        
        if not self.password_var.get().strip():
            messagebox.showerror("Erro", "Por favor, insira sua senha.")
            return False
        
        if not self.use_recommendations_var.get() and not self.keywords_var.get().strip():
            messagebox.showerror("Erro", "Por favor, insira palavras-chave para busca ou ative as recomendações.")
            return False
        
        return True
    
    def test_browser(self):
        """
        Testa se o Playwright está funcionando
        """
        self.log_message("🧪 Testando Playwright...")
        self.update_status("Testando navegador...", 'orange')
        
        def run_test():
            try:
                import asyncio
                from playwright.async_api import async_playwright
                
                async def test():
                    playwright = await async_playwright().start()
                    browser = await playwright.chromium.launch(headless=self.headless_var.get())
                    page = await browser.new_page()
                    await page.goto("https://www.google.com")
                    title = await page.title()
                    await browser.close()
                    await playwright.stop()
                    return "Google" in title
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(test())
                
                if success:
                    self.log_message("✅ Playwright funcionando perfeitamente!")
                    self.update_status("Navegador OK - Pronto para automação", 'green')
                    messagebox.showinfo("Sucesso", "Playwright está funcionando corretamente!\nSistema pronto para automação inteligente.")
                else:
                    raise Exception("Falha no teste")
                    
            except Exception as e:
                self.log_message(f"❌ Erro no teste: {e}")
                self.update_status("Erro no navegador", 'red')
                messagebox.showerror("Erro", f"Erro ao testar Playwright:\n{e}\n\nInstale com:\npip install playwright\nplaywright install")
        
        Thread(target=run_test, daemon=True).start()
    
    def start_automation(self):
        """
        Inicia a automação em uma thread separada
        """
        if not self.validate_inputs():
            return
        
        if self.is_running:
            messagebox.showwarning("Aviso", "A automação já está em execução!")
            return
        
        # Atualiza interface
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.test_button.config(state='disabled')
        self.progress.start()
        self.update_status("Executando automação inteligente...", 'green')
        
        # Limpa os logs
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        # Inicia automação em thread separada
        self.automation_thread = Thread(target=self.run_automation, daemon=True)
        self.automation_thread.start()
    
    def run_automation(self):
        """
        Executa a automação
        """
        try:
            # Cria instância da automação
            self.automation = LinkedInAutomation(
                email=self.email_var.get(),
                password=self.password_var.get(),
                keywords=self.keywords_var.get(),
                location=self.location_var.get(),
                experience_level=self.experience_level_var.get(),
                work_type=self.work_type_var.get(),
                contract_type=self.contract_type_var.get(),
                apply_filters=self.apply_filters_var.get(),
                max_jobs=int(self.max_jobs_var.get()),
                delay=int(self.delay_var.get()),
                log_callback=self.log_message,
                # Novos parâmetros para filtragem inteligente
                user_skills=self.user_skills_var.get(),
                avoid_terms=self.avoid_terms_var.get(),
                use_recommendations=self.use_recommendations_var.get()
            )
            
            # Executa a automação
            result = self.automation.run()
            
            if result:
                self.update_status("Automação concluída com sucesso!", 'green')
                self.log_message("🎉 Automação finalizada com sucesso!")
            else:
                self.update_status("Automação falhou", 'red')
                self.log_message("❌ Automação falhou")
            
        except Exception as e:
            self.log_message(f"❌ Erro na automação: {e}")
            self.update_status("Erro na automação", 'red')
            messagebox.showerror("Erro", f"Erro durante a automação:\n{e}")
        finally:
            # Finaliza a automação
            self.finish_automation()
    
    def stop_automation(self):
        """
        Para a automação
        """
        if self.automation:
            self.automation.stop()
        self.log_message("⏹️ Parando automação...")
        self.update_status("Parando...", 'orange')
        self.finish_automation()
    
    def finish_automation(self):
        """
        Finaliza a automação e atualiza a interface
        """
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.test_button.config(state='normal')
        self.progress.stop()
        
        if not self.automation or not self.is_running:
            self.update_status("Pronto para iniciar automação inteligente", 'blue')
        
        if self.automation:
            self.automation.quit()
            self.automation = None
    
    def run(self):
        """
        Inicia o loop principal da interface
        """
        self.log_message("🚀 LinkedIn Job Automation Tool - Smart Edition iniciado!")
        self.log_message("🎯 Sistema de filtragem inteligente ativado")
        self.log_message("✅ Compatível com Chrome 140+ sem ChromeDriver")
        self.log_message("💡 Configure seu perfil e clique em 'Testar Navegador' primeiro")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            if self.automation:
                self.automation.quit()