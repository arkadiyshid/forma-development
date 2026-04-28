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
    "77:01:0003041:6341", 
    "77:01:0003041:6452", 
    "77:01:0003041:6563", 
    "77:01:0003041:6675", 
    "77:01:0003041:6786", 
    "77:01:0003041:6896", 
    "77:01:0003041:6918", 
    "77:01:0003041:6231", 
    "77:01:0003041:6242", 
    "77:01:0003041:6253", 
    "77:01:0003041:6264", 
    "77:01:0003041:6275", 
    "77:01:0003041:6286", 
    "77:01:0003041:6297", 
    "77:01:0003041:6308", 
    "77:01:0003041:6319", 
    "77:01:0003041:6330", 
    "77:01:0003041:6342", 
    "77:01:0003041:6353", 
    "77:01:0003041:6364", 
    "77:01:0003041:6375", 
    "77:01:0003041:6386", 
    "77:01:0003041:6397", 
    "77:01:0003041:6408", 
    "77:01:0003041:6419", 
    "77:01:0003041:6430", 
    "77:01:0003041:6441", 
    "77:01:0003041:6453", 
    "77:01:0003041:6464", 
    "77:01:0003041:6475", 
    "77:01:0003041:6486", 
    "77:01:0003041:6497", 
    "77:01:0003041:6508", 
    "77:01:0003041:6519", 
    "77:01:0003041:6530", 
    "77:01:0003041:6541", 
    "77:01:0003041:6552", 
    "77:01:0003041:6564", 
    "77:01:0003041:6575", 
    "77:01:0003041:6586", 
    "77:01:0003041:6597", 
    "77:01:0003041:6608", 
    "77:01:0003041:6619", 
    "77:01:0003041:6630", 
    "77:01:0003041:6641", 
    "77:01:0003041:6652", 
    "77:01:0003041:6663", 
    "77:01:0003041:6676", 
    "77:01:0003041:6687", 
    "77:01:0003041:6698", 
    "77:01:0003041:6709", 
    "77:01:0003041:6720", 
    "77:01:0003041:6731", 
    "77:01:0003041:6742", 
    "77:01:0003041:6753", 
    "77:01:0003041:6764", 
    "77:01:0003041:6775", 
    "77:01:0003041:6787", 
    "77:01:0003041:6798", 
    "77:01:0003041:6809", 
    "77:01:0003041:6820", 
    "77:01:0003041:6831", 
    "77:01:0003041:6842", 
    "77:01:0003041:6853", 
    "77:01:0003041:6864", 
    "77:01:0003041:6875", 
    "77:01:0003041:6886", 
    "77:01:0003041:6897", 
    "77:01:0003041:6898", 
    "77:01:0003041:6899", 
    "77:01:0003041:6900", 
    "77:01:0003041:6901", 
    "77:01:0003041:6902", 
    "77:01:0003041:6903", 
    "77:01:0003041:6904", 
    "77:01:0003041:6905", 
    "77:01:0003041:6906", 
    "77:01:0003041:6908", 
    "77:01:0003041:6909", 
    "77:01:0003041:6910", 
    "77:01:0003041:6911", 
    "77:01:0003041:6912", 
    "77:01:0003041:6913", 
    "77:01:0003041:6914", 
    "77:01:0003041:6915", 
    "77:01:0003041:6916", 
    "77:01:0003041:6917", 
    "77:01:0003041:6919", 
    "77:01:0003041:6920", 
    "77:01:0003041:6921", 
    "77:01:0003041:6922", 
    "77:01:0003041:6923", 
    "77:01:0003041:6924", 
    "77:01:0003041:6925", 
    "77:01:0003041:6926", 
    "77:01:0003041:6927", 
    "77:01:0003041:6928", 
    "77:01:0003041:6232", 
    "77:01:0003041:6233", 
    "77:01:0003041:6234", 
    "77:01:0003041:6235", 
    "77:01:0003041:6236", 
    "77:01:0003041:6237", 
    "77:01:0003041:6238", 
    "77:01:0003041:6239", 
    "77:01:0003041:6240", 
    "77:01:0003041:6241", 
    "77:01:0003041:6243", 
    "77:01:0003041:6244", 
    "77:01:0003041:6245", 
    "77:01:0003041:6246", 
    "77:01:0003041:6247", 
    "77:01:0003041:6248", 
    "77:01:0003041:6249", 
    "77:01:0003041:6250", 
    "77:01:0003041:6251", 
    "77:01:0003041:6252", 
    "77:01:0003041:6254", 
    "77:01:0003041:6255", 
    "77:01:0003041:6256", 
    "77:01:0003041:6257", 
    "77:01:0003041:6258", 
    "77:01:0003041:6259", 
    "77:01:0003041:6260", 
    "77:01:0003041:6261", 
    "77:01:0003041:6262", 
    "77:01:0003041:6263", 
    "77:01:0003041:6265", 
    "77:01:0003041:6266", 
    "77:01:0003041:6267", 
    "77:01:0003041:6268", 
    "77:01:0003041:6269", 
    "77:01:0003041:6270", 
    "77:01:0003041:6271", 
    "77:01:0003041:6272", 
    "77:01:0003041:6273", 
    "77:01:0003041:6274", 
    "77:01:0003041:6276", 
    "77:01:0003041:6277", 
    "77:01:0003041:6278", 
    "77:01:0003041:6279", 
    "77:01:0003041:6280", 
    "77:01:0003041:6281", 
    "77:01:0003041:6282", 
    "77:01:0003041:6283", 
    "77:01:0003041:6284", 
    "77:01:0003041:6285", 
    "77:01:0003041:6287", 
    "77:01:0003041:6288", 
    "77:01:0003041:6289", 
    "77:01:0003041:6290", 
    "77:01:0003041:6291", 
    "77:01:0003041:6292", 
    "77:01:0003041:6293", 
    "77:01:0003041:6294", 
    "77:01:0003041:6295", 
    "77:01:0003041:6296", 
    "77:01:0003041:6298", 
    "77:01:0003041:6299", 
    "77:01:0003041:6300", 
    "77:01:0003041:6301", 
    "77:01:0003041:6302", 
    "77:01:0003041:6303", 
    "77:01:0003041:6304", 
    "77:01:0003041:6305", 
    "77:01:0003041:6306", 
    "77:01:0003041:6307", 
    "77:01:0003041:6309", 
    "77:01:0003041:6310", 
    "77:01:0003041:6311", 
    "77:01:0003041:6312", 
    "77:01:0003041:6313", 
    "77:01:0003041:6314", 
    "77:01:0003041:6315", 
    "77:01:0003041:6316", 
    "77:01:0003041:6317", 
    "77:01:0003041:6318", 
    "77:01:0003041:6320", 
    "77:01:0003041:6321", 
    "77:01:0003041:6322", 
    "77:01:0003041:6323", +
    "77:01:0003041:6324", 
    "77:01:0003041:6325", 
    "77:01:0003041:6326", 
    "77:01:0003041:6327", 
    "77:01:0003041:6328", 
    "77:01:0003041:6329", 
    "77:01:0003041:6331", 
    "77:01:0003041:6332", 
    "77:01:0003041:6333", 
    "77:01:0003041:6334", 
    "77:01:0003041:6335", 
    "77:01:0003041:6336", 
    "77:01:0003041:6337", 
    "77:01:0003041:6338", 
    "77:01:0003041:6339", 
    "77:01:0003041:6340", 
    "77:01:0003041:6343", 
    "77:01:0003041:6344", 
    "77:01:0003041:6345", 
    "77:01:0003041:6346", 
    "77:01:0003041:6347", 
    "77:01:0003041:6348", 
    "77:01:0003041:6349", 
    "77:01:0003041:6350", 
    "77:01:0003041:6351", 
    "77:01:0003041:6352", 
    "77:01:0003041:6354", 
    "77:01:0003041:6355", 
    "77:01:0003041:6356", 
    "77:01:0003041:6357", 
    "77:01:0003041:6358", 
    "77:01:0003041:6359", 
    "77:01:0003041:6360", 
    "77:01:0003041:6361", 
    "77:01:0003041:6362", 
    "77:01:0003041:6363", 
    "77:01:0003041:6365", 
    "77:01:0003041:6366", 
    "77:01:0003041:6367", 
    "77:01:0003041:6368", 
    "77:01:0003041:6369", 
    "77:01:0003041:6370", 
    "77:01:0003041:6371", 
    "77:01:0003041:6372", 
    "77:01:0003041:6373", 
    "77:01:0003041:6374", 
    "77:01:0003041:6376", 
    "77:01:0003041:6377", 
    "77:01:0003041:6378", 
    "77:01:0003041:6379", 
    "77:01:0003041:6380", 
    "77:01:0003041:6381", 
    "77:01:0003041:6382", 
    "77:01:0003041:6383", 
    "77:01:0003041:6384", 
    "77:01:0003041:6385", 
    "77:01:0003041:6387", 
    "77:01:0003041:6388", 
    "77:01:0003041:6389", 
    "77:01:0003041:6390", 
    "77:01:0003041:6391", 
    "77:01:0003041:6392", 
    "77:01:0003041:6393", 
    "77:01:0003041:6394", 
    "77:01:0003041:6395", 
    "77:01:0003041:6396", 
    "77:01:0003041:6398", 
    "77:01:0003041:6399", 
    "77:01:0003041:6400", 
    "77:01:0003041:6401", 
    "77:01:0003041:6402", 
    "77:01:0003041:6403", 
    "77:01:0003041:6404", 
    "77:01:0003041:6405", 
    "77:01:0003041:6406", 
    "77:01:0003041:6407", 
    "77:01:0003041:6409", 
    "77:01:0003041:6410", 
    "77:01:0003041:6411", 
    "77:01:0003041:6412", 
    "77:01:0003041:6413", 
    "77:01:0003041:6414", 
    "77:01:0003041:6415", 
    "77:01:0003041:6416", 
    "77:01:0003041:6417", 
    "77:01:0003041:6418", 
    "77:01:0003041:6420", 
    "77:01:0003041:6421", 
    "77:01:0003041:6422", 
    "77:01:0003041:6423", 
    "77:01:0003041:6424", 
    "77:01:0003041:6425", 
    "77:01:0003041:6426", 
    "77:01:0003041:6427", 
    "77:01:0003041:6428", 
    "77:01:0003041:6429", 
    "77:01:0003041:6431", 
    "77:01:0003041:6432", 
    "77:01:0003041:6433", 
    "77:01:0003041:6434", 
    "77:01:0003041:6435", 
    "77:01:0003041:6436", 
    "77:01:0003041:6437", 
    "77:01:0003041:6438", 
    "77:01:0003041:6439", 
    "77:01:0003041:6440", 
    "77:01:0003041:6442", 
    "77:01:0003041:6443", 
    "77:01:0003041:6444", 
    "77:01:0003041:6445", 
    "77:01:0003041:6446", 
    "77:01:0003041:6459", 
    "77:01:0003041:6460", 
    "77:01:0003041:6461", 
    "77:01:0003041:6462", 
    "77:01:0003041:6463", 
    "77:01:0003041:6465", 
    "77:01:0003041:6466", 
    "77:01:0003041:6467", 
    "77:01:0003041:6468", 
    "77:01:0003041:6470", 
    "77:01:0003041:6528", 
    "77:01:0003041:6529", 
    "77:01:0003041:6540", 
    "77:01:0003041:6542", 
    "77:01:0003041:6543", 
    "77:01:0003041:6544", 
    "77:01:0003041:6573", 
    "77:01:0003041:6574", 
    "77:01:0003041:6579", 
    "77:01:0003041:6581", 
    "77:01:0003041:6583"
]
URL = "https://www.gosuslugi.ru/600359/1/form"
COOKIES_FILE = "cookies.pkl"

if os.name == "nt": #windows
    CHROMEDRIVER_PATH =  r"C:\Users\shidlovskiyaf\projects\PKK_FLAT_PARS\chromedriver.exe"
else: #unix
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
