import os
import sys
import time
import pickle
import random
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# === LOGGING SETUP ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('parser.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# === НАСТРОЙКИ ===
# TEST MODE: Ограниченный список для тестирования (25 номеров)
KAD_NUMBERS = [
    "77:01:0003041:6341",
    "77:01:0003041:6452",
    "77:01:0003041:6563",
    "77:01:0003041:6675",
    "77:01:0003041:6786",
    "77:01:0003041:6896",
    "77:01:0003041:6907",
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
TYPE_PAUSE_RANGE = (0.25, 0.55)
TYPE_CHAR_RANGE = (0.03, 0.08)
MICRO_THINK_RANGE = (0.25, 0.6)
CLICK_PAUSE_RANGE = (0.2, 0.5)
PAGE_THINK_RANGE = (0.5, 1.4)
MIN_REQUEST_INTERVAL = (1.2, 2.4)
LONG_BREAK_EVERY = (6, 12)
LONG_BREAK_RANGE = (6.0, 14.0)
ANTIBOT_COOLDOWN_RANGE = (20.0, 45.0)
RETRY_DELAY_RANGE = (3.0, 6.0)
MAX_RETRIES = 2
PACE_MAX = 3.0

# NEW: Периодическая перезагрузка страницы для обхода антибота
PAGE_RELOAD_EVERY = (5, 8)  # Перезагружать страницу каждые 5-8 запросов
PAGE_RELOAD_PAUSE = (3.0, 7.0)  # Пауза после перезагрузки

# Проверка ChromeDriver
if not os.path.exists(CHROMEDRIVER_PATH):
    logger.error(f"ChromeDriver не найден: {CHROMEDRIVER_PATH}")
    sys.exit(1)

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


STATE = {
    "pace": 1.0,
    "antibot_hits": 0,
    "last_request_ts": 0.0,
    "actions": 0,
    "requests_since_reload": 0,  # NEW: счетчик запросов с последней перезагрузки
    "next_reload_at": random.randint(*PAGE_RELOAD_EVERY),  # NEW: когда делать перезагрузку
}


def _paced_range(base_range):
    return (base_range[0] * STATE["pace"], base_range[1] * STATE["pace"])


def human_pause(base_range):
    time.sleep(random.uniform(*_paced_range(base_range)))


def maybe_long_break():
    if STATE["actions"] == 0:
        return
    if STATE["actions"] % random.randint(*LONG_BREAK_EVERY) == 0:
        logger.info("Длинный перерыв для имитации человеческого поведения")
        human_pause(LONG_BREAK_RANGE)


def ensure_request_spacing():
    now = time.time()
    min_interval = random.uniform(*_paced_range(MIN_REQUEST_INTERVAL))
    wait_for = min_interval - (now - STATE["last_request_ts"])
    if wait_for > 0:
        time.sleep(wait_for)
    STATE["last_request_ts"] = time.time()


def bump_pace():
    STATE["pace"] = min(PACE_MAX, STATE["pace"] * 1.4)
    logger.warning(f"Темп замедлен до {STATE['pace']:.2f}x")


def human_type(element, text):
    for ch in text:
        element.send_keys(ch)
        time.sleep(random.uniform(*_paced_range(TYPE_CHAR_RANGE)))
        if random.random() < 0.08:
            time.sleep(random.uniform(*_paced_range(MICRO_THINK_RANGE)))
    typing_pause()


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
    human_pause(CLICK_PAUSE_RANGE)
    try:
        button.click()
    except Exception:
        driver.execute_script("arguments[0].click();", button)
    human_pause(SHORT_PAUSE_RANGE)
    STATE["actions"] += 1
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
    logger.info("Cookies сохранены")


def load_cookies():
    with open(COOKIES_FILE, "rb") as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            logger.warning(f"Ошибка загрузки cookie: {e}")
    driver.refresh()
    time.sleep(2)


def authorise_if_needed():
    driver.get(URL)
    if os.path.exists(COOKIES_FILE):
        load_cookies()
        logger.info("Cookies загружены — работаем авторизовано")
    else:
        logger.info("=" * 50)
        logger.info("Авторизуйтесь на сайте в открывшемся окне браузера")
        input("Когда авторизация завершена, нажмите [Enter]...")
        save_cookies()


def check_for_captcha_or_block():
    """NEW: Проверка на капчу, антибот или неожиданные изменения страницы"""
    indicators = [
        (By.CLASS_NAME, "rros-ui-lib-error-message"),  # Окно ошибки антибота
        (By.XPATH, "//*[contains(text(), 'Captcha') or contains(text(), 'captcha') or contains(text(), 'CAPTCHA')]"),  # Капча
        (By.XPATH, "//*[contains(text(), 'проверка') or contains(text(), 'Проверка')]"),  # Проверка безопасности
        (By.XPATH, "//*[contains(text(), 'подозрительн') or contains(text(), 'Подозрительн')]"),  # Подозрительная активность
    ]

    for by, selector in indicators:
        try:
            element = driver.find_element(by, selector)
            if element.is_displayed():
                logger.warning("=" * 60)
                logger.warning("ОБНАРУЖЕНА КАПЧА ИЛИ АНТИБОТ ПРОВЕРКА!")
                logger.warning("=" * 60)
                logger.warning("Текущий URL: " + driver.current_url)
                logger.warning("Решите капчу или пройдите проверку в браузере")
                logger.warning("=" * 60)
                input("После решения нажмите [Enter] для продолжения...")
                logger.info("Продолжаем работу")
                STATE["antibot_hits"] += 1
                bump_pace()
                human_pause(PAGE_RELOAD_PAUSE)
                return True
        except Exception:
            continue
    return False


def handle_antibot_error():
    try:
        error_block = WebDriverWait(driver, 1.5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "rros-ui-lib-error-message"))
        )
        logger.warning("Обнаружена блокировка антибота")
        STATE["antibot_hits"] += 1
        bump_pace()

        # NEW: Сначала проверяем, не требуется ли ручное вмешательство
        if check_for_captcha_or_block():
            return True

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
            logger.info("Окно ошибки закрыто")
        except Exception as e:
            logger.error(f"Не удалось закрыть окно ошибки: {e}")
        logger.info("Пауза для снятия блокировки")
        human_pause(ANTIBOT_COOLDOWN_RANGE)
        return True
    except TimeoutException:
        return False


