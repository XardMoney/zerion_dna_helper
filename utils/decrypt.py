"""Скрипт для дешифровки файла"""
import argparse
import os
from cryptography.fernet import Fernet, InvalidToken
import getpass
from loguru import logger


def decrypt_file(file_name, key):
    fernet = Fernet(key)
    with open(file_name, 'rb') as encrypted_file:
        encrypted = encrypted_file.read()
    decrypted = fernet.decrypt(encrypted)
    with open(file_name, 'wb') as decrypted_file:
        decrypted_file.write(decrypted)


def decrypt_file_to_memory(file_name, key):
    fernet = Fernet(key)
    with open(file_name, 'rb') as encrypted_file:
        encrypted = encrypted_file.read()
    decrypted = fernet.decrypt(encrypted)
    return decrypted


def get_decrypt_data(file_path) -> bytes | None:
    try:
        password_key = getpass.getpass(prompt=f'Введите ключ для расшифровки данных {file_path}: ')
        data = decrypt_file_to_memory(file_path, password_key)
        logger.success(f'File {file_path} decrypt success!')
        return data
    except ValueError as e:
        logger.error(str(e))
        return
    except InvalidToken:
        logger.error('Указан неверный ключ для расшифровки')
        return


def main():
    parser = argparse.ArgumentParser(description="Скрипт для дешифровки файла")

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
        password_key = getpass.getpass(prompt='Введите ключ для расшифровки данных: ')
        decrypt_file(path, password_key)
        logger.success(f'File {path} decrypt success!')
    except ValueError as e:
        logger.error(str(e))
        return
    except InvalidToken:
        logger.error('Указан неверный ключ для расшифровки')
        return


if __name__ == '__main__':
    main()
