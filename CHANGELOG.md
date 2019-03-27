History
=======

0.5.9 (March 27th, 2019)
-------------------------

0.5.8 (March 26th, 2019)
-------------------------
* Upgrade to keeper-contracts 0.8.8.


0.5.7 (March 25th, 2019)
-------------------------
* Unify authentication and publicKey parameters in the ddo.


0.5.6 (March 22nd, 2019)
-------------------------
* Upgrade to the changes in the did registry contract in version 0.8.7.

0.5.5 (March 21st, 2019)
-------------------------
* Fix issue with the validation of the signature.
* Add docstrings missed.

0.5.4 (March 20th, 2019)
-------------------------
* Use personal_sendTransaction to execute smart contract functions to avoid having to unlock account before each transaction.
* Improved error handling.
* Better control of http requests connection pool.

0.5.3 (March 18th, 2019)
------------------------
* Update to keeper 0.8.6

0.5.2 (March 14th, 2019)
-------------------------
* This release works with keeper v0.8.5 which automatically propses/approves the agreement template. Brizo and squid-py should work without the need for worring about approving the agreement template.

0.5.1 (March 13th, 2019)
-------------------------
* Small bug fixed.

0.5.0 (March 6th, 2019)
-------------------------
* Working with keeper-contracts v0.8.1.
* Update with the new squid API.

0.4.4 (February 21st, 2019)
-------------------------
* Change log level in the event listener.

0.4.3 (February 19th, 2019)
-------------------------
* Unlock missed account to avoid Nile error

0.4.2 (February 7th, 2019)
-------------------------
* Secret store bug fixed

0.4.1 (February 6th, 2019)
-------------------------
* Include template in the distribution

0.4.0 (February 6th, 2019)
-------------------------
* This release implements the latest v0.1 squid-api.

0.3.3 (February 6th, 2019)
-------------------------
* Create checksum in the register_asset method

0.3.2 (January 30th, 2019)
-------------------------
* Fixing in the secret-store
* Remove circular dependencies

0.3.1 (January 30th, 2019)
-------------------------
* Support changes in OEP-8

0.3.0 (January 29th, 2019)
-------------------------
* Enable squid to run with keeper-contracts v0.6.x

0.2.24 (January 21st, 2019)
---------------------------
* Remove dids in the services

0.2.21 (January 15th, 2019)
---------------------------
* Fixes a bug that breaks resolving assets in brizo.

0.2.17 (December 18th, 2019)
---------------------------
* Unify DID format across different languages.
* Move unlock_account to the Account class
* Detect existing service agreement and raise error before executing the agreement on-chain
* Raise error in execute_service_agreement when consumer signature is invalid to allow Brizo to provide more accurate error message
* Simplify imports

0.2.14 (December 7th, 2019)
---------------------------
* New docker images need this update.

0.2.11 (November 28th, 2019)
---------------------------
Progress in Service Level Agreements and consume workflow.

This version is still to be integration tested.

0.2.7 (November 19th, 2019)
---------------------------
* Fix, include .json service agreement template and path handling

0.2.6 (November 19th, 2019)
---------------------------
* Refactor of Service Level Agreement flow
* Cleanup, bugfixes

0.2.5 (November 16th, 2019)
---------------------------
* Service agreement handlers
* Access conditions
* General refactoring

0.2.4 (November 16th, 2019)
---------------------------
* Minor fixes to the version dependencies (web3==4.5.0, and including all sub-packages).

0.2.1 (October 30th, 2019)
---------------------------
* Following the new squid API.
* Complete refactor of methods.

0.1.3 (October 12th, 2019)
---------------------------
* Implementation of the new API methods
* First squid useful version







