.. index:: _rewards

.. _rewards:

Rewards
#######

Depositors (lenders) and borrowers in Crayon Protocol are rewarded with the ``XCRAY`` token. Accumulated rewards can be claimed from the Crayon Protocol Control contract.

The following functions in the C Control smart contract support the reward token, including minting activities.

.. py:function:: mint_all_reward_token(_user: address)
    
    Credit ``_user`` with all the reward tokens accumulated by ``_user`` on all the desks minus a percentage specified by the ``_user``'s front-end, or other service, provider.

    * ``_user``: The address whose rewards are being claimed

.. py:function:: mint_reward_token(_user: address, _desks: DynArray[address, 20])

    Credit ``_user`` with the reward tokens accumulated by ``_user`` on ``_desks``.

    * ``_user``: The address whose rewards are being claimed
    * ``_desks``: Desks on which ``_user`` accumulated rewards 

.. py:function:: get_reward_parameters(_desk: address) -> (uint256, uint256)

    Return the amount of reward tokens distributed to borrowers and depositors per block. Returns a tuple with borrower and lender rate as first and second component, respectively. This is a ``view`` function.

    * ``_desk``: The desk whose reward parameters are sought

.. py:function:: reward_balanceOf(_user: address, _desks: DynArray[address, 20]) -> uint256

    Return the balance of rewards ``_user`` accumulated on ``_desks`` as of the last update of the cumulative rewards on those desks. This function is a ``view`` function.

    * ``_user``: The user whose reward balance is sought
    * ``_desks``: The desks where rewards are to be checked

.. note::

    ``reward_balanceOf`` returns the balance as of the last call to ``update_cumul_rewards`` on the desk. The user can force an up-to-date balance by first calling ``update_cumul_rewards`` on the desks the user has chosen.

.. note::

    ``mint_reward_token`` and ``mint_all_reward_token`` mint the most up-to-date reward token balance. Indeed they internally call ``update_cumul_rewards`` on the desks the user chose.

.. py:function:: update_cumul_rewards()
    
    Force an update of the reward indices of a desk.

.. note::

    Unlike the other functions on this page, ``update_cumul_rewards`` is a method on the ``Desk`` smart contract **not** the ``Control`` smart contract.
    