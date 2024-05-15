"""
Скрипт для шифрования файлов
"""
import argparse
import os
from cryptography.fernet import Fernet
import getpass
from loguru import logger


def encrypt_file(file_name, key):
    fernet = Fernet(key)
    with open(file_name, 'rb') as file:
        original = file.read()
    encrypted = fernet.encrypt(original)
    with open(file_name, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)


def main():
    parser = argparse.ArgumentParser(description="Скрипт для шифрования файла")

    # example data/filename.txt
    parser.add_argument("--path", help="Путь до файла", required=True)

    args = parser.parse_args()
    path = args.path

    if not os.path.exists(path):
        logger.error(f"File '{path}' does not exist.")
        return

    if os.path.isdir(path):
        logger.error(f"path is cannot be directory!")
        return

    try:
        password_key = getpass.getpass(prompt='Введите ключ для шифрования данных: ')
        encrypt_file(path, password_key)
        logger.success(f'File {path} encrypt success!')
    except ValueError as e:
        logger.error(str(e))
        return
    except IsADirectoryError as e:
        logger.error(e)
        return


if __name__ == '__main__':
    main()
