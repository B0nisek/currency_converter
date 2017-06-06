import sys, getopt, json, requests
from bs4 import BeautifulSoup

'''
validate_currency(currency)

currency - given currency

currency needs to be 3 chars long and contain only alpha
'''


def validate_currency(currency):
    if len(currency) is not 3:
        raise ValueError("Currency should be 3 letters long")
    if not currency.isalpha():
        raise ValueError("Currency should contain only letters")


'''
convert(amount, currency_input, currency_output)

converts given amount of currency input

returns a dictionary with converted prices {currency:converted price}
'''


def convert(amount, currency_input, currency_output):
    result = {}

    currency_dict = get_currency_dictionary(currency_input, currency_output)

    for key in currency_dict.keys():
        ratio = float(currency_dict.get(key))
        result.update({key: ratio*amount})

    return result


'''
get_currency_dictionary(currency_input, currency_output)

scrapes data from web to get a dictionary filled with results depending on currency output.
if currency output is not given returns result with all loaded currencies

returns a dictionary {currency:price} format
'''


def get_currency_dictionary(currency_input, currency_output):
    currency_dict = {}
    url_to_scrape = 'http://www.xe.com/currencytables/?from=' + currency_input
    r = requests.get(url_to_scrape)
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.find('table', attrs={'id': 'historicalRateTbl'}).find('tbody').find_all('tr')

    for row in rows:
        cells = row.findAll('td')

        if currency_output is not None:
            if currency_output == cells[0].string:
                currency_dict.update({cells[0].string: cells[2].string})
                break

        else:
            currency_dict.update({cells[0].string: cells[2].string})

    return currency_dict

'''
create_json(amount, currency_input, result)

amount - float from command line, input
currency_input - input currency
result - dictionary with results {currency:price}

returns json formated string
'''


def create_json(amount, currency_input, result):
    my_json = '{"input": {"amount": %s, "currency": "%s"}, "output": ' % (amount, currency_input)
    my_json += result.__str__().replace('\'', '\"')
    my_json += '}'

    parsed = json.loads(my_json)

    return json.dumps(parsed, indent=4, sort_keys=True)

'''
get_options()

gets and parses options from command line. expects correct arguments. unexpected arguments raises an exception
which is not handled

returns arguments in following order amount, input_currency, output_currency
'''


def get_options():
    opts, args = getopt.getopt(sys.argv[1:], 'a:i:o:', ['amount=', 'input_currency=', 'output_currency='])

    input_currency = None
    amount = None
    output_currency = None

    for opt, arg in opts:
        if opt in ("-a", "--amount"):
            amount = float(arg)
        elif opt in ("-i", "--input_currency"):
            input_currency = arg
        elif opt in ("-o", "--output_currency"):
            output_currency = arg

    return amount, input_currency, output_currency


def main():
    amount, currency_input, currency_output = get_options()

    try:
        validate_currency(currency_input)
        if currency_output is not None:
            validate_currency(currency_output)
    except ValueError as ex:
        print(ex)
        return -1

    result = convert(amount, currency_input, currency_output)

    json_result = create_json(str(amount), currency_input, result)

    print(json_result)

main()
