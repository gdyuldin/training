### Check that test cover all branches

We have next function:

```python
def logic(a, b=0):
    if b != 0:
        return a / b
    else:
        return a
```

You should write one/many tests to cover all branches of this function

All test should be places in one file, and written with unittest module


Example:
```python
import unittest

from function import logic


class TestCase(unittest.TestCase):
    # Your test logic
    pass


if __name__ == '__main__':
    unittest.main()
```
