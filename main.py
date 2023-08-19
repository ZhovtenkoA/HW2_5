import argparse
import asyncio
import json
from datetime import datetime, timedelta
import aiohttp


async def get_exchange_rates(days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days - 1)
    exchange_rates = []

    async with aiohttp.ClientSession() as session:
        current_date = start_date
        while current_date <= end_date:
            formatted_date = current_date.strftime('%d.%m.%Y')
            url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={formatted_date}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    rates = {
                        formatted_date: {
                            'EUR': {
                                'sale': None,
                                'purchase': None
                            },
                            'USD': {
                                'sale': None,
                                'purchase': None
                            }
                        }
                    }
                    for rate in data['exchangeRate']:
                        if rate['currency'] == 'EUR':
                            rates[formatted_date]['EUR']['sale'] = rate['saleRate']
                            rates[formatted_date]['EUR']['purchase'] = rate['purchaseRate']
                        elif rate['currency'] == 'USD':
                            rates[formatted_date]['USD']['sale'] = rate['saleRate']
                            rates[formatted_date]['USD']['purchase'] = rate['purchaseRate']
                    exchange_rates.append(rates)

            current_date += timedelta(days=1)

    return exchange_rates


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Get exchange rates for the last N days.')
    parser.add_argument(
        'days', type=int, help='number of days to retrieve exchange rates (maximum 10)')
    args = parser.parse_args()

    if args.days > 10:
        print("Maximum supported number of days is 10.")
    else:
        loop = asyncio.get_event_loop()
        try:
            rates = loop.run_until_complete(get_exchange_rates(args.days))
            json_output = json.dumps(rates, indent=4)
            print(json_output)
        finally:
            loop.close()
