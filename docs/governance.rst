.. index:: _governance

.. _governance:

Governance
##########

Governance of the Crayon Protocol is concerned with deciding:

* The desks to deploy including their longables (tokens accepted as collateral) and horizons (loan durations).
* Setting and re-setting various fees on those desks.
* Setting and re-setting reward token distributions (``XCRAY`` tokens).

Fees and reward token distributions are managed on an on-going basis.

Approved governance decisions are executed through the ``Control`` smart contract where deployed desks are registered. The ``admin`` address in ``Control`` is the only address empowered to register newly deployed desks and set and reset fees and reward rates.

Current State
=============

The Crayon Protocol team currently holds the governance privileges and the ``Control`` smart contract's ``admin`` keys.

Future State
============

Governance will be transferred to ``XCRAY`` token holders. See :ref:`Roadmap <roadmap>`. ``XCRAY`` token holders will use the (to-be-deployed) ``Governor`` smart contract to vote their tokens in favor of (or against) proposed new desk deployments or new fees and distribution rates of reward tokens across the desks. The Crayon Protocol team will also change the ``admin`` address in the ``Control`` smart contract to the ``Governor`` smart contract address which therefore will have sole privileges for setting fees and reward rates on the various registered desks.

Governance Execution Functions
==============================

Changing Crayon Protocol desk attributes is generally a two-step process that initially schedules the changes to be made and in a second step, after the passage of a public number of blocks, commits the changes. Setting distribution rates of ``XCRAY`` tokens for a particular desk, however, takes effect as soon as that desk queries the ``Control`` smart contract for an update.

The functions below are part of the Crayon Protocol ``Control`` smart contract.

Reward token distribution rates are reset and read using these functions.

.. py:function:: set_desk_rates(_desks: DynArray[address, MAX_NUM_DESKS],  _borrow_rates: DynArray[uint256, MAX_NUM_DESKS],  _deposit_rates: DynArray[uint256, MAX_NUM_DESKS])
    :noindex:

    Set new ``XCRAY`` distribution rates for lenders and borrowers at a number of desks. All three arrays must have the same length.

    * ``_desks``: The array of desks targeted for new _borrow_rates
    * ``_borrow_rates``: The array of new distribution rates for borrowers
    * ``deposit_rates``: The array of new distribution rates for lenders

.. note::

    This function will revert if the length of the arrays exceeds the number of deployed desks that were registered with this ``Control`` smart contract.

.. py:function:: get_reward_parameters(_desk: address) -> (uint256, uint256)
    :noindex:

    Return the tuple of rates of distribution of ``XCRAY`` tokens to borrowers and lenders, resp. This is a ``view`` function.

    * ``_desk``: The desk for which the rates are sought

The following functions in ``Control`` reset attributes in Crayon Protocol desks.

.. py:function:: schedule_new_fee(_horizon: uint256, _new_fee: uint256, _desk: address)
    :noindex:

    Schedules a change in the fee paid by borrowers.

    * ``_horizon``: The borrowing horizon for which a new fee is being Set
    * ``_new_fee``: The new fee value in bps. A value of 9 means a fee of 0.09%
    * ``_desk``:  The Crayon Protocol desk targeted by the change

.. py:function:: schedule_new_flashloan_fee(_new_flashloan_fee: uint256, _desk: address)
    :noindex:

    Schedules a change in the flashloan fee on a desk.

    * ``_new_flashloan_fee``: The new fee value in bps
    * ``_desk``: The Crayon Protocol desk targeted by the change

.. py:function:: schedule_new_liquidation_bonus(_new_liquidation_bonus: uint256, _desk: address)
    :noindex:

    Schedules a change in the liquidation bonus for liquidators.

    * ``_new_liquidation_bonus``: The new liquidation bonus in bps
    * ``_desk``: The Crayon Protocol desk targeted by the change

.. py:function:: commit_new_fee(_desk: address)
    :noindex:

    Start applying the already-scheduled new borrowing fee. 

    * ``_desk``: The Crayon Protocol desk for which the new fee was scheduled

.. py:function:: commit_new_flashloan_fee(_desk: address)
    :noindex:

    Start applying the already-scheduled new flashloan fee. 

    * ``_desk``: The Crayon Protocol desk for which the new flashloan fee was scheduled

.. py:function:: commit_new_liquidation_bonus(_desk: address)
    :noindex:

    Start applying the already-scheduled new liquidation bonus. 

    * ``_desk``: The Crayon Protocol desk for which the new liquidation bonus was scheduled

.. note::

    The last three functions (the "commit" functions) will revert if called before the minimum waiting period has elapsed.

Monitoring Changes
==================

Users can watch for scheduled changes by listening to events logged by functions in the ``Control`` smart contract. They are:

.. code-block:: python
    
    event NewFee:
        desk: indexed(address)
        horizon: indexed(uint256)
        new_fee: uint256
        from_block: uint256

    event NewFlashFee:
        desk: indexed(address)
        new_flash_fee: uint256
        from_block: uint256

    event NewLiquidationBonus:
        desk: indexed(address)
        new_liquidation_bonus: uint256
        from_block: uint256





