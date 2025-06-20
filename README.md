### Before running program
`pip install -r requirements.txt`

### Example of running program with all possible arguments
`python main.py --file products.csv --order-by "rating=asc" --where "brand=xiaomi" --aggregate "price=avg"`

### Running test coverage check
`pytest --cov=main test.py`

### Required arguments
- `--file`