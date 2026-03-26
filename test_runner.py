import os
import unittest
import xmlrunner

if __name__ == "__main__":
    os.makedirs("reports", exist_ok=True)
    suite = unittest.TestLoader().discover("./tests", pattern="test_*.py")
    with open("reports/results.xml", "wb") as output:
        xmlrunner.XMLTestRunner(output=output).run(suite)
