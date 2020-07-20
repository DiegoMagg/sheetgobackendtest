import unittest
from accounts import tests as accounts_tests
from application import tests as app_tests


MODULES = (accounts_tests, app_tests)

if __name__ == "__main__":
    for module in MODULES:
        print(f'Starting {module.__name__}')
        suite = unittest.TestLoader().loadTestsFromModule(module)
        unittest.TextTestRunner(verbosity=1).run(suite)
