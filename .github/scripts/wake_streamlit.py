"""Ouvre l'application Streamlit dans un vrai navigateur pour la garder éveillée.

Une simple requête HTTP ne suffit pas sur Streamlit Community Cloud : l'URL
redirige via un cookie (boucle de redirections pour curl) et une appli endormie
n'est relancée qu'en cliquant sur « Yes, get this app back up! ». On ouvre donc
la page avec Chromium, on clique sur ce bouton s'il apparaît, puis on attend
que l'interface Streamlit soit réellement chargée.
"""

import os
import re
import sys
import time

from playwright.sync_api import sync_playwright

URL = sys.argv[1]
WAKE_BUTTON = re.compile(r"get this app back up|wake .*up", re.IGNORECASE)
APP_SELECTOR = '[data-testid="stApp"], [data-testid="stAppViewContainer"]'
TIMEOUT_S = 300


def app_loaded(page):
    for frame in page.frames:
        try:
            if frame.locator(APP_SELECTOR).count():
                return True
        except Exception:
            pass
    return False


def click_wake_button(page):
    for frame in page.frames:
        try:
            button = frame.get_by_role("button", name=WAKE_BUTTON)
            if button.count():
                button.first.click()
                return True
        except Exception:
            pass
    return False


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
    page = browser.new_page(viewport={"width": 1366, "height": 900})
    print(f"Ouverture de {URL}")
    page.goto(URL, wait_until="domcontentloaded", timeout=120_000)

    woken = False
    deadline = time.time() + TIMEOUT_S
    while time.time() < deadline:
        if app_loaded(page):
            break
        if not woken and click_wake_button(page):
            woken = True
            print("L'application dormait : réveil demandé.")
        page.wait_for_timeout(5_000)
    else:
        page.screenshot(path="etat-application.png", full_page=True)
        print(f"Échec : l'interface Streamlit n'est pas chargée après {TIMEOUT_S} s.")
        sys.exit(1)

    # Rester quelques secondes connecté pour que la visite compte comme activité.
    page.wait_for_timeout(20_000)
    print("Succès : application chargée" + (" après réveil." if woken else ", elle était déjà éveillée."))
    browser.close()
