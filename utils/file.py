from core.config import FILE_LOCK


async def read_lines(path, encoding="utf-8"):
    async with FILE_LOCK:
        with open(path, encoding=encoding) as f:
            lines = f.readlines()

        lines = list(filter(lambda x: x, [line.strip() for line in lines]))

        return lines


async def append_line(line, path, encoding="utf-8"):
    async with FILE_LOCK:
        with open(path, mode="a", encoding=encoding) as f:
            f.write(line.strip() + "\n")


async def clear_file(path, encoding="utf-8"):
    async with FILE_LOCK:
        with open(path, mode="w", encoding=encoding) as f:
            f.truncate(0)
