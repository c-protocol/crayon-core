# @version ^0.3.7

token_price : public(int256)
decimals: public(uint8)

@external
def __init__(
    _initial_price: int256,
    _decimals: uint8
):
    """
    @dev initial price expected to be precise to decimals
    @param _initial_price The initial price including decimals precision
    @param _decimals The precision of the price returned from the oracle
    """
    self.token_price = _initial_price
    self.decimals = _decimals

@external
@view
def latestRoundData() -> (uint80, int256, uint256, uint256, uint80):
    """
    @dev Only returns price
    """

    # we only ever use the price from this call
    return (0, self.token_price, 0, 0, 0)

@external
def set_token_price(
    _price : int256
):
    """
    @dev price includes decimals precision
    @param _price The new price
    """
    
    self.token_price = _price
    