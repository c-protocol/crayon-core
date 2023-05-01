
def min_longable_amount(
    amount,
    longable_decimals,
    longable_oracle,
    value_to_loan_ratio,
    base_coin_decimals,
    borrow_fee
):
    # value_to_loan_ratio is stored as percentage
    ltv  = value_to_loan_ratio
    (_, longable_price, _, _, _) = longable_oracle.latestRoundData()
    oracle_decimals = longable_oracle.decimals()
    borrow_token_decimals = base_coin_decimals
    longable_amount  = 0
    # ltv is in percentage. we have to divide it by 100
    longable_amount = (amount + borrow_fee) * ltv * 10 ** (oracle_decimals + longable_decimals - borrow_token_decimals - 2) // longable_price

    return longable_amount + 10**longable_decimals

