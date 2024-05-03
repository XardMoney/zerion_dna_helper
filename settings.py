# Shuffle accounts (True or False)
SHUFFLE_ACCOUNTS = True

# Use proxy (True or False)
USE_PROXY = True

# Limit of accounts that can be run concurrently
SEMAPHORE_LIMIT = 5

# Limit of retries for all the actions
NUMBER_OF_RETRIES = 5

# Range of the seconds to sleep between actions (random selection)
SLEEP_RANGE = [15, 25]

# Limit of gwei for all the transactions
GWEI_LIMIT = 20
# Range of the seconds to sleep between gwei checks (random selection)
SLEEP_RANGE_FOR_GWEI_CHECKS = [40, 60]
