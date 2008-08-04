import fs
import fs.multiplexing

class path(fs.multiplexing.path):
    _supercede_attributes = (
        fs.multiplexing.path._supercede_attributes + ('open',))
    
    def __init__(self, bind):
        super(path, self).__init__()
        self._bound = bind
    
    def open(self, mode='r', *moreargs, **kwargs):
        if mode == 'w':
            self.unbind()
        ## we don't have test code for this yet
        #elif mode == 'r+':
            #with self._bind.open('r', *moreargs, **kwargs) as f:
                #self._file = f.read()
        if self._bound:
            return self._bound.open(mode, *moreargs, **kwargs)
        else:
            return super(path, self).open(mode, *moreargs, **kwargs)

    
