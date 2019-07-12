from playhouse.shortcuts import model_to_dict
from model import Contract
from exception import InvalidValueException
from util.decorator import admin_required
from .base import BaseHandler


class ContractHandler(BaseHandler):

    def get(self):
        """Return all Contracts"""
        contracts = []
        contracts = [model_to_dict(c or {}) for c in Contract.select().where(Contract.obsolete == False)]
        self.json_response(contracts)

    @admin_required
    async def post(self):
        payload = self.request_body.get('contract', None)

        if not payload:
            raise InvalidValueException('relayer payload is empty')

        async with self.application.objects.atomic():
            contract = await self.application.objects.create(Contract, **payload)
            self.json_response(contract)
