 
.. index:: _providers

.. _providers:

Providers 
#########

The Crayon Protocol team decided to leave it to third parties to build front-ends to access the protocol's desks. Providers are incentivized by letting them specify and keep a percentage of reward tokens earned by their users. When minting reward tokens for a user, the protocol awards that percentage of the rewards to the provider the user used.

The following functions in the C Control smart contract are available for provider interaction.

.. py:function:: register_provider(_provider_percentage: uint256)

    Register ``msg.sender`` as a provider (of front end in most common use case). Reverts if ``msg.sender`` is already registered or had registered in the past and then unregistered.

    * ``_provider_percentage``: The percentage of reward tokens earned by its users that the provider will keep

.. note::

    A provider that un-registers cannot later re-register using its previous address but can re-register using a new address. This is meant to protect users from abusive behavior. 

.. py:function:: unregister_provider()

    Unregister ``msg.sender`` as a provider. Reverts if ``msg.sender`` is not already registered as a provider. Provider still earns rewards from activity that happened prior to un-registering.

.. py:function:: is_registered_provider(_provider: address) -> bool

    Returns ``True`` or ``False``. ``True`` means ``_provider`` has registered as a provider and has specified the percentage of its users' reward tokens that it will keep. This is a ``view`` function.

    * ``_provider``: The address

.. py:function:: provider_percentage(_provider: address) -> uint256
    
    Return the percentage of the cumulated reward tokens a provider keeps. A return value of 5 means the provider keeps 5% of its users' rewards. This is a ``view`` function.

    * ``_provider``: The address of the provider

    