import tomllib
from pathlib import Path
from urllib.parse import urlparse

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
            raise ValueError("Невенрный URL-адрес репозитория")

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
            raise ValueError(f"Пареметр {key} пустой")

    validate_repository(config)

    validate_output_file(config)

def print_config(config):
    for key, value in config.items():
        print(f'{key} = {value}')

def main():
    try:
        config = load_config()
        validate_config(config)
    except FileNotFoundError:
        print("Файл не найден!")
        return
    except tomllib.TOMLDecodeError:
        print("Некорректный формат TOML")
        return
    except ValueError as e:
        print(f'Ошибка компиляции: {e}')
        return

    print_config(config)




if __name__ == '__main__':
    main()