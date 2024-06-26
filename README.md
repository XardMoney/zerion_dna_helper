[![PyPI supported Python versions](https://img.shields.io/pypi/pyversions/better-automation.svg)](https://www.python.org/downloads/release/python-3116/)
# Общая информация
Данный софт поможет вам в минте Zerion DNA в сети Ethereum. Если не умеете устанавливать софты, читайте гайд - [\*тык\*](https://teletype.in/@rwlije/XardMoneyPythonGuide)

## 💡 Основные особенности  
+ _Асинхронность_
+ _Поддержка http proxy_
+ _Логирование_
+ _Сбор неотработавших и отработавших аккаунтов в отдельные текстовые файлы_
+ _Проверка уровня газа и другие настройки_

## ⚙️ Настройки
После полной установки открываем файл `settings.py`, переходим к настройкам:
+ `SHUFFLE_ACCOUNTS` - перемешивать аккаунты (True) или идти по порядку (False)
+ `USE_PROXY` - использовать прокси (True) или нет (False)
+ `SEMAPHORE_LIMIT` - количество аккаунтов, выполняющихся одновременно (аналог количества потоков), целое число
+ `NUMBER_OF_RETRIES` - количество попыток для проведения транзакции, целое число
+ `SLEEP_RANGE` - задержка между аккаунтами и попытками выполнить транзацию, два целых числа (минимум и максимум, каждый раз выбирается рандомно)
+ `GWEI_LIMIT` - максимально допустимый газ для выполнения транзакции, целое число
+ `SLEEP_RANGE_FOR_GWEI_CHECKS` - задержка между проверками газа для отдельног аккаунта, два целых числа (минимум и максимум, каждый раз выбирается рандомно)

## 🗂 Файлы
Основные файлы
+ `files/private_keys.txt` - ваши приватники
+ `files/proxy_list.txt` - ваши прокси, пример правильного формата в файле (если у вас прокси другого формата, можете попросить ChatGPT преобразовать их в нужный для софта)

Следующих файлов не будет при скачивании, но они будут созданы после первого запуска софта:
+ `files/log.txt` - все логи софта
+ `files/succeeded_wallets.txt` - аккаунты, на которых минт выполнен успешно (после каждого запуска очищается, поэтому тут будут данные с последнего запуска)
+ `files/failed_wallets.txt` - аккаунты, на которых минт не удался из-за какой-то ошибки (после каждого запуска очищается, поэтому тут будут данные с последнего запуска)

## 🔗 Links
[**@XardMoney**](https://t.me/XardMoney) | [**@XardCode**](https://t.me/XardCode)
