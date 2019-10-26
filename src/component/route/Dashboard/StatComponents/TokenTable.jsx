import React from 'react'
import { Grid, Paper } from '@material-ui/core'
import { withStyles } from '@material-ui/core/styles'
import { isEmpty } from 'service/helper'
import { SITE_MAP } from 'service/constant'
import { ExternalLinks } from 'service/backend'
import { CustomLink, StyledLink } from 'component/shared/Adapters'

const StyledPaper = withStyles(theme => ({
  root: {
    padding: 10,
    marginBottom: 15,
    paddingLeft: 20
  }
}))(Paper)

const TableHeads = [
  'Rank',
  'Token',
  'Price ($)',
  'Trades (24h)',
  'Volumes ($)',
]

const EmptyTokenTable = ({ coinbase }) => (
  <Grid container direction="column" className="mt-2">
    <Grid item className="text-center">
      You have yet to set any token for trading.
    </Grid>
    <Grid item className="text-center">
      Start adding some token <CustomLink to={`${SITE_MAP.Dashboard}/${coinbase}/config`}>here</CustomLink>...
    </Grid>
  </Grid>
)

const rowStyle = { width: '20%', textAlign: 'center' }

const TokenTable = ({ tokens, coinbase }) => {

  return isEmpty(tokens) ? <EmptyTokenTable coinbase={coinbase} /> : (
    <Grid container direction="column">
      <Grid item container className="mb-1" className="p-1">
        {TableHeads.map(h => <Grid key={h} item style={rowStyle}>{h}</Grid>)}
      </Grid>
      {tokens.map((item, index) => (
        <Grid item key={index}>
          <StyledPaper elevation={0}>
            <Grid container>
              <Grid item style={rowStyle}>{index + 1}</Grid>
              <Grid item style={rowStyle}>
                <StyledLink
                  href={ExternalLinks.token(item.address)}
                  rel="noopener noreferrer"
                  target="_blank"
                  className="m-0"
                  style={{ lineHeight: '19px' }}
                >
                  {item.symbol}
                </StyledLink>
              </Grid>
              <Grid item style={rowStyle}>
                {item.price}
              </Grid>
              <Grid item style={rowStyle}>
                {item.tradeNumber}
              </Grid>
              <Grid item style={rowStyle}>
                {item.volume24h.toLocaleString({ useGrouping: true })}
              </Grid>
            </Grid>
          </StyledPaper>
        </Grid>
      ))}
    </Grid>
  )
}

export default TokenTable
