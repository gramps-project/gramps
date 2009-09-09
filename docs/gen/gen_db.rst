##########################
The :mod:`gen.db` Module
##########################

Contents:

.. automodule:: gen.db

*****************************
Base object
*****************************

GrampsDbBase
====================================
.. automodule:: gen.db.base
.. autoclass:: GrampsDbBase
   :members:
   :undoc-members:
   :show-inheritance:

*****************************
Read object
*****************************

GrampsDbRead
====================================
.. automodule:: gen.db.read
.. autoclass:: GrampsDbRead
   :members:
   :show-inheritance:

*****************************
Write object
*****************************

GrampsDbWrite
====================================
.. automodule:: gen.db.write
.. autoclass:: GrampsDBDir
   :members:
   :undoc-members:
   :show-inheritance:

*****************************
Cursor
*****************************

GrampsCursor
====================================
.. automodule:: gen.db.cursor
.. autoclass:: GrampsCursor
   :members:
   :undoc-members:
   :show-inheritance:

*****************************
BSDDB txn
*****************************

BSDDBtxn
====================================
.. automodule:: gen.db.bsddbtxn
.. autoclass:: BSDDBTxn
   :members:
   :undoc-members:
   :show-inheritance:

*****************************
Txn object
*****************************

GrampsDbTxn
====================================
.. automodule:: gen.db.txn
.. autoclass:: GrampsDbTxn
   :members:
   :undoc-members:
   :show-inheritance:

*****************************
Undoredo object
*****************************

GrampsDbUndo
====================================
.. automodule:: gen.db.undoredo
.. autoclass:: GrampsDbUndo
   :members:
   :undoc-members:
   :show-inheritance:

GrampsDbUndoList
====================================

.. autoclass:: GrampsDbUndoList
   :members:
   :undoc-members:
   :show-inheritance:

GrampsDbUndoBSDDB
====================================

.. autoclass:: GrampsDbUndoBSDDB
   :members:
   :undoc-members:
   :show-inheritance:

*****************************
Dbconst object
*****************************

DbConst
====================================
.. automodule:: gen.db.dbconst
   :members:

*****************************
Exceptions object
*****************************

GrampsDbException
====================================
.. automodule:: gen.db.exceptions
.. autoclass:: GrampsDbException
   :members:
   :undoc-members:
   :show-inheritance:

GrampsDbWriteFailure
====================================

.. autoclass:: GrampsDbWriteFailure
   :members:
   :undoc-members:
   :show-inheritance:

FileVersionError
====================================   

.. autoclass:: FileVersionError
   :members:
   :undoc-members:
   :show-inheritance:

FileVersionDeclineToUpgrade
====================================

.. autoclass:: FileVersionDeclineToUpgrade
   :members:
   :undoc-members:
   :show-inheritance:

*****************************
Upgrade utilities
*****************************

.. automodule:: gen.db.upgrade
    :members:
    :undoc-members:
