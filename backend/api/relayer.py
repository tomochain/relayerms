from playhouse.shortcuts import model_to_dict
from logzero import logger
from model import Relayer
from exception import InvalidValueException, MissingArgumentException
from util.decorator import authenticated
from .base import BaseHandler
from blockchain import Blockchain
from settings import settings
from urllib.parse import urljoin
import requests



RELAYER_SCHEMA = {
    'owner': {
        'type': 'string',
        'is_address': True,
        'required': True,
    },
    'name': {
        'type': 'string',
        'minlength': 3,
        'maxlength': 200,
        'required': True,
    },
    'coinbase': {
        'type': 'string',
        'is_address': True,
        'required': True,
    },
    'deposit': {
        'type': 'string',
        'required': True,
    },
    'trade_fee': {
        'type': 'number',
        'min': 1,
        'max': 9999,
        'required': True,
    },
    'from_tokens': {
        'type': 'list',
        'schema': {
            'type': 'string',
            'is_address': True,
        },
        'minlength': 0,
        'required': True,
        'empty': True,
    },
    'to_tokens': {
        'type': 'list',
        'schema': {
            'type': 'string',
            'is_address': True,
        },
        'minlength': 0,
        'required': True,
        'empty': True,
    },
    'logo': {
        'type': 'string',
        'nullable': True,
    },
    'link': {
        'type': 'string',
        'nullable': True,
    },
    'resigning': {
        'type': 'boolean',
        'default': False,
    },
    'lock_time': {
        'type': 'number',
        'nullable': True,
    },
}


def verify_user(user, relayer_owner):
    if not user:
        raise InvalidValueException('Missing user address')

    if not relayer_owner:
        raise InvalidValueException('Missing relayer owner address')

    if user.lower() != relayer_owner.lower():
        raise InvalidValueException('Owner address does not match relayer_owner address')


class RelayerHandler(BaseHandler):

    schema = RELAYER_SCHEMA

    @authenticated
    async def get(self, user):
        relayers = [model_to_dict(relayer or {}) for relayer in Relayer.select().where(Relayer.owner == user)]
        self.json_response(relayers)

    @authenticated
    async def post(self, user):
        """Add new relayer"""
        relayer = self.request_body
        name = relayer.get('name', None)

        verify_user(user, relayer['owner'])

        normalized_relayer = self.validator.normalized(relayer)

        b = Blockchain()
        coinbase = b.web3.toChecksumAddress(relayer['coinbase'])
        r = b.getRelayerByCoinbase(coinbase)

        if r[1].lower() != user.lower():
            raise InvalidValueException('owner required')

        b.updateRelayer(coinbase)

        query = (Relayer.update(**normalized_relayer).where(Relayer.coinbase == coinbase).returning(Relayer))
        cursor = query.execute()

        try:
            requests.put(urljoin(settings['tomodex'], '/api/relayer') + '?relayerAddress=' + coinbase + '&relayerName=' + name + '&authKey=' + settings['tomodex_auth'])
        except:
            logger.error('Update tomodex failed')

        self.json_response(model_to_dict(cursor[0]))

    @authenticated
    async def patch(self, user):
        """Update existing relayer"""
        relayer = self.request_body
        relayer_id = relayer.get('id', None)
        relayer_owner = relayer.get('owner', None)
        name = relayer.get('name', None)

        verify_user(user, relayer_owner)

        if relayer_id == None:
            raise MissingArgumentException('missing relayer id')

        del relayer['id']

        if relayer.get('new_owner', None):
            relayer['owner'] = relayer['new_owner']
            del relayer['new_owner']

        normalized_relayer = self.validator.normalized(relayer)

        try:
            db_relayer = Relayer.select().where(Relayer.id == relayer_id).get()

            db_relayer = model_to_dict(db_relayer)
            if (user.lower() != relayer_owner.lower()) or (user.lower() != db_relayer['owner'].lower()):
                raise MissingArgumentException('wrong owner')

            b = Blockchain()
            coinbase = b.web3.toChecksumAddress(db_relayer['coinbase'])
            r = b.getRelayerByCoinbase(coinbase)

            if r[1].lower() != relayer['owner'].lower():
                raise InvalidValueException('owner required')

            b.updateRelayer(coinbase)

            try:
                requests.put(urljoin(settings['tomodex'], '/api/relayer') + '?relayerAddress=' + coinbase + '&relayerName=' + name + '&authKey=' + settings['tomodex_auth'])
            except:
                logger.error('Update tomodex failed')

            query = (Relayer.update(**normalized_relayer).where(Relayer.id == relayer_id).returning(Relayer))
            cursor = query.execute()
            self.json_response(model_to_dict(cursor[0]))
        except IndexError:
            raise InvalidValueException('relayer id={param} does not exist'.format(param=str(relayer_id)))

    @authenticated
    async def delete(self, user):
        """Delete a relayer"""
        relayer_id = self.get_argument('id', None)

        if not relayer_id:
            raise MissingArgumentException('missing relayer id')

        try:
            relayer = Relayer.select().where(Relayer.owner == user, Relayer.id == relayer_id).get()
            db_relayer = model_to_dict(relayer)

            if user.lower() != db_relayer['owner'].lower():
                raise MissingArgumentException('wrong owner')

            b = Blockchain()
            r = b.getRelayerByCoinbase(db_relayer['coinbase'])

            if r[1].lower() != user.lower():
                raise InvalidValueException('owner required')


            relayer.delete_instance()
            self.json_response({})
        except Exception:
            raise InvalidValueException('invalid relayer: relayer with id={} or owner={} does not exist'.format(relayer_id, user))
