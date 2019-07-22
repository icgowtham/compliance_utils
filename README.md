# Compliance Utilities
* Utility to check Python source files for various compliance.

### Introduction
* `Compliance Utils` is a Python based utility to check Python based source files for various compliance like: Doc Compliance, Code Compliance, Code Complexity, Coverage etc.

### Sample usage:
* On one terminal first run the manager application:
```bash
$ python code_compliance_check.py -path file.py
```

### Development
Clone the git repo and follow the steps below on any linux  machine.

    git clone https://github.com/icgowtham/compliance_utils.git
    cd compliance_utils

Setup python virtual environment.

    make setup-env
    source venv3/bin/activate


### Tests

To run the unit tests in folder unit_tests_path:

    pytest -vs tests

