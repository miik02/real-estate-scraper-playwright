from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import pandas as pd
import time

def prueba():
    with Stealth().use_sync(sync_playwright()) as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="./perfil_bot", # Carpeta donde se guarda el rastro humano
            channel="chrome",             # Obliga a usar tu Google Chrome real instalado, no Chromium
            headless=False,
            slow_mo=100,                  # Lo ralentizamos más para no asustar al servidor
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = context.pages[0]

        # 2. Navegamos a la URL
        print("Entrando en la web...")
        page.goto("https://www.idealista.com")
        time.sleep(3)

        page.goto("https://www.idealista.com/geo/venta-viviendas/metro-las-rosas/")
        time.sleep(3)
        casas = page.locator("article:not(.adv)")
        print(f"Casas totales enconradas: {casas.count()}")
        print(f"Procedemos a buscar casas de particulares")
        casas_particulares = []


        for i in range (casas.count()):

            casa_actual = casas.nth(i)
            logo = casa_actual.locator(".logo-branding")

            if logo.count() == 0:
                nombre = casa_actual.locator(".item-link")
                precio = casa_actual.locator(".price-row")
                items = casa_actual.locator(".item-detail")
                link = "https://www.idealista.com" + nombre.get_attribute("href")
            
                casas_particulares.append({
                    "Nombre": nombre.inner_text(),
                    "Precio": precio.inner_text().split("\n")[0].strip(),
                    "Caraceristicas": ", ".join([texto.strip() for texto in items.all_inner_texts()]),
                    "Enlace": link
                })

        print(len(casas_particulares))
        print(casas_particulares)
        return casas_particulares

datos = prueba()

df = pd.DataFrame(datos)
df.to_csv("Data/Casas_particulares.csv")