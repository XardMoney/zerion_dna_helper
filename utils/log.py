from loguru import logger as log
from sys import stderr

log.remove()
log.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                       ' | <level>{level: <8}</level>'
                       ' - <white>{message}</white>')
log.add(open("files/log.txt", mode="a", encoding="utf-8"), format='<white>{time:HH:mm:ss}</white>'
                                                                  ' | <level>{level: <8}</level>'
                                                                  ' - <white>{message}</white>')
