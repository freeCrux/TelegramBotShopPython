import requests
from bs4 import BeautifulSoup


async def update_currency_rate_satoshi() -> float:
    """
    :return: float value - Currency rate for satoshi if url not available then return -1.0
    """
    test_url = f'https://crypto.com/price/ru/satoshi'
    response = requests.get(test_url)
    if response.ok:
        soup = BeautifulSoup(response.text, "lxml")
        currency_rate = soup.find("p", {"class": 'chakra-text css-1arpw5g'})
        if currency_rate is not None:
            return float(currency_rate.text.split("$")[-1])

    return float(-1)


async def get_wallet_balance(address: str) -> int:
    """
    :param address: address from BTC wallet
    :return: Amount of satoshi from address if address not exist return -1
    """
    response = requests.get(f'https://blockchain.info/rawaddr/{address}')
    if response.ok:
        wallet = response.json()
        return int(wallet['final_balance'])

    return -1

# currency_rate = update_currency_rate_satoshi()
# print(f"Currency_rate: {currency_rate}$")
# text = get_wallet_balance('bc1qe0sdtah4jz2jzp3umvpg2dkk8uvphac47jwlgw4253434g4')
# balance = text * currency_rate
# print(f"{balance}$")
