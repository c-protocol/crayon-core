# @version ^0.3.7
# (c) Crayon Protocol Authors
# This is only used for testing

decimals : public(uint8)
balanceOf : public(HashMap[address, uint256])
allowance : public(HashMap[address, HashMap[address, uint256]])
admin : public(address)

@external
def __init__(
    _decimals : uint8
):
    self.decimals = _decimals
    # give deployer a billion tokens
    self.balanceOf[msg.sender] = 10  ** (9 + convert(_decimals, uint256))
    self.admin = msg.sender

@external
def transfer(
    _to: address,
    _am: uint256
) -> bool:

    self.balanceOf[msg.sender] -= _am
    self.balanceOf[_to] += _am

    return True

@external
def transferFrom(
    _from : address,
    _to : address,
    _am : uint256
) -> bool:

    self.balanceOf[_from] -= _am
    self.balanceOf[_to] += _am
    self.allowance[_from][_to] -= _am

    return True

@external
def approve(
    _to : address,
    _am : uint256
) -> bool:
    self.allowance[msg.sender][_to] = _am

    return True