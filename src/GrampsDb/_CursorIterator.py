from _LongOpStatus import LongOpStatus

class CursorIterator(object):
    
    def __init__(self,db,cursor):
	self._db = db
	self._cursor = cursor
	#self._status = LongOpStatus(total_steps=cursor.get_length(),interval=10)
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
		    #if self._status.should_cancel():
		    #    raise GrampsDbUserCancel

		    # emit heartbeat
		    self._status.heartbeat()
		    next = self._cursor.next()

	    # emit stop signal
	    self._status.end()
	    self._cursor.close()
	    raise StopIteration
	except:
	    # Not allowed to use 'finally' because we 
	    # yeild inside the try clause.
	    self._cursor.close()
	    self._status_end()
	    raise
    
