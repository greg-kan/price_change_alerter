from pathlib import Path
from configparser import RawConfigParser
from datetime import date
import os

DEBUG_MODE = True

APP_FOLDER = '.price_change_alerter'
CONF_APP_FILE = 'application.ini'
CONF_APP_FILE_LOGGING_SECTION = 'logging'
CONF_DB_FILE = 'database.ini'
CONF_DB_FILE_POSTGRES_CONNECTION_SECTION = 'postgresql'
CONF_TELEGRAM_FILE = 'telegram.ini'
CONF_TELEGRAM_FILE_BOT_SECTION = 'bot'

EARLIEST_DATE_STR = '1980-01-01'

app_home = Path.home() / APP_FOLDER

if not os.path.exists(app_home):
    raise Exception(f"Util home folder absent: {app_home}")

app_conf_file = app_home / CONF_APP_FILE
db_conf_file = app_home / CONF_DB_FILE
telegram_conf_file = app_home / CONF_TELEGRAM_FILE


def config(filename, section):
    parser = RawConfigParser()
    parser.read(filename)

    parameters = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            parameters[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return parameters


LOGGING_PARAMS = config(app_conf_file, CONF_APP_FILE_LOGGING_SECTION)
DB_PARAMS = config(db_conf_file, CONF_DB_FILE_POSTGRES_CONNECTION_SECTION)
TELEGRAM_BOT_PARAMS = config(telegram_conf_file, CONF_TELEGRAM_FILE_BOT_SECTION)
APPLICATION_LOG = f"{Path(LOGGING_PARAMS['log_files_dir']) / LOGGING_PARAMS['app_log_file_prefix']}_{date.today()}.log"
