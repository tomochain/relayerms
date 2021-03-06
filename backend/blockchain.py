import os
import json
from web3.auto import w3
from logzero import logger
from settings import settings
from model import Relayer, Token, Domain
from playhouse.shortcuts import model_to_dict

is_production = os.getenv('STG') == 'production'


class Blockchain:

    web3 = None

    RegistrationABI = json.loads('[{"constant":false,"inputs":[{"name":"coinbase","type":"address"},{"name":"fromToken","type":"address"},{"name":"toToken","type":"address"}],"name":"listToken","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"MaximumRelayers","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"RELAYER_LIST","outputs":[{"name":"_deposit","type":"uint256"},{"name":"_tradeFee","type":"uint16"},{"name":"_index","type":"uint256"},{"name":"_owner","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"coinbase","type":"address"}],"name":"depositMore","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"RELAYER_COINBASES","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"RESIGN_REQUESTS","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"coinbase","type":"address"}],"name":"getRelayerByCoinbase","outputs":[{"name":"","type":"uint256"},{"name":"","type":"address"},{"name":"","type":"uint256"},{"name":"","type":"uint16"},{"name":"","type":"address[]"},{"name":"","type":"address[]"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"coinbase","type":"address"},{"name":"tradeFee","type":"uint16"},{"name":"fromTokens","type":"address[]"},{"name":"toTokens","type":"address[]"}],"name":"update","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"maxRelayer","type":"uint256"},{"name":"maxToken","type":"uint256"},{"name":"minDeposit","type":"uint256"}],"name":"reconfigure","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"coinbase","type":"address"}],"name":"cancelSelling","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"coinbase","type":"address"},{"name":"fromToken","type":"address"},{"name":"toToken","type":"address"}],"name":"deListToken","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"coinbase","type":"address"},{"name":"price","type":"uint256"}],"name":"sellRelayer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"RelayerCount","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"RELAYER_ON_SALE_LIST","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"coinbase","type":"address"}],"name":"resign","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"coinbase","type":"address"},{"name":"new_owner","type":"address"}],"name":"transfer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"MinimumDeposit","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"coinbase","type":"address"},{"name":"tradeFee","type":"uint16"},{"name":"fromTokens","type":"address[]"},{"name":"toTokens","type":"address[]"}],"name":"register","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[],"name":"MaximumTokenList","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"coinbase","type":"address"}],"name":"buyRelayer","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"name":"coinbase","type":"address"}],"name":"refund","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"CONTRACT_OWNER","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"tomoxListing","type":"address"},{"name":"maxRelayers","type":"uint256"},{"name":"maxTokenList","type":"uint256"},{"name":"minDeposit","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"max_relayer","type":"uint256"},{"indexed":false,"name":"max_token","type":"uint256"},{"indexed":false,"name":"min_deposit","type":"uint256"}],"name":"ConfigEvent","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"deposit","type":"uint256"},{"indexed":false,"name":"tradeFee","type":"uint16"},{"indexed":false,"name":"fromTokens","type":"address[]"},{"indexed":false,"name":"toTokens","type":"address[]"}],"name":"RegisterEvent","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"deposit","type":"uint256"},{"indexed":false,"name":"tradeFee","type":"uint16"},{"indexed":false,"name":"fromTokens","type":"address[]"},{"indexed":false,"name":"toTokens","type":"address[]"}],"name":"UpdateEvent","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"owner","type":"address"},{"indexed":false,"name":"deposit","type":"uint256"},{"indexed":false,"name":"tradeFee","type":"uint16"},{"indexed":false,"name":"fromTokens","type":"address[]"},{"indexed":false,"name":"toTokens","type":"address[]"}],"name":"TransferEvent","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"deposit_release_time","type":"uint256"},{"indexed":false,"name":"deposit_amount","type":"uint256"}],"name":"ResignEvent","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"success","type":"bool"},{"indexed":false,"name":"remaining_time","type":"uint256"},{"indexed":false,"name":"deposit_amount","type":"uint256"}],"name":"RefundEvent","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"is_on_sale","type":"bool"},{"indexed":false,"name":"coinbase","type":"address"},{"indexed":false,"name":"price","type":"uint256"}],"name":"SellEvent","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"success","type":"bool"},{"indexed":false,"name":"coinbase","type":"address"},{"indexed":false,"name":"price","type":"uint256"}],"name":"BuyEvent","type":"event"}]')

    TOMOXListingABI = json.loads('[{"constant":true,"inputs":[],"name":"tokens","outputs":[{"name":"","type":"address[]"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"token","type":"address"}],"name":"getTokenStatus","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"token","type":"address"}],"name":"apply","outputs":[],"payable":true,"stateMutability":"payable","type":"function"}]')

    TRC21ABI = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"value","type":"uint256"}],"name":"estimateFee","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"issuer","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"minFee","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"value","type":"uint256"}],"name":"setMinFee","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"name","type":"string"},{"name":"symbol","type":"string"},{"name":"decimals","type":"uint8"},{"name":"cap","type":"uint256"},{"name":"minFee","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":true,"name":"issuer","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Fee","type":"event"}]')

    contracts = [
        {
            'id': 1,
            'name': 'TOMOXListing',
            'address': settings['tomoxlisting_addr'],
            'abi': TOMOXListingABI
        },
        {
            'id': 2,
            'name': 'RelayerRegistration',
            'address': settings['relayerregistration_addr'],
            'abi': RegistrationABI
        }
    ]

    def __init__(self):
        """ Interact with Blockchain through SmartContract & WebSocket
        """
        self.web3 = w3
        logger.info('Web3 URI: %s', os.getenv('WEB3_PROVIDER_URI'))
        logger.info('Chain connection status: %s', self.web3.isConnected())
        logger.info('Node name: %s', self.web3.clientVersion)

    def getRelayerByCoinbase(self, coinbase):
        c = self.web3.eth.contract(address=settings['relayerregistration_addr'], abi=self.RegistrationABI)
        relayer = c.functions.getRelayerByCoinbase(self.web3.toChecksumAddress(coinbase)).call()
        logger.info('Relayer %s', relayer)
        return relayer

    def updateRelayer(self, coinbase):
        coinbase = self.web3.toChecksumAddress(coinbase)
        c = self.web3.eth.contract(address=self.web3.toChecksumAddress(settings['relayerregistration_addr']), abi=self.RegistrationABI)
        logger.info('UpdateRelayer coinbase %s', coinbase)

        try:
            relayer = c.functions.getRelayerByCoinbase(coinbase).call()

            name='Relayer' + str(relayer[0])
            lock_time = c.functions.RESIGN_REQUESTS(coinbase).call()
            resigning = True if (lock_time) else False

            domain = self.createDomain(coinbase, resigning)
            Relayer.insert(
                idx=relayer[0],
                coinbase=coinbase,
                owner=relayer[1],
                name=name,
                deposit=relayer[2],
                trade_fee=relayer[3],
                from_tokens=relayer[4],
                to_tokens=relayer[5],
                link=domain,
                domain=domain,
                resigning=resigning,
                lock_time=lock_time).on_conflict(
                conflict_target=(Relayer.coinbase,),
                update={
                    Relayer.owner: relayer[1],
                    Relayer.deposit: relayer[2],
                    Relayer.trade_fee: relayer[3],
                    Relayer.from_tokens: relayer[4],
                    Relayer.to_tokens: relayer[5],
                    Relayer.resigning: resigning,
                    Relayer.lock_time: lock_time}
               ).execute()

        except:
            logger.error('UpdateRelayer failed')
        
    def updateRelayers(self):
        c = self.web3.eth.contract(address=self.web3.toChecksumAddress(settings['relayerregistration_addr']), abi=self.RegistrationABI)

        relayer_count = c.functions.RelayerCount().call()
        logger.info('Relayer count %s', relayer_count)
        for n in range(relayer_count):
            coinbase = c.functions.RELAYER_COINBASES(n).call()
            logger.info('Relayer coinbase %s', coinbase)
            relayer = c.functions.getRelayerByCoinbase(coinbase).call()
            lock_time = c.functions.RESIGN_REQUESTS(coinbase).call()
            logger.info('Relayer resign request %s', lock_time)

            resigning = True if (lock_time) else False

            logger.info('Relayer owner %s', relayer[1])
            for t in relayer[4]:
                self.updateToken(t)
            for t in relayer[5]:
                self.updateToken(t)

            domain = self.createDomain(coinbase, resigning)
            rl = (Relayer.insert(
                idx=relayer[0],
                coinbase=coinbase,
                owner=relayer[1],
                name='Relayer' + str(relayer[0]),
                deposit=relayer[2],
                trade_fee=relayer[3],
                from_tokens=relayer[4],
                to_tokens=relayer[5],
                link=domain,
                domain=domain,
                resigning=resigning,
                lock_time=lock_time).on_conflict(
                conflict_target=(Relayer.coinbase,),
                update={
                    Relayer.idx: relayer[0],
                    Relayer.owner: relayer[1],
                    Relayer.deposit: relayer[2],
                    Relayer.trade_fee: relayer[3],
                    Relayer.from_tokens: relayer[4],
                    Relayer.to_tokens: relayer[5],
                    Relayer.resigning: resigning,
                    Relayer.lock_time: lock_time}
               ).execute())

    def createDomain(self, coinbase, resigning):
        used = not resigning
        b = False
        try:
            try:
                db_relayer = Relayer.select().where(Relayer.coinbase == coinbase).get()
            except Relayer.DoesNotExist:
                b = True
            db_relayer = model_to_dict(db_relayer)
            Domain.update(used=used, coinbase=coinbase).where(Domain.domain == db_relayer['domain']).execute()
        except:
            pass

        try: 
            db_domain = Domain.select().where(Domain.used == False).order_by(Domain.id.asc()).get()
            db_domain = model_to_dict(db_domain)
            if b == True:
                Domain.update(used=True, coinbase=coinbase).where(Domain.domain == db_domain['domain']).execute()
            return db_domain['domain']
        except:
            countDomain = Domain.select().where(Domain.used == True).count()
            domain =  'https://' + format(countDomain, '03d') + '.' + settings['domain_suffix']
            Domain.insert(domain=domain, used=True, coinbase=coinbase).on_conflict_ignore(True).execute()
            return domain

    def updateToken(self, address):
        if address != '0x0000000000000000000000000000000000000001':
            t = self.web3.eth.contract(address=self.web3.toChecksumAddress(address), abi=self.TRC21ABI)
            total_supply = t.functions.totalSupply().call()
            symbol = t.functions.symbol().call()
            name = symbol
            decimals = t.functions.decimals().call()
            is_major = False
        else:
            total_supply = '1000000000000000000000000000000'
            symbol = 'TOMO'
            name = 'TomoChain'
            decimals = '18'
            is_major = True

        if symbol == 'BTC' or symbol == 'USDT' or symbol == 'TOMO' or symbol == 'ETH':
            is_major = True

        logger.info('Token address %s symbol %s major %s', address, symbol, is_major)
        rl = (Token.insert(
	    address=address,
	    name=name,
	    symbol=symbol,
	    decimals=decimals,
	    total_supply=total_supply,
	    is_major=is_major).on_conflict(
	    conflict_target=(Token.address,),
	    update={Token.is_major: is_major}
	   ).execute())
 
    
