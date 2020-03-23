"""Configuration file for build/utilities."""

from colorama import Fore, Style

# Check mark character
CHECK_MARK = u'\u2714'
# Cross mark character
CROSS_MARK = u'\u2718'
# Okay green colour.
OKAY_GREEN = Fore.GREEN
# Error red colour.
ERROR_RED = Fore.RED
# Normal text.
NORMAL_TEXT = Style.RESET_ALL
# Okay message prefix or suffix.
OKAY_MSG = OKAY_GREEN + CHECK_MARK + NORMAL_TEXT
# Error message prefix or suffix.
ERROR_MSG = ERROR_RED + CROSS_MARK + NORMAL_TEXT

# Tuple containing directories which can be ignored while looking for 'unit_test' files.
IGNORE_LIST = ('tests', 'unit_tests', 'samples', 'templates', 'images', 'docs')

# The cut-off for code coverage percentage. Anything below this will be flagged.
CUT_OFF_CODE_COVERAGE_PCT = 80

# Ignore list for 'flake8' compliance violation codes
CODE_COMPLIANCE_IGNORE_LIST = ['F405', 'E731']

# Compliance check plugins' folder name
COMPLIANCE_CHECK_PLUGINS_FOLDER = 'compliance_check_plugins'

# Filter for git diff
GIT_DIFF_FILTER = 'ACMRTUXB'

CODE_VALIDATOR_TO_MODULE_MAP = {
    'flake8': 'flake8.api.legacy',
    'pylint': 'pylint.epylint'
}
