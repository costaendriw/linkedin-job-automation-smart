"""
LinkedIn Job Automation Tool - Smart Edition
Aplicação principal com filtragem inteligente e compatibilidade Chrome 140+

Desenvolvido com Playwright para máxima performance e compatibilidade
"""

import sys
import os
import subprocess

# Adiciona o diretório src ao path para importar os módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

def check_playwright_installation():
    """
    Verifica se o Playwright está instalado e configurado
    """
    try:
        import playwright
        print("✅ Playwright importado com sucesso")
        return True
    except ImportError:
        print("❌ Playwright não encontrado!")
        print("📥 Instale com: pip install playwright")
        return False

def install_playwright_browsers():
    """
    Instala os navegadores do Playwright se necessário
    """
    try:
        print("🔍 Verificando instalação dos navegadores...")
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Navegadores do Playwright instalados/atualizados")
            return True
        else:
            print(f"❌ Erro ao instalar navegadores: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout na instalação - pode estar demorando mais que o esperado")
        return False
    except Exception as e:
        print(f"❌ Erro na instalação: {e}")
        return False

def main():
    """
    Função principal que inicia a aplicação
    """
    print("=" * 70)
    print("🚀 LinkedIn Job Automation Tool - Smart Edition")
    print("=" * 70)
    print("🎯 Sistema de filtragem inteligente baseado no seu perfil")
    print("✅ Compatível com Chrome 140+ (sem ChromeDriver)")
    print("⚡ Powered by Playwright para máxima performance")
    print("-" * 70)
    
    # Verificar instalação do Playwright
    if not check_playwright_installation():
        print("\n🔧 Para instalar o Playwright:")
        print("   pip install playwright")
        print("   playwright install")
        input("\n⏸️ Pressione Enter para continuar mesmo assim...")
    
    try:
        # Tentar instalar/atualizar navegadores automaticamente
        print("\n🔧 Configurando navegadores...")
        if not install_playwright_browsers():
            print("⚠️ Navegadores podem não estar atualizados")
            print("💡 Execute manualmente: playwright install")
        
        print("\n🎨 Iniciando interface gráfica...")
        
        # Importar e executar a GUI
        from gui import LinkedInGUI
        
        # Criar e executar a interface gráfica
        app = LinkedInGUI()
        app.run()
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("\n🔧 Soluções possíveis:")
        print("   1. Verifique se todos os arquivos estão na pasta 'src/'")
        print("   2. Instale as dependências: pip install -r requirements.txt")
        print("   3. Execute: playwright install")
        input("\n⏸️ Pressione Enter para sair...")
        
    except Exception as e:
        print(f"❌ Erro ao iniciar a aplicação: {e}")
        print("\n🐛 Informações de debug:")
        print(f"   Python: {sys.version}")
        print(f"   Diretório atual: {current_dir}")
        print(f"   Path do src: {src_path}")
        
        # Listar arquivos para debug
        if os.path.exists(src_path):
            files = os.listdir(src_path)
            print(f"   Arquivos em src/: {files}")
        else:
            print("   ❌ Pasta src/ não encontrada!")
        
        input("\n⏸️ Pressione Enter para sair...")

def check_system_requirements():
    """
    Verifica requisitos do sistema
    """
    print("🔍 Verificando requisitos do sistema...")
    
    # Verificar versão do Python
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python {python_version.major}.{python_version.minor} (OK)")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} (requer 3.8+)")
        return False
    
    # Verificar importações básicas
    try:
        import tkinter
        print("✅ Tkinter disponível")
    except ImportError:
        print("❌ Tkinter não disponível")
        return False
    
    try:
        import asyncio
        print("✅ Asyncio disponível")
    except ImportError:
        print("❌ Asyncio não disponível")
        return False
    
    return True

def show_features():
    """
    Mostra as principais funcionalidades do sistema
    """
    print("\n🎯 FUNCIONALIDADES PRINCIPAIS:")
    print("   • Filtragem inteligente baseada no seu perfil LinkedIn")
    print("   • Aproveitamento das recomendações automáticas do LinkedIn")  
    print("   • Sistema de compatibilidade avançado com suas skills")
    print("   • Filtros por experiência, modalidade e tipo de contrato")
    print("   • Anti-detecção nativo para máxima segurança")
    print("   • Interface gráfica intuitiva com logs em tempo real")
    print("   • Salvamento automático de logs e estatísticas")

if __name__ == "__main__":
    try:
        # Verificar requisitos do sistema
        if not check_system_requirements():
            print("\n❌ Requisitos do sistema não atendidos")
            input("⏸️ Pressione Enter para sair...")
            sys.exit(1)
        
        # Mostrar funcionalidades
        show_features()
        
        # Executar aplicação principal
        main()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Aplicação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        input("⏸️ Pressione Enter para sair...")
    finally:
        print("\n👋 Encerrando aplicação...")
        print("🎯 Obrigado por usar o LinkedIn Job Automation - Smart Edition!")