def open_cadaster_search_form():
    driver.get(URL)
    human_pause(PAGE_THINK_RANGE)
    click_button_by_text("Начать", timeout=5)
    click_button_by_text("Посмотреть основные сведения о недвижимости")
    click_button_by_text("Квартира")
    click_button_by_text("Кадастровый номер")
    wait_for_cad_input()
    human_pause(SHORT_PAUSE_RANGE)


def ensure_search_form_ready():
    try:
        wait_for_cad_input(timeout=2)
    except TimeoutException:
        logger.info("Форма не готова, открываю заново")
        open_cadaster_search_form()


def return_to_search_form():
    logger.debug("Возврат к форме поиска через кнопку 'Назад'")
    back_button = click_button_by_text("Назад", timeout=5)

    try:
        WebDriverWait(driver, 5).until(EC.staleness_of(back_button))
    except (TimeoutException, StaleElementReferenceException):
        pass

    try:
        cad_input = wait_for_cad_input(timeout=5)
        cad_input.clear()
        return cad_input
    except TimeoutException:
        logger.warning("После 'Назад' поле не появилось, восстанавливаю форму")
        open_cadaster_search_form()
        cad_input = wait_for_cad_input(timeout=5)
        cad_input.clear()
        return cad_input


def maybe_reload_page():
    """NEW: Периодическая перезагрузка страницы для обхода антибота"""
    if STATE["requests_since_reload"] >= STATE["next_reload_at"]:
        logger.info(f"Перезагрузка страницы после {STATE['requests_since_reload']} запросов")
        driver.get(URL)
        human_pause(PAGE_RELOAD_PAUSE)
        open_cadaster_search_form()
        STATE["requests_since_reload"] = 0
        STATE["next_reload_at"] = random.randint(*PAGE_RELOAD_EVERY)
        logger.info(f"Следующая перезагрузка через {STATE['next_reload_at']} запросов")


