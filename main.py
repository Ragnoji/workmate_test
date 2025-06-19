import argparse
import csv
from math import inf
import os
from tabulate import tabulate

parser = argparse.ArgumentParser(
    prog='ProgramName',
    description='What the program does',
    epilog='Text at the bottom of help'
)

parser.add_argument('--aggregate')
parser.add_argument('--file')
parser.add_argument('--order-by')
parser.add_argument('--rating')
parser.add_argument('--where')


def parse_csv(file: str) -> tuple[list[str], list[list[str]]]:
    data = []
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        headers = None
        for row in reader:
            if headers is None:
                headers = row
                continue
            data.append(row)
    return headers, data


def split_parameters(expression: str, operators: dict) -> tuple:
    operator = None
    parameters = [[]]
    for ch in expression:
        if ch in operators:
            parameters.append([])
            operator = ch
            continue
        parameters[-1].append(ch)
    parameters = [''.join(p) for p in parameters]
    column, value = parameters
    return operator, column, value


def get_column_type(data: list[list[str]], column_id: int) -> type:
    column_type = str

    if len(data) > 1:
        try:
            float(data[1][column_id])
            column_type = float
        except ValueError:
            pass
    return column_type


def get_column_id(headers: list[str], column: str) -> int:
    try:
        column_id = headers.index(column)
    except ValueError as e:
        print(f"Column {column} does not exist")
        raise e
    return column_id


def filter_data(data: list[list[str]], headers: list[str], where: str) -> list[list[str]]:
    operators = {
        '<': lambda x, y: x < y,
        '=': lambda x, y: x == y,
        '>': lambda x, y: x > y
    }

    try:
        operator, column, compared_value = split_parameters(where, operators)
    except ValueError as e:
        print("Invalid format of --where")
        raise e

    operator_function = operators[operator]
    column_id = get_column_id(headers, column)
    column_type = get_column_type(data, column_id)

    if column_type is not str and operator != '=':
        try:
            compared_value = column_type(compared_value)
        except ValueError as e:
            print(f'--where value "{compared_value}" can not be converted to column type {column_type}')
            raise e

    filtered_data = []

    for i in range(len(data)):
        row = data[i]
        row_value = row[column_id]
        if column_type is not str:
            row_value = column_type(row_value)

        if not operator_function(row_value, compared_value):
            continue

        filtered_data.append(row)

    return filtered_data


def aggregate_data(data: list[list[str]], headers: list[str], aggregate: str) -> list[list[str]]:
    def calculate_avg():
        total = 0
        for i in range(len(data)):
            cur_value = float(data[i][column_id])
            total += cur_value
        avg = total / (len(data))
        return avg

    def calculate_min():
        min_value = inf
        for i in range(1, len(data)):
            cur_value = float(data[i][column_id])
            min_value = min(min_value, cur_value)
        return min_value

    def calculate_max():
        max_value = -inf
        for i in range(1, len(data)):
            cur_value = float(data[i][column_id])
            max_value = max(max_value, cur_value)
        return max_value

    supported_funcs = {
        'avg': calculate_avg,
        'min': calculate_min,
        'max': calculate_max
    }

    try:
        column, func = aggregate.split('=')
    except ValueError as e:
        print('Invalid format of --aggregate')
        raise e

    column_id = get_column_id(headers, column)
    column_type = get_column_type(data, column_id)

    if column_type is str:
        raise ValueError(f"Column for aggregation does not consist of numerical values")

    if func not in supported_funcs:
        raise ValueError(f"Not supported aggregation function")

    filtered_data = [[func], [supported_funcs[func]()]]
    return filtered_data


def order_data(data: list[list[str]], headers: list[str], order_by: str) -> list[list[str]]:
    try:
        column, direction = order_by.split('=')
    except ValueError as e:
        print('Invalid format of --order-by')
        raise e

    supported_directions = {
        'asc': False,
        'desc': True
    }

    if direction not in supported_directions:
        raise ValueError(f'Invalid --order-by value passed')

    reverse_bool = supported_directions[direction]
    column_id = get_column_id(headers, column)
    column_type = get_column_type(data, column_id)
    data = sorted(data, key=lambda x: column_type(x[column_id]), reverse=reverse_bool)
    return data


if __name__ == '__main__':
    headers, table = [], []
    args = parser.parse_args()
    if args.file is not None and os.path.isfile(args.file):
        headers, table = parse_csv(args.file)
    if args.where is not None:
        table = filter_data(table, headers, args.where)
    if args.order_by is not None:
        table = order_data(table, headers, args.order_by)
    if args.aggregate is not None:
        table = aggregate_data(table, headers, args.aggregate)
        print(tabulate(table, tablefmt="github"))
    else:
        print(tabulate(table, headers, tablefmt="github"))




