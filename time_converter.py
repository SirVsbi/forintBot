import datetime
import json
from os import path


def date_converter(time):
    # date = '11/07/2022 - 18:05:12'
    date_root = "11/07/2022 - "
    date = date_root + time

    # convert string to datetimeformat
    date = datetime.datetime.strptime(date, "%d/%m/%Y - %H:%M:%S")

    # convert datetime to timestamp
    timestamp = datetime.datetime.timestamp(date)
    print(date)
    print(timestamp)
    return timestamp


def data_writer(time, exchange_rate):
    filename = "data.json"
    listObj = {}

    # Check if file exists
    if path.isfile(filename) is False:
        raise Exception("File not found")

    # Read JSON file
    with open(filename) as fp:
        listObj = json.load(fp)

    # Verify existing list
    print(listObj)

    print(type(listObj))

    listObj[date_converter(time)] = exchange_rate

    # Verify updated list
    print(listObj)

    with open(filename, 'w') as json_file:
        json.dump(listObj, json_file,
                  indent=4,
                  separators=(',', ': '))


if __name__ == '__main__':
    while True:
        time = input("time")
        rate = input("rate")
        data_writer(time, rate)
