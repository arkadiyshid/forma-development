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
   "77:01:0001043:3003", 
    "77:01:0001043:3114", 
    "77:01:0001043:3225", 
    "77:01:0001043:3246", 
    "77:01:0001043:3257", 
    "77:01:0001043:3268", 
    "77:01:0001043:3279", 
    "77:01:0001043:3290", 
    "77:01:0001043:2893", 
    "77:01:0001043:2904", 
    "77:01:0001043:2926", 
    "77:01:0001043:2937", 
    "77:01:0001043:2948", 
    "77:01:0001043:2959", 
    "77:01:0001043:2970", 
    "77:01:0001043:2981", 
    "77:01:0001043:2992", 
    "77:01:0001043:3004", 
    "77:01:0001043:3015", 
    "77:01:0001043:3026", 
    "77:01:0001043:3037", 
    "77:01:0001043:3048", 
    "77:01:0001043:3059", 
    "77:01:0001043:3070", 
    "77:01:0001043:3081", 
    "77:01:0001043:3092", 
    "77:01:0001043:3103", 
    "77:01:0001043:3115", 
    "77:01:0001043:3126", 
    "77:01:0001043:3137", 
    "77:01:0001043:3148", 
    "77:01:0001043:3159", 
    "77:01:0001043:3170", 
    "77:01:0001043:3181", 
    "77:01:0001043:3192", 
    "77:01:0001043:3203", 
    "77:01:0001043:3214", 
    "77:01:0001043:3226", 
    "77:01:0001043:3237", 
    "77:01:0001043:3238", 
    "77:01:0001043:3240", 
    "77:01:0001043:3241", 
    "77:01:0001043:3242", 
    "77:01:0001043:3243", 
    "77:01:0001043:3244", 
    "77:01:0001043:3245", 
    "77:01:0001043:3247", 
    "77:01:0001043:3248", 
    "77:01:0001043:3249", 
    "77:01:0001043:3250", 
    "77:01:0001043:3251", 
    "77:01:0001043:3252", 
    "77:01:0001043:3253", 
    "77:01:0001043:3254", 
    "77:01:0001043:3255", 
    "77:01:0001043:3256", 
    "77:01:0001043:3258", 
    "77:01:0001043:3259", 
    "77:01:0001043:3260", 
    "77:01:0001043:3261", 
    "77:01:0001043:3262", 
    "77:01:0001043:3263"
]
URL = "https://www.gosuslugi.ru/600359/1/form"
COOKIES_FILE = "cookies.pkl"
CHROMEDRIVER_PATH = '/Users/arkadijsidlovskij/Desktop/projects/PKK_FLAT_PARS/chromedriver'

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
        wait = WebDriverWait(driver, 3)
        start_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//button[.//span[contains(text(),"Начать")]]')
        ))
        start_button.click()

        time.sleep(1)

        # 2. Дальше остальные действия, подстраивай по структуре сайта
        info_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH,'//button[.//span[@class="answer-btn__title" and contains(text(), "Посмотреть основные сведения о недвижимости")]]')
            )
)
        info_button.click()

        time.sleep(1)

        # 3. Дальше кнопка квартира
        flat_button = wait.until(
             EC.element_to_be_clickable(
                (By.XPATH,'//button[.//span[@class="answer-btn__title" and contains(text(), "Квартира")]]')
            )

)
        flat_button.click()

        time.sleep(1)

        # 4. Дальше кнопка кадастровый номер
        cad_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH,'//button[.//span[@class="answer-btn__title" and contains(text(), "Кадастровый номер")]]')
            )
)
        cad_button.click()

        time.sleep(1)

        # Ввод кадастрового номера
        cad_input = wait.until(
        EC.presence_of_element_located((By.ID, "c_cadNumInput"))
    )
        cad_input.clear()
        cad_input.send_keys(kad_num)

        time.sleep(random.uniform(1.0, 1.5))

    # Нажимает кнопку "Продолжить"
        continue_btn = wait.until(
        EC.element_to_be_clickable((
            By.XPATH, '//span[contains(text(), "Продолжить")]/ancestor::button'
        ))
    )
        continue_btn.click()
        wait = WebDriverWait(driver, 2)
        result = {}

        label_xpath = lambda name: f'//div[@role="presentation" and normalize-space(text())="{name}"]/parent::epgu-constructor-output-html/following-sibling::epgu-constructor-output-html[1]/div'
        fields = [
            ("Наименование", "Наименование"),
            ("Кадастровый номер", "Кадастровый номер"),
            ("Адрес (местоположение)", "Адрес"),
            ("Площадь, кв.м", "Площадь"),
            ("Назначение", "Назначение"),
            ("Вид жилого помещения", "Вид_жилого_помещения"),
            ("Этаж", "Этаж"),
            ("Кадастровая стоимость (руб.)", "Кадастровая_стоимость"),
            ("Вид права, номер и дата регистрации", "Вид_права"),
            ("Ограничение прав и обременение объекта недвижимости", "Обременения"),
        ]

        for field, field_key in fields:
            try:
                elem = wait.until(
                    EC.visibility_of_element_located((By.XPATH, label_xpath(field)))
                )
                value = elem.text.strip()
                # Для кадастрового номера убираем все после \n (если есть "Подробнее" и т.д.)
                if field == "Кадастровый номер":
                    value = value.split('\n')[0].strip()
                result[field_key] = value
            except Exception as e:
                result[field_key] = "—"

        # Печать
        print(f"\n--- Результаты для {kad_num} ---")
        for k, v in result.items():
            print(f"{k}: {v}")
        print("--- Конец ---\n")

        # Запись в файл
        with open("result.txt", "a", encoding="utf-8") as f:
            f.write(f"Кадастровый номер запроса: {kad_num}\n")
            for k, v in result.items():
                f.write(f"{k}: {v}\n")
            f.write("-" * 30 + "\n")

        return {"kad_num": kad_num, "info": [f"{k}: {v}" for k, v in result.items()]}
    except Exception as e:
        print(f"ERROR: {e}")
        return {"kad_num": kad_num, "info": [], "error": str(e)}

# Пример вызова:
# parse_other_site(driver, "КАДАСТРОВЫЙ_НОМЕР")

# --- АВТОРИЗАЦИЯ (Реальный вход или куки) ---
authorise_if_needed()

results = []

# --- ГЛАВНОЙ ЦИКЛ ---
for kad in KAD_NUMBERS:
    result = parse_kadaster(kad)
    results.append(result)
    time.sleep(random.uniform(1.0, 1.5))

# --- Запись результата ---
with open("results.txt", "w", encoding="utf-8") as f:
    for res in results:
        f.write(f"Кадастровый номер: {res['kad_num']}\n")
        for line in res["info"]:
            f.write(f"{line}\n")
        f.write("-" * 25 + "\n")
print("Готово! Данные сохранены в results.txt")

# driver.quit()  # раскомментируй, если хочешь закрывать браузер