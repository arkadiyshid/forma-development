import os
import time
import pickle
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# === НАСТРОЙКИ ===
KAD_NUMBERS = [ # впиши свои данные 
    "77:01:0001043:3003", 
    "77:01:0001043:3114", 
    "77:01:0001043:3225", 
    "77:01:0001043:3246", 
    "77:01:0001043:3257", 
    "77:01:0001043:3268", 
    "77:01:0001043:3279"
]
URL = "https://www.gosuslugi.ru/600359/1/form"
COOKIES_FILE = "cookies.pkl"
CHROMEDRIVER_PATH = '/Users/arkadijsidlovskij/Desktop/projects/PKK_FLAT_PARS/chromedriver'
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    f"result_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
)
DEFAULT_WAIT = 15
SHORT_PAUSE_RANGE = (0.15, 0.35)
TYPE_PAUSE_RANGE = (0.4, 0.8)
RETRY_DELAY_RANGE = (3.0, 6.0)
MAX_RETRIES = 2

service = Service(executable_path=CHROMEDRIVER_PATH)
options = webdriver.ChromeOptions()
options.add_experimental_option(
    "prefs",
    {
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.images": 2,
    }
)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, DEFAULT_WAIT)


def short_pause():
    time.sleep(random.uniform(*SHORT_PAUSE_RANGE))


def typing_pause():
    time.sleep(random.uniform(*TYPE_PAUSE_RANGE))


def retry_pause():
    time.sleep(random.uniform(*RETRY_DELAY_RANGE))


def click_button_by_text(text, timeout=DEFAULT_WAIT):
    button = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                f'//button[.//span[contains(normalize-space(), "{text}")]]'
            )
        )
    )
    button.click()
    return button


def wait_for_cad_input(timeout=DEFAULT_WAIT):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.ID, "c_cadNumInput"))
    )

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

def handle_antibot_error():
    try:
        error_block = WebDriverWait(driver, 1.5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "rros-ui-lib-error-message"))
        )
        print("[INFO] Найдено окно ошибки антибота — пробуем закрыть и повторить поиск.")
        try:
            cross = None
            try:
                cross = error_block.find_element(By.XPATH,
                    "../../button[contains(@class, 'rros-ui-lib-button--link')]")
            except Exception:
                parent = error_block.find_element(By.XPATH, "../..")
                cross = parent.find_element(By.CSS_SELECTOR, ".rros-ui-lib-button.rros-ui-lib-button--link")
            if not cross:
                cross = driver.find_element(By.CSS_SELECTOR, ".rros-ui-lib-error-title .rros-ui-lib-button.rros-ui-lib-button--link")
            cross.click()
            print("[INFO] Крестик кликнут!")
        except Exception as e:
            print("[WARN] Не удалось кликнуть крестик:", e)
        return True
    except TimeoutException:
        return False


def open_cadaster_search_form():
    driver.get(URL)
    click_button_by_text("Начать", timeout=5)
    click_button_by_text("Посмотреть основные сведения о недвижимости")
    click_button_by_text("Квартира")
    click_button_by_text("Кадастровый номер")
    wait_for_cad_input()


def ensure_search_form_ready():
    try:
        wait_for_cad_input(timeout=2)
    except TimeoutException:
        open_cadaster_search_form()


def return_to_search_form():
    prev_button_selector = 'epgu-cf-ui-prev-button button[name="prev"]'
    selectors = [
        (By.CSS_SELECTOR, prev_button_selector),
        (By.XPATH, '//button[@name="prev" and .//span[normalize-space()="Назад"]]'),
        (By.CSS_SELECTOR, 'button[name="prev"]'),
        (By.XPATH, '//button[.//span[normalize-space()="Назад"]]'),
    ]

    print("[INFO] Пытаюсь найти кнопку 'Назад'.")
    print(
        "[DEBUG] Кнопок через CSS epgu-cf-ui-prev-button button[name='prev']: "
        f"{len(driver.find_elements(By.CSS_SELECTOR, prev_button_selector))}"
    )

    back_button = None
    for by, selector in selectors:
        try:
            back_button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((by, selector))
            )
            print(f"[INFO] Кнопка 'Назад' найдена через {by}: {selector}")
            break
        except TimeoutException:
            continue

    if back_button is None:
        raise TimeoutException("Кнопка 'Назад' не найдена")

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", back_button)
    short_pause()
    try:
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, prev_button_selector)))
        back_button.click()
        print("[INFO] Клик по 'Назад' выполнен обычным click().")
    except Exception:
        driver.execute_script(
            """
            const btn = document.querySelector('epgu-cf-ui-prev-button button[name="prev"]')
                || document.querySelector('button[name="prev"]');
            if (btn) { btn.click(); }
            """,
        )
        print("[INFO] Клик по 'Назад' выполнен через JS.")

    try:
        WebDriverWait(driver, 5).until(EC.staleness_of(back_button))
    except (TimeoutException, StaleElementReferenceException):
        pass

    try:
        cad_input = wait_for_cad_input(timeout=5)
        cad_input.clear()
        print("[INFO] После 'Назад' поле кадастрового номера снова доступно.")
        return cad_input
    except TimeoutException:
        print("[WARN] После клика 'Назад' поле не появилось, восстанавливаю форму заново.")
        open_cadaster_search_form()
        cad_input = wait_for_cad_input(timeout=5)
        cad_input.clear()
        return cad_input

def parse_kadaster(kad_num):
    ensure_search_form_ready()
    try:
        cad_input = wait_for_cad_input(timeout=5)
        cad_input.clear()
        cad_input.send_keys(kad_num)
        typing_pause()
        continue_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((
                By.XPATH, '//span[contains(text(), "Продолжить")]/ancestor::button'
            ))
        )
        continue_btn.click()
        wait = WebDriverWait(driver, DEFAULT_WAIT)
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

        if handle_antibot_error():
            raise RuntimeError("Антибот временно заблокировал запрос")

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

        return {"kad_num": kad_num, "info": [f"{k}: {v}" for k, v in result.items()]}
    except Exception as e:
        print(f"ERROR: {e}")
        return {"kad_num": kad_num, "info": [], "error": str(e)}

# Пример вызова:
# parse_other_site(driver, "КАДАСТРОВЫЙ_НОМЕР")

# --- АВТОРИЗАЦИЯ (Реальный вход или куки) ---
authorise_if_needed()
open_cadaster_search_form()

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(f"Результаты запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 40 + "\n")

# --- ГЛАВНОЙ ЦИКЛ ---
for index, kad in enumerate(KAD_NUMBERS):
    result = None
    for attempt in range(1, MAX_RETRIES + 1):
        result = parse_kadaster(kad)
        if not result.get("error"):
            break
        print(f"[WARN] Ошибка для {kad}, попытка {attempt} из {MAX_RETRIES}.")
        retry_pause()
        ensure_search_form_ready()

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"Кадастровый номер: {result['kad_num']}\n")
        for line in result["info"]:
            f.write(f"{line}\n")
        if result.get("error"):
            f.write(f"ERROR: {result['error']}\n")
        f.write("-" * 25 + "\n")
    if index < len(KAD_NUMBERS) - 1:
        try:
            return_to_search_form()
            short_pause()
        except Exception:
            ensure_search_form_ready()

print(f"Готово! Данные сохранены в {OUTPUT_FILE}")

# driver.quit()  # раскомментируй, если хочешь закрывать браузер
