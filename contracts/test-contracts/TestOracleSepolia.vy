# @version ^0.3.7

TEST_ORACLE : constant(address) = 0x132C06E86CcCf93Afef7B33f0FF3e2E97EECf8f6
TEST_ORACLE_DECIMALS : constant(uint8) = 8

interface ITestOracle:
    def getAssetPrice(_token : address) -> uint256: view

decimals: public(uint8)

numeraire : public(address)
token : public(address)
oracle : ITestOracle

@external
def __init__(
    _numeraire: address,
    _token: address,
    _decimals: uint8
):
    """
    @dev Price unit converter
    @param _numeraire The token in units of which prices are to be expressed
    @param _token The token the price of which this oracle provides
    @param _decimals The precision of the returned price
    """

    self.numeraire = _numeraire
    self.token = _token
    self.decimals = _decimals
    self.oracle = ITestOracle(TEST_ORACLE)

@external
@view
def latestRoundData() -> (uint80, int256, uint256, uint256, uint80):
    """
    @dev Only returns price
    """

    base_price : uint256 = self.oracle.getAssetPrice(self.numeraire)
    token_price : uint256 = self.oracle.getAssetPrice(self.token)

    # we only ever use the price from this call. Note this assumes token_price and base_price are expressed with the same precision -- which is indeed the case for our test oracle
    return (0, convert(token_price * 10**convert(self.decimals, uint256) / base_price, int256), 0, 0, 0)