def parse_kadaster(kad_num):
    logger.info(f"Обработка {kad_num}")
    ensure_search_form_ready()

    # NEW: Проверка на капчу перед началом
    check_for_captcha_or_block()

    try:
        cad_input = wait_for_cad_input(timeout=5)
        cad_input.clear()
        human_type(cad_input, kad_num)
        logger.debug(f"Номер {kad_num} введен")
        ensure_request_spacing()
        continue_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((
                By.XPATH, '//span[contains(text(), "Продолжить")]/ancestor::button'
            ))
        )
        continue_btn.click()
        human_pause(SHORT_PAUSE_RANGE)
        STATE["actions"] += 1
        STATE["requests_since_reload"] += 1  # NEW: увеличиваем счетчик

        # NEW: Проверка на капчу после клика
        check_for_captcha_or_block()

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

        logger.info(f"Данные для {kad_num} успешно извлечены")
        for k, v in result.items():
            logger.debug(f"  {k}: {v}")

        maybe_long_break()
        return {"kad_num": kad_num, "info": [f"{k}: {v}" for k, v in result.items()]}
    except Exception as e:
        logger.error(f"Ошибка при обработке {kad_num}: {e}")
        # NEW: Проверка на капчу при ошибке
        check_for_captcha_or_block()
        return {"kad_num": kad_num, "info": [], "error": str(e)}


# === CLEANUP HANDLER ===
def cleanup():
    logger.info("Завершение работы, закрытие браузера")
    try:
        driver.quit()
    except Exception as e:
        logger.error(f"Ошибка при закрытии браузера: {e}")


import atexit
atexit.register(cleanup)

# === MAIN ===
try:
    logger.info("Запуск парсера GOSPARSE (Claude Edition)")
    logger.info(f"Всего кадастровых номеров: {len(KAD_NUMBERS)}")

    authorise_if_needed()
    open_cadaster_search_form()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Результаты запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 40 + "\n")

    script_start = time.perf_counter()

    for index, kad in enumerate(KAD_NUMBERS):
        result = None
        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(f"[{index+1}/{len(KAD_NUMBERS)}] {kad}, попытка {attempt}/{MAX_RETRIES}")
            result = parse_kadaster(kad)
            if not result.get("error"):
                break
            logger.warning(f"Ошибка для {kad}, попытка {attempt} из {MAX_RETRIES}")
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
            # NEW: Проверяем, нужна ли перезагрузка страницы
            maybe_reload_page()

            # Если перезагрузки не было, используем обычный возврат
            if STATE["requests_since_reload"] > 0:
                try:
                    return_to_search_form()
                    human_pause(SHORT_PAUSE_RANGE)
                except Exception:
                    logger.warning(f"Возврат к форме не удался после {kad}")
                    ensure_search_form_ready()

    elapsed = time.perf_counter() - script_start
    minutes, seconds = divmod(elapsed, 60)
    logger.info(f"Готово! Данные сохранены в {OUTPUT_FILE}")
    logger.info(f"Время выполнения: {int(minutes)} мин {seconds:.1f} сек")
    logger.info(f"Срабатываний антибота: {STATE['antibot_hits']}")

except KeyboardInterrupt:
    logger.info("Прервано пользователем")
except Exception as e:
    logger.error(f"Критическая ошибка: {e}", exc_info=True)
finally:
    cleanup()
