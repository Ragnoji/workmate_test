import pytest
import os
from main import (
    parse_csv, split_parameters, get_column_type,
    get_column_id, filter_data, aggregate_data, order_data
)

TEST_CSV_PATH = os.path.join(os.path.dirname(__file__), "products.csv")


@pytest.fixture(scope="module")
def products_data():
    headers, data = parse_csv(TEST_CSV_PATH)
    return headers, data


def test_parse_csv(products_data):
    headers, data = products_data
    assert headers == ["name", "brand", "price", "rating"]
    assert len(data) == 10
    assert data[0] == ["iphone 15 pro", "apple", "999", "4.9"]


def test_split_parameters_valid():
    op, col, val = split_parameters("price>500", {'>': None})
    assert op == '>'
    assert col == "price"
    assert val == "500"


def test_get_column_id(products_data):
    headers, _ = products_data
    assert get_column_id(headers, "rating") == 3
    with pytest.raises(ValueError):
        get_column_id(headers, "not_a_column")


def test_get_column_type(products_data):
    headers, data = products_data
    idx = get_column_id(headers, "price")
    assert get_column_type(data, idx) == float
    idx = get_column_id(headers, "name")
    assert get_column_type(data, idx) == str


def test_filter_data_gt(products_data):
    headers, data = products_data
    filtered = filter_data(data, headers, "price>800")
    assert all(float(row[2]) > 800 for row in filtered)


def test_filter_data_eq(products_data):
    headers, data = products_data
    filtered = filter_data(data, headers, "brand=apple")
    assert all(row[1] == "apple" for row in filtered)


def test_aggregate_data_avg(products_data):
    headers, data = products_data
    result = aggregate_data(data, headers, "price=avg")
    assert result[0][0] == "avg"
    assert isinstance(result[1][0], float)


def test_aggregate_data_min(products_data):
    headers, data = products_data
    result = aggregate_data(data, headers, "price=min")
    assert result[1][0] == 149.0


def test_order_data_asc(products_data):
    headers, data = products_data
    ordered = order_data(data, headers, "rating=asc")
    ratings = [float(row[3]) for row in ordered]
    assert ratings == sorted(ratings)


def test_order_data_desc(products_data):
    headers, data = products_data
    ordered = order_data(data, headers, "price=desc")
    prices = [float(row[2]) for row in ordered]
    assert prices == sorted(prices, reverse=True)


def test_split_parameters_invalid():
    with pytest.raises(ValueError):
        split_parameters("pricerating", {'>': lambda x, y: x > y})


def test_filter_data_nonconvertible_type(products_data):
    headers, data = products_data
    with pytest.raises(ValueError):
        filter_data(data, headers, "price>expensive")


def test_filter_data_unknown_operator(products_data):
    headers, data = products_data
    with pytest.raises(ValueError):
        filter_data(data, headers, "price$999")


def test_filter_data_column_not_exist(products_data):
    headers, data = products_data
    with pytest.raises(ValueError):
        filter_data(data, headers, "nonexistent>0")


def test_aggregate_data_invalid_column_type(products_data):
    headers, data = products_data
    with pytest.raises(ValueError):
        aggregate_data(data, headers, "brand=max")


def test_aggregate_data_invalid_format(products_data):
    headers, data = products_data
    with pytest.raises(ValueError):
        aggregate_data(data, headers, "rating")


def test_aggregate_data_unsupported_function(products_data):
    headers, data = products_data
    with pytest.raises(ValueError):
        aggregate_data(data, headers, "price=total")


def test_order_data_invalid_format(products_data):
    headers, data = products_data
    with pytest.raises(ValueError):
        order_data(data, headers, "rating")


def test_order_data_invalid_direction(products_data):
    headers, data = products_data
    with pytest.raises(ValueError):
        order_data(data, headers, "rating=middle")
