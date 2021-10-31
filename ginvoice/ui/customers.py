from ginvoice.common import signal


@signal()
def filter_customers(row, search):
    return search.get_text().lower() in row.get_child().get_text().lower()
