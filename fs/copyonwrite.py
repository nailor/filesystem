import fs
import fs.multiplexing

class path(fs.multiplexing.path):
    _supercede_attributes = (
        fs.multiplexing.path._supercede_attributes + ('open', 'mkdir'))
    
    def __init__(self, bind=None, **kwargs):
        super(path, self).__init__(**kwargs)
        if bind:
            self._bound = bind
        else:
            self._bound = getattr(kwargs.get('parent',''), '_bind', None)
    
    def open(self, mode='r', *moreargs, **kwargs):
        if mode == 'w':
            self.unbind()
        ## TODO: we don't have test code for this yet
        #elif mode == 'r+':
            #with self._bind.open('r', *moreargs, **kwargs) as f:
                #self._file = f.read()
        if self._bound:
            return self._bound.open(mode, *moreargs, **kwargs)
        else:
            return super(path, self).open(mode, *moreargs, **kwargs)

    def mkdir(self, *args, **kwargs):
        self.unbind()
        return super(path, self).mkdir(*args, **kwargs)

    def rename(self, new_path):
        if self._bound:
            tmp_bound = self._bound
            self.unbind()
            self.rename(new_path)
            self.bind(tmp_bound)
            return
        if getattr(new_path, '_bound', False):
            new_path.unbind()
        ## TODO: one more scenario that should be dealt with:
        ## new_path is a file system of the binding type
        return super(path, self).rename(new_path)
        

