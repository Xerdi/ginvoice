
__SIGNAL_HANDLERS__ = dict()


def signal(name=None, meta_data=None):

    def _decorator(func):

        def _executor(*args):
            if meta_data:
                return func(*args, meta_data)
            else:
                return func(*args)

        global __SIGNAL_HANDLERS__
        __SIGNAL_HANDLERS__[name or func.__name__] = _executor

        return _executor
    return _decorator


def connect_signal(builder, gobject, signal_name, handler_name, connect_object, flags, user_data):
    handler = __SIGNAL_HANDLERS__[handler_name]
    if connect_object:
        gobject.connect(signal_name, handler, connect_object)
    else:
        gobject.connect(signal_name, handler)
