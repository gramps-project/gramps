
class LongOpStatus(object):
    def __init__(self):
	self._cancel = False

    def cancel(self):
	self._cancel = True

    def shouldCancel(self):
	return self._cancel

class CursorIterator(object):
    
    def __init__(self,db,cursor):
	self._db = db
	self._cursor = cursor
	self._status = LongOpStatus()

    def __iter__(self):
	try:
	    # Emit start signal
	    self._db.emit('long-op-start',(self._status,))

	    first = self._cursor.first()
	    if first: 
		yield first

		next = self._cursor.next()
		while next:
		    yield next

		    # check for cancel
		    #if self._status.shouldCancel():
		    #    raise GrampsDbUserCancel

		    # emit heartbeat
		    self._db.emit('long-op-heartbeat')
		    next = self._cursor.next()

	    # emit stop signal
	    self._db.emit('long-op-end')
	    self._cursor.close()
	    raise StopIteration
	except:
	    self._cursor.close()
	    self._db.emit('long-op-end')
	    raise
