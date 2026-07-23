import os
import time

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), '..'))
IMAGES_DIR = os.path.join(PROJECT_ROOT, 'docs', 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

def capture_with_playwright():
    print("Intentando capturar con Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Capturar Dashboard
        print("Navegando a Dashboard...")
        page.goto('http://localhost:3000/dashboard')
        time.sleep(5)  # Esperar que carguen las animaciones de los gráficos
        dashboard_path = os.path.join(IMAGES_DIR, 'dashboard_real.png')
        page.screenshot(path=dashboard_path)
        print(f"OK Dashboard guardado en: {dashboard_path}")
        
        # Capturar Panel Principal / Home (para image3.png)
        print("Navegando a Home...")
        page.goto('http://localhost:3000/')
        time.sleep(3)
        home_path = os.path.join(IMAGES_DIR, 'home_real.png')
        page.screenshot(path=home_path)
        print(f"OK Home guardado en: {home_path}")
        
        browser.close()

def capture_with_selenium():
    print("Intentando capturar con Selenium...")
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        # Capturar Dashboard
        print("Navegando a Dashboard...")
        driver.get('http://localhost:3000/dashboard')
        time.sleep(5)
        dashboard_path = os.path.join(IMAGES_DIR, 'dashboard_real.png')
        driver.save_screenshot(dashboard_path)
        print(f"OK Dashboard guardado en: {dashboard_path}")
        
        # Capturar Home
        print("Navegando a Home...")
        driver.get('http://localhost:3000/')
        time.sleep(3)
        home_path = os.path.join(IMAGES_DIR, 'home_real.png')
        driver.save_screenshot(home_path)
        print(f"OK Home guardado en: {home_path}")
    finally:
        driver.quit()

if __name__ == '__main__':
    if HAS_PLAYWRIGHT:
        try:
            capture_with_playwright()
        except Exception as e:
            print(f"Error con Playwright: {e}")
            if HAS_SELENIUM:
                capture_with_selenium()
            else:
                print("No hay Selenium disponible para fallback.")
    elif HAS_SELENIUM:
        try:
            capture_with_selenium()
        except Exception as e:
            print(f"Error con Selenium: {e}")
    else:
        print("Error: No está instalado Playwright ni Selenium en el entorno de Python local.")
        print("Instale uno de ellos para capturar la pantalla automáticamente.")
