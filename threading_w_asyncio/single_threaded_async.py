# Single threaded implementation of basic stock price web scraper. Get list of S&P500 companies
# and then get current stock price from Google Finance. Then print the stock prices. Good example
# for threading, as the majority of the time is I/O limited due to external https calls.

from bs4 import BeautifulSoup
import requests
import time
from pprint import pprint


def get_stock_symbols():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    raw_html = requests.get(url, timeout=600)
    soup = BeautifulSoup(raw_html.text, "lxml")
    table = soup.find(id="constituents")
    table_rows = table.find_all("tr")
    symbols = []
    for table_row in table_rows[1:]:
        symbol = table_row.find("td").text.strip("\n")
        symbols.append(symbol)
    return symbols


def get_price(symbol):
    # See if we can scrape from different stock quote website, so we can make async

    # Try all these. Stock exchange can vary on google finance
    urls = [
        f"https://www.google.com/finance/quote/{symbol}:NYSE?hl=en",
        f"https://www.google.com/finance/quote/{symbol}:NASDAQ?hl=en",
        f"https://www.google.com/finance/quote/{symbol}:BATS?hl=en",
    ]

    quote = "PRICE NOT FOUND"
    for url in urls:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        price = soup.find("div", class_=["fxKbKc"])
        if price is not None:
            quote = price.text.replace(",", "")
            break

    # From here, we could write the quote to a system like a database with another process
    print(f"{symbol}: {quote}")

    # Slow down API calls a bit so we don't bombard the API and be respectful.
    time.sleep(0.3)


def main():
    tik = time.perf_counter()
    companies = get_stock_symbols()
    # print(companies)

    for symbol in companies:
        get_price(symbol)
    tok = time.perf_counter()
    print(f"TOTAL RUNTIME (secs): {round(tok-tik, 2)}")


if __name__ == "__main__":
    main()
