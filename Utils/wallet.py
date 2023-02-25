import requests
from bs4 import BeautifulSoup
import fake_useragent


async def update_currency_rate_satoshi() -> float:
    """
    :return: float value - Currency rate for satoshi if url not available then return -1.0
    """
    user_agent = fake_useragent.UserAgent().random
    header = {"user-agent": user_agent}
    url = f'https://crypto.com/price/ru/satoshi'
    response = requests.get(url, headers=header)
    if response.ok:
        soup = BeautifulSoup(response.text, "lxml")
        currency_rate = soup.find("p", {"class": 'chakra-text css-1arpw5g'})
        if currency_rate is not None:
            return float(currency_rate.text.split("$")[-1])

    return float(-1)


async def update_wallet_balance(address: str) -> int:
    """
    :param address: address from BTC wallet
    :return: Amount of satoshi from address if address not exist or connection problem return -1
    """
    user_agent = fake_useragent.UserAgent().random
    header = {"user-agent": user_agent}
    first_url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}"
    second_url = f"https://blockchain.info/rawaddr/{address}"

    response = requests.get(first_url, headers=header)
    if not response.ok:
        response = requests.get(second_url, headers=header)
        if not response.ok:
            return -1

    wallet = response.json()
    return int(wallet['final_balance'])


# currency_rate = update_currency_rate_satoshi()
# print(f"Currency_rate: {currency_rate}$")
# text = get_wallet_balance('bc1qe0sdtah4jz2jzp3umvpg2dkk8uvphac47jwlgw4253434g4')
# balance = text * currency_rate
# print(f"{balance}$")
