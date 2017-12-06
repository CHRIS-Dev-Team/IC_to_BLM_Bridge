months = [{
    'name': 'JANUARY',
    'abbreviation': 'JAN',
    'number': 1
}, {
    'name': 'FEBRUARY',
    'abbreviation': 'FEB',
    'number': 2
}, {
    'name': 'MARCH',
    'abbreviation': 'MAR',
    'number': 3
}, {
    'name': 'APRIL',
    'abbreviation': 'APR',
    'number': 4
}, {
    'name': 'MAY',
    'abbreviation': 'MAY',
    'number': 5
}, {
    'name': 'JUNE',
    'abbreviation': 'JUN',
    'number': 6
}, {
    'name': 'JULY',
    'abbreviation': 'JUL',
    'number': 7
}, {
    'name': 'AUGUST',
    'abbreviation': 'AUG',
    'number': 8
}, {
    'name': 'SEPTEMBER',
    'abbreviation': 'SEP',
    'number': 9
}, {
    'name': 'OCTOBER',
    'abbreviation': 'OCT',
    'number': 10
}, {
    'name': 'NOVEMBER',
    'abbreviation': 'NOV',
    'number': 11
}, {
    'name': 'DECEMBER',
    'abbreviation': 'DEC',
    'number': 12
}]


def convert_month(input_type, month, return_type):
    valid_types = ['name', 'abbreviation', 'number']
    input_type = input_type.lower()
    return_type = return_type.lower()
    try:
        month = int(month)
    except ValueError:
        month = month.upper()

    if input_type in valid_types and return_type in valid_types:
        try:
            return (m[return_type] for m in months if m[input_type] == month).next()
        except StopIteration:
            raise StopIteration("Sorry, {} was not found under the {} input type".format(month, input_type))
    else:
        raise ValueError('Your input was "{}" and your return type was "{}". They can only be one of the following: \n'
                         '    "Name" - For the full name of the month (ex. November)\n'
                         '    "Abbreviation" - For abbreviation of the month (ex. Nov)\n'
                         '    "Number" - For the numerical value of the month (ex. 11)\n'
                         '*Not case sensitive'.format(input_type, return_type))