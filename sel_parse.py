import os
import time
import pickle
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# === НАСТРОЙКИ ===
KAD_NUMBERS = [ # впиши свои данные
    "77:01:0002021:5673",
    "77:01:0002009:4870"
]
URL = "https://www.gosuslugi.ru/600359/1/form"
COOKIES_FILE = "cookies.pkl"
CHROMEDRIVER_PATH = r'C:\Users\shidlovskiyaf\projects\PKK_FLAT_PARS\chromedriver.exe'

service = Service(executable_path=CHROMEDRIVER_PATH)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30)

def save_cookies():
    with open(COOKIES_FILE, "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("[INFO] Cookies сохранены в 'cookies.pkl'.")

def load_cookies():
    with open(COOKIES_FILE, "rb") as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print("Cookie load error:", e)
    driver.refresh()
    time.sleep(2)

def authorise_if_needed():
    driver.get(URL)
    if os.path.exists(COOKIES_FILE):
        load_cookies()
        print("[INFO] Загружены cookies — работаем авторизовано!")
    else:
        print("\n" + "=" * 50)
        print("[ACTION] Авторизуйтесь на сайте в ОТКРЫВШЕМСЯ ОКНЕ БРАУЗЕРА (и решите капчу, если нужно)!")
        input("Когда авторизация завершена, нажмите [Enter] в терминале...")
        save_cookies()

def close_error_and_retry():
    try:
        # Ловим окно ошибки
        error_block = WebDriverWait(driver, 1.5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "rros-ui-lib-error-message"))
        )
        print("[INFO] Найдено окно ошибки антибота — пробуем закрыть и повторить поиск.")
        time.sleep(2)
        try:
            # Крестик-кнопка прямо после error_message (чаще всего внутри error-title)
            # Если не найдёт — ищет по всему driver внутри блока ошибки
            cross = None
            # Сперва ищет внутри "error-title" — нужен только первый крестик
            try:
                cross = error_block.find_element(By.XPATH,
                    "../../button[contains(@class, 'rros-ui-lib-button--link')]") # родитель/сосед
            except:
                # Крестик как вложенная кнопка после error_message
                parent = error_block.find_element(By.XPATH, "../..") # rros-ui-lib-error-title
                cross = parent.find_element(By.CSS_SELECTOR, ".rros-ui-lib-button.rros-ui-lib-button--link")
            if not cross:
                # Просто ищем по всей error_title на всякий случай
                cross = driver.find_element(By.CSS_SELECTOR, ".rros-ui-lib-error-title .rros-ui-lib-button.rros-ui-lib-button--link")
            cross.click()
            print("[INFO] Крестик кликнут!")
            time.sleep(1)
        except Exception as e:
            print("[WARN] Не удалось кликнуть крестик:", e)
        # Повтор поиска
        try:
            search_button = driver.find_element(By.ID, "realestateobjects-search")
            search_button.click()

            
            # close_error_and_retry()
            print("[INFO] Повторный поиск запущен; пауза 30-60 секунд для обхода антибота.")
            time.sleep(random.uniform(30.0, 60.0))
            driver.get("https://lk.rosreestr.ru/eservices/")
            time.sleep(2)
            parse_kadaster(kad)
        except Exception as e:
            print("[ERROR] Не удалось повторно нажать поиск:", e)
    except TimeoutException:
        pass  # Окна ошибки нет — всё ок

def parse_kadaster(kad_num):
    driver.get(URL)
    try:
        # 1. НАЖАТЬ НА КНОПКУ "Начать"
        wait = WebDriverWait(driver, 5)
        start_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//button[.//span[contains(text(),"Начать")]]')
        ))
        start_button.click()

        time.sleep(2)

        # 2. Дальше остальные действия, подстраивай по структуре сайта
        info_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH,'//button[.//span[@class="answer-btn__title" and contains(text(), "Посмотреть основные сведения о недвижимости")]]')
            )
)
        info_button.click()

        time.sleep(2)

        # 3. Дальше кнопка квартира
        flat_button = wait.until(
             EC.element_to_be_clickable(
                (By.XPATH,'//button[.//span[@class="answer-btn__title" and contains(text(), "Квартира")]]')
            )

)
        flat_button.click()

        time.sleep(2)

        # 4. Дальше кнопка кадастровый номер
        cad_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH,'//button[.//span[@class="answer-btn__title" and contains(text(), "Кадастровый номер")]]')
            )
)
        cad_button.click()

        time.sleep(2)

        # Ввод кадастрового номера
        cad_input = wait.until(
        EC.presence_of_element_located((By.ID, "c_cadNumInput"))
    )
        cad_input.clear()
        cad_input.send_keys(kad_num)

        time.sleep(random.uniform(3.5, 5.2))

    # Нажимает кнопку "Продолжить"
        continue_btn = wait.until(
        EC.element_to_be_clickable((
            By.XPATH, '//span[contains(text(), "Продолжить")]/ancestor::button'
        ))
    )
        continue_btn.click()
    
    # ... следующий шаг

# ПРИМЕЧАНИЕ:
# Вся цепочка кликов и вводов должна вызываться последовательно, 
# между действиями иногда стоит поставить time.sleep(0.5) — если страница не сразу реагирует.

        # Здесь твой дальнейший код

        return {}
    except Exception as e:
        print(f"ERROR: {e}")
        return {}

# Пример вызова:
# parse_other_site(driver, "КАДАСТРОВЫЙ_НОМЕР")

# --- АВТОРИЗАЦИЯ (Реальный вход или куки) ---
authorise_if_needed()

results = []

# --- ГЛАВНОЙ ЦИКЛ ---
for kad in KAD_NUMBERS:
    result = parse_kadaster(kad)
    results.append(result)
    time.sleep(random.uniform(1.5, 2.5))

# --- Запись результата ---
with open("results.txt", "w", encoding="utf-8") as f:
    for res in results:
        f.write(f"Кадастровый номер: {res['kad_num']}\n")
        for line in res["info"]:
            f.write(f"{line}\n")
        f.write("-" * 25 + "\n")
print("Готово! Данные сохранены в results.txt")

# driver.quit()  # раскомментируй, если хочешь закрывать браузер