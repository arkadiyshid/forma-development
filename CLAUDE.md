# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GOSPARSE — автоматизированный парсер кадастровых данных с портала Госуслуг (gosuslugi.ru). Проект использует Selenium для автоматизации браузера и извлечения информации о недвижимости по кадастровым номерам.

## Architecture

Проект состоит из двух основных скриптов:

- **sel_parse_1.py** — базовая версия парсера с простой логикой обработки
- **sel_parse_codex.py** — продвинутая версия с имитацией человеческого поведения, антибот-защитой и адаптивными паузами

### Key Components

**Антибот-система (sel_parse_codex.py)**:
- Динамические паузы с рандомизацией (`human_pause`, `human_type`)
- Адаптивный темп работы через `STATE["pace"]` — замедляется при обнаружении блокировок
- Обработка ошибок антибота через `handle_antibot_error()` — автоматическое закрытие модальных окон и повторные попытки
- Длинные перерывы каждые 6-12 запросов для имитации естественного поведения

**Авторизация**:
- Cookie-based аутентификация через `cookies.pkl`
- Функция `authorise_if_needed()` загружает сохраненные cookies или запрашивает ручную авторизацию
- Первый запуск требует ручного входа в браузере

**Парсинг данных**:
- Извлечение 10 полей: наименование, кадастровый номер, адрес, площадь, назначение, вид жилого помещения, этаж, кадастровая стоимость, вид права, обременения
- XPath-селекторы через `label_xpath()` для поиска пар label-value
- Результаты сохраняются в `data/result_YYYY-MM-DD_HH-MM-SS.txt`

**Навигация по форме**:
- `open_cadaster_search_form()` — проходит через многошаговую форму (Начать → Посмотреть основные сведения → Квартира → Кадастровый номер)
- `return_to_search_form()` — возврат к форме поиска через кнопку "Назад" с проверкой доступности поля ввода
- `ensure_search_form_ready()` — проверяет готовность формы перед каждым запросом

## Development Commands

### Setup
```bash
python3 -m venv venv
source venv/bin/activate  # на macOS/Linux
pip install -r requirements.txt
```

### Running
```bash
# Базовая версия
python sel_parse_1.py

# Продвинутая версия с антибот-защитой
python sel_parse_codex.py
```

### Configuration

Перед запуском необходимо настроить:

1. **CHROMEDRIVER_PATH** — путь к ChromeDriver (сейчас: `/Users/arkadijsidlovskij/Desktop/projects/PKK_FLAT_PARS/chromedriver`)
2. **KAD_NUMBERS** — список кадастровых номеров для обработки (формат: "77:01:0003041:6341")

### Output

- Результаты: `data/result_YYYY-MM-DD_HH-MM-SS.txt`
- Ошибки: `errors.txt`
- Образцы данных: `samples.xlsx`
- Cookies: `cookies.pkl` (игнорируется git)

## Important Notes

- ChromeDriver должен соответствовать версии установленного Chrome
- При первом запуске требуется ручная авторизация на Госуслугах
- Скрипт не закрывает браузер автоматически (закомментирован `driver.quit()`) для отладки
- sel_parse_codex.py использует адаптивные задержки — время выполнения зависит от количества номеров и срабатывания антибота
- Изображения отключены в Chrome для ускорения загрузки (`profile.managed_default_content_settings.images: 2`)
