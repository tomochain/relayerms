import { bindActions } from 'redux-zero/utils'
import wretch from 'wretch'
import PouchDB from 'pouchdb'
import pouchMemory from 'pouchdb-adapter-memory'
import pouchQuery from 'pouchdb-find'

import store from 'service/store'
import * as http from 'service/backend'
import { AlertVariant } from 'service/frontend'
import { ThrowOn } from 'service/helper'


export const AppInitialization = async (state) => {
  // GET BASIC DATA FROM BACKENDS
  const {
    Contracts,
    Relayers,
    Tokens,
    error,
  } = await http.getPublicResource()

  const {
    tomochain,
    error: tomoPriceError,
  } = await http.getTomoPrice()

  ThrowOn(error, `Fetch Token Error: ${error}`)

  const notifications = [
    ...state.notifications,
    {
      open: true,
      message: 'fetched all resources',
      variant: AlertVariant.success,
    },
  ]

  const [getBitcoinError, bitcoinStat] = await wretch('https://api.coingecko.com/api/v3/coins/bitcoin?localization=false')
    .get().json().then(resp => [null, resp]).catch(t => [null, null])

  ThrowOn(getBitcoinError, 'Error getting bitcoin stat')

  const [getEthError, ethStat] = await wretch('https://api.coingecko.com/api/v3/coins/ethereum?localization=false')
    .get().json().then(resp => [null, resp]).catch(t => [null, null])

  ThrowOn(getEthError, 'Error getting ethereum stat')

  const network_info = {
    ...state.network_info,
    tomousd: tomoPriceError ? NaN : tomochain.usd,
    btcusd: (bitcoinStat) ? bitcoinStat.market_data.current_price.usd : 0,
    ethusd: (ethStat) ? ethStat.market_data.current_price.usd : 0,
  }

  // INIT POUCHDB FOR FRONTEND-SEARCHING
  PouchDB.plugin(pouchMemory)
  PouchDB.plugin(pouchQuery)

  const pouch = new PouchDB('tomorelayer', { adapter: 'memory' })

  await Promise.all(Contracts.map(async c => pouch.put({
    ...c,
    _id: 'contract' + c.id.toString(),
    type: 'contract',
    // We create a joined-string for `fuzzy searching`,
    // including all fields that we want user to be able to search
    fuzzy: [c.owner, c.address, c.name].join(','),
  })))

  await Promise.all(Tokens.map(async c => pouch.put({
    ...c,
    _id: 'token' + c.id.toString(),
    type: 'token',
    fuzzy: [c.name, c.symbol, c.address].join(',')
  })))

  await Promise.all(Relayers.map(async c => pouch.put({
    ...c,
    _id: 'relayer' + c.id.toString(),
    type: 'relayer',
    fuzzy: [
      c.name,
      c.owner,
      c.coinbase,
      c.address,
    ].join(','),
  })))

  await pouch.createIndex({
    index: {
      fields: [ '_id', 'fuzzy' ],
    },
  })

  return {
    Contracts,
    Relayers,
    Tokens,
    notifications,
    network_info,
    pouch,
  }
}

export const Logout = (state) => {
  window.sessionStorage.removeItem('tomorelayerAccessToken')
  const user = {
    ...state.user,
    wallet: undefined,
    hooked: false,
  }
  return {
    user,
  }
}

export const bindLogout = () => bindActions({ Logout }, store).Logout()
