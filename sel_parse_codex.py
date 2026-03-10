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
RESULT_READY_WAIT = 10
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
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
    short_pause()
    try:
        button.click()
    except Exception:
        driver.execute_script("arguments[0].click();", button)
    return button


def wait_for_cad_input(timeout=DEFAULT_WAIT):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.ID, "c_cadNumInput"))
    )


def label_xpath(name):
    return (
        f'//div[@role="presentation" and normalize-space(text())="{name}"]'
        '/parent::epgu-constructor-output-html/'
        'following-sibling::epgu-constructor-output-html[1]/div'
    )


def wait_for_result_card(timeout=RESULT_READY_WAIT):
    WebDriverWait(driver, timeout).until(
        EC.any_of(
            EC.visibility_of_element_located((By.XPATH, label_xpath("Кадастровый номер"))),
            EC.visibility_of_element_located((By.XPATH, label_xpath("Адрес (местоположение)"))),
        )
    )


def extract_field_value(field_name):
    elements = driver.find_elements(By.XPATH, label_xpath(field_name))
    if not elements:
        return "—"

    value = elements[0].text.strip()
    if not value:
        return "—"
    if field_name == "Кадастровый номер":
        return value.split('\n')[0].strip() or "—"
    return value

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
    print("[INFO] Пытаюсь нажать кнопку 'Назад' тем же способом, что и остальные кнопки.")
    back_button = click_button_by_text("Назад", timeout=5)

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
    print(f"[STEP] Начинаю обработку {kad_num}", flush=True)
    ensure_search_form_ready()
    try:
        cad_input = wait_for_cad_input(timeout=5)
        cad_input.clear()
        cad_input.send_keys(kad_num)
        typing_pause()
        print(f"[STEP] Номер {kad_num} введен, нажимаю 'Продолжить'", flush=True)
        continue_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((
                By.XPATH, '//span[contains(text(), "Продолжить")]/ancestor::button'
            ))
        )
        continue_btn.click()
        print(f"[STEP] Клик по 'Продолжить' выполнен для {kad_num}", flush=True)
        result = {}
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

        wait_for_result_card()

        for field, field_key in fields:
            result[field_key] = extract_field_value(field)

        # Печать
        print(f"\n--- Результаты для {kad_num} ---")
        for k, v in result.items():
            print(f"{k}: {v}")
        print("--- Конец ---\n")

        return {"kad_num": kad_num, "info": [f"{k}: {v}" for k, v in result.items()]}
    except Exception as e:
        print(f"[ERROR] {kad_num}: {e}", flush=True)
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


script_start = time.perf_counter()
# --- ГЛАВНОЙ ЦИКЛ ---
for index, kad in enumerate(KAD_NUMBERS):
    result = None
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[STEP] Цикл: {kad}, попытка {attempt}/{MAX_RETRIES}", flush=True)
        result = parse_kadaster(kad)
        if not result.get("error"):
            print(f"[STEP] Парсинг завершен для {kad}, пишу в файл", flush=True)
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
            print(f"[STEP] Переход к следующему номеру после {kad}", flush=True)
            return_to_search_form()
            short_pause()
        except Exception:
            print(f"[WARN] Возврат к форме не удался после {kad}, пробую восстановить форму", flush=True)
            ensure_search_form_ready()

print(f"Готово! Данные сохранены в {OUTPUT_FILE}")

elapsed = time.perf_counter() - script_start
minutes, seconds = divmod(elapsed, 60)
print(f"Время выполнения: {int(minutes)} мин {seconds:.1f} сек.")
# driver.quit()  # раскомментируй, если хочешь закрывать браузер
