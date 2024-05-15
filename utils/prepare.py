from loguru import logger

from utils.decrypt import get_decrypt_data


def get_data(file_path: str, encrypted=True) -> list[str]:
    if encrypted:
        data = get_decrypt_data(file_path)
        data = data.decode('utf-8')
    else:
        with open(file_path, 'r') as file:
            data = file.read()

    lines = data.strip().splitlines()
    logger.success(f'Was found {len(lines)} lines')
    return lines
