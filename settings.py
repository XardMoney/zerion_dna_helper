# Shuffle accounts (True or False)
SHUFFLE_ACCOUNTS = True

# Use proxy (True or False)
USE_PROXY = True

# Encrypted files (True or False)
ENCRYPT_FILES = True

# Limit of accounts that can be run concurrently
SEMAPHORE_LIMIT = 2

# Limit of retries for all the actions
NUMBER_OF_RETRIES = 5

# Range of the seconds to sleep between actions (random selection)
SLEEP_RANGE = [600, 2400]
SLEEP_RANGE_BETWEEN_ATTEMPT = [10, 20]

# Limit of gwei for all the transactions
GWEI_LIMIT = 20
# Range of the seconds to sleep between gwei checks (random selection)
SLEEP_RANGE_FOR_GWEI_CHECKS = [40, 60]
