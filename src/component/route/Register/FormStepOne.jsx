import React from 'react'
import { Box, Button, TextField, Typography } from '@material-ui/core'
import { MISC } from 'service/constant'
import { wrappers } from './forms'

const FormStepOne = props => {
  const {
    values,
    errors,
    handleChange,
    handleSubmit,
  } = props

  return (
    <form onSubmit={handleSubmit} className="text-left">
      <Typography variant="h5" className="mb-2">
        Relayer Registration
      </Typography>
      <Box display="flex" flexDirection="column" className="mb-2">
        <div>Deposit a minimum of {MISC.MinimumDeposit} TOMO, used to pay gas fees related to relayer operations.</div>
        <div>This deposit will be locked during the operation of your relayer</div>
        <div>The relayer Identifier Address can be a random wallet address since it does not store funds</div>
        <div>The logged-in address must be different from the relayer Identifier Address</div>
      </Box>
      <TextField
        name="deposit"
        label="How much TOMO do you want to deposit?"
        id="deposit-input"
        placeholder={`minimum ${MISC.MinimumDeposit}`}
        value={values.deposit}
        onChange={handleChange}
        error={errors.deposit}
        helperText={errors.deposit && <i className="text-alert">* Minimum deposit is 25,000 TOMO</i>}
        type="number"
        variant="outlined"
        className="mb-2"
        inputProps= {{
          'data-testid': 'deposit-input'
        }}
        required
        fullWidth
      />
      <TextField
        name="coinbase"
        label="What is your relayer Indentifier Address?"
        id="coinbase-input"
        value={values.coinbase}
        onChange={handleChange}
        error={Boolean(errors.coinbase)}
        helperText={errors.coinbase && <i className="text-alert">{errors.coinbase}</i>}
        inputProps= {{
          'data-testid': 'coinbase-input'
        }}
        variant="outlined"
        required
        fullWidth
      />
      <Box display="flex" justifyContent="flex-end" className="mt-2">
        <Button color="primary" variant="contained" type="submit">
          Save & Continue
        </Button>
      </Box>
    </form>
  )
}

export default wrappers.depositAndCoinbaseForm(FormStepOne)
