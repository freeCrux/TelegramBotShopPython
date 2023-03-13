from asyncio import sleep
import requests
import fake_useragent
from database.sql_bd import DataBase
import datetime


class Converter:

    _coinmarketcap_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    def __init__(self, network: list[str], token_coinmarketcap: str):
        self._delay_update_coins_rate = 60
        self._last_update_time: datetime = datetime.date.today()

        self._tokens = {"coinmarketcap": token_coinmarketcap}
        self._network = network
        self._coins_rate = {
            "BTC": None,
            "SATOSHI": None,
            "USDT": None,
        }
        self._get_currency_coin_rate()

    def _get_currency_coin_rate(self):
        parameters = {"symbol": ",".join(self._network)}
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self._tokens["coinmarketcap"],
        }

        response = requests.get(url=self._coinmarketcap_url, headers=headers, params=parameters)
        if response.ok:
            data = response.json()
            self._coins_rate["BTC"] = round(data['data']['BTC']['quote']['USD']['price'], 2)
            self._coins_rate["SATOSHI"] = round(data['data']['BTC']['quote']['USD']['price'] / 100000000, 7)
            self._coins_rate["USDT"] = round(data['data']['USDT']['quote']['USD']['price'], 2)

            # TODO потом удали эти ништяки, они для теста
            print(f"Bitcoin rate: $ {self._coins_rate['BTC']}")
            print(f"Satoshi rate: $ {self._coins_rate['SATOSHI']}")
            print(f"USDT rate: $ {self._coins_rate['USDT']}")

        else:
            raise Exception("Can`t get coins rate!")

    def update_coin_rate(self):
        cur_time = datetime.date.today()
        if cur_time > self._last_update_time + datetime.timedelta(minutes=self._delay_update_coins_rate):
            self._get_currency_coin_rate()

    def convert_coin_to_usd(self, coin_amount: float, network: str) -> float:
        if network in self._network:
            if network == "USDT":
                return coin_amount / 10**6
            return coin_amount * self._coins_rate[network]
        else:
            raise Exception(f"{network} don`t available for processing. Only can with {self._network}")


class WalletsHandler:

    _bts_url = "https://api.blockcypher.com/v1/btc/main/addrs/"
    _bts_url2 = "https://blockchain.info/rawaddr/"

    def __init__(self, network: list, db: DataBase, token_coinmarketcap: str, token_etherscan: str):
        self._network = network

        # Time in minutes
        self._payment_time = 120
        self.token_etherscan = token_etherscan

        self._db = db
        self._converter = Converter(network=network, token_coinmarketcap=token_coinmarketcap)

    def get_payment_time(self):
        return self._payment_time

    def get_currency_coin_balance(self, address: str, network: str) -> float:
        """
        :return: Amount of satoshi(for BTC) and for other coins from address,
        if address not exist or connection problem return -1
        """
        user_agent = fake_useragent.UserAgent().random
        header = {"user-agent": user_agent}
        if network in self._network:

            if network == "BTC":
                url1 = f"{self._bts_url}{address}"
                url2 = f"{self._bts_url2}{address}"
                response = requests.get(url1, headers=header)
                if not response.ok:
                    response = requests.get(url2, headers=header)
                    if not response.ok:
                        return float(-1)
                wallet = response.json()
                return wallet['final_balance']

            elif network == "USDT":
                usdt_contract_address = '0xdac17f958d2ee523a2206206994597c13d831ec7'
                url = f'https://api.etherscan.io/api?module=account&action=tokenbalance&contractaddress=' \
                           f'{usdt_contract_address}&address={address}&tag=latest&apikey={self.token_etherscan}'
                response = requests.get(url, headers=header)
                if not response.ok:
                    return float(-1)
                wallet = response.json()
                return wallet['result']
            else:
                raise Exception(f"U have forgotten add {network} to function")

        raise Exception(f"{network} don`t available for processing. Only can with {self._network}")

    async def _update_data_and_client_balance(self, address: tuple):
        old_address_balance: int = address[2]
        new_address_balance: float = self.get_currency_coin_balance(address=address[1], network=address[4])
        client_payed_coin: float = new_address_balance - old_address_balance
        self._db.set_usage_status_how_free_wallet_address(address_id=address[0])
        self._db.update_wallet_address_balance(address_id=address[0], balance=new_address_balance)
        if client_payed_coin > 0:
            client_payed_usd: float = self._converter.convert_coin_to_usd(coin_amount=client_payed_coin,
                                                                          network=address[4])
            self._db.change_client_balance(client_id=address[6], cash=client_payed_usd)
        await sleep(3)

    async def processing_addresses_that_over_wait_and_update_coins_rate(self):
        self._converter.update_coin_rate()
        addresses_id: list = self._db.get_id_wallet_addresses_that_over_wait()
        for i in addresses_id:
            address_data: tuple = self._db.get_wallet_address_data(address_id=i)
            if address_data is not None:
                print(i)
                await self._update_data_and_client_balance(address=address_data)
            else:
                raise Exception(f"{addresses_id} isn`t on database")
