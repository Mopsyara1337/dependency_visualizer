import gzip
import tomllib
import zlib
from pathlib import Path
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.error import URLError

import packages as pak
import graph as gr

PROJECT_DIR = Path(__file__).resolve().parent.parent

def load_config():
    config_path = PROJECT_DIR / "config.toml"
    with open(config_path, "rb") as f:
        return tomllib.load(f)

def validate_repository(config):
    """Проверяет корректности адреса репозитория (URL или пути к файлу)"""

    repository = config["repository"]
    if config["test_mode"]:
        repository_path = PROJECT_DIR / repository
        if not repository_path.is_file():
            raise ValueError(f"Файл репозитория "
                             f"{repository} не найден")

    else:
        parsed = urlparse(repository)
        if ((parsed.scheme not in ("http", "https"))
            or not parsed.hostname
            or any(char.isspace() for char in repository)):
            raise ValueError("Неверный URL-адрес репозитория")

def validate_output_file(config):
    """Проверяет корректность выходного файла"""

    file = Path(config["output_file"])
    if file.suffix.lower() != ".png":
        raise ValueError("Неверное расширение выходного файла")

    if file.name != config["output_file"]:
        raise ValueError("Некорректное имя выходного файла")

    banned_chars = "<>:\"/\\|?*"
    if any(char in banned_chars for char in file.name):
        raise ValueError("Имя файла содержит запрещенные символы")

def validate_config(config):
    """Проверка корректности параметров конфигурации"""

    expected_types = {"package": str, "repository": str,
                      "test_mode": bool, "output_file": str}

    for key, expected_type in expected_types.items():
        if key not in config:
            raise ValueError(f"Отсутствует параметр {key}")

        if not isinstance(config[key], expected_type):
            raise ValueError(f'Неверный тип параметра {key}:'
                             f' ожидался {expected_type.__name__},'
                             f' получен {type(config[key]).__name__}')

    string_keys = ["package", "repository", "output_file"]
    for key in string_keys:
        if config[key].strip() == "":
            raise ValueError(f"Параметр {key} пустой")

    validate_repository(config)

    validate_output_file(config)

def prepare_config():
    try:
        config = load_config()
        validate_config(config)
    except FileNotFoundError:
        print("Файл не найден!")
        return None
    except tomllib.TOMLDecodeError:
        print("Некорректный формат TOML")
        return None
    except ValueError as e:
        print(f'Ошибка конфигурации: {e}')
        return None
    return config

def prepare_package(config):
    try:
        packages_data = load_packages_data(config)
    except HTTPError as e:
        print(f"Ошибка HTTP: {e.code}")
        return None
    except URLError as e:
        print(f"Ошибка подключения {e.reason}")
        return None
    except TimeoutError as e:
        print(f"Истекло время ожидания {e}")
        return None
    except (gzip.BadGzipFile, EOFError, zlib.error, UnicodeDecodeError) as e:
        print(f"Ошибка: {e}")
        return None
    except OSError as e:
        print(f"Ошибка получения данных репозитория: {e}")
        return None

    return pak.build_package_index(packages_data)

def load_packages_data(config):
    if not config["test_mode"]:
        packages_data = pak.fetch_packages(config["repository"])
    else:
        repository_path = PROJECT_DIR / config["repository"]
        packages_data = repository_path.read_text(encoding="utf-8")

    return packages_data


def main():
    config = prepare_config()
    if config is None:
        return

    package_index = prepare_package(config)
    if package_index is None:
        return

    try:
        reverse_graph = gr.build_reverse_graph(package_index)
        reverse_dependencies = gr.find_reverse_dependencies(
            reverse_graph, config["package"]
        )
    except ValueError as e:
        print(f"Ошибка построения графа: {e}")
        return

    print(f"Найдено обратных зависимостей для пакета {config["package"]}: "
          f"{len(reverse_dependencies)}")
    print("\nОбратные зависимости:")

    if not reverse_dependencies:
        print("Обратные зависимости отсутствуют")

    for package in sorted(reverse_dependencies):
        print(package)

if __name__ == '__main__':
    main()