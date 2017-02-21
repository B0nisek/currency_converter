import sys, getopt, json, requests
from bs4 import BeautifulSoup


def valid_currency(currency):
    if not currency.isalpha():
        raise ValueError("Currency should contain only letters")
    if len(currency) is not 3:
        raise ValueError("Currency should be 3 letters long")


def convert(amount, currency_input, currency_output):
    result = {}

    currency_dict = get_currency_dictionary(currency_input, currency_output)

    for key in currency_dict.keys():
        ratio = float(currency_dict.get(key))
        result.update({key: ratio*amount})

    return result


def get_currency_dictionary(currency_input, currency_output=None):
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


def create_json(amount, currency_input, result):
    my_json = '{"input": {"amount": %s, "currency": "%s"}, "output": ' % (amount, currency_input)
    my_json += result.__str__().replace('\'', '\"')
    my_json += '}'

    parsed = json.loads(my_json)

    return json.dumps(parsed, indent=4, sort_keys=True)


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

    result = convert(amount, currency_input, currency_output)

    json_result = create_json(str(amount), currency_input, result)

    print(json_result)

main()
