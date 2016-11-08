from threading import Timer


class RepeatingTimer():

    def __init__(self, interval, func, repeat=True, max_tries=None, args=(), kwargs={}):
        self.interval = interval
        self.func = func
        self.repeat = repeat
        self.max_tries = max_tries
        self.try_count = 0
        self.args = args
        self.kwargs = kwargs

        self.timer = None

    def _callback(self):
        self.try_count += 1

        self.func(*self.args, **self.kwargs)

        if self.repeat is True and (self.max_tries is None or self.try_count < self.max_tries):
            self.reset()
        else:
            self.cancel()

    def cancel(self):
        if self.timer is not None:
            self.timer.cancel()

    def start(self):
        self.timer = Timer(self.interval, self._callback)
        self.timer.start()

    def reset(self):
        self.cancel()
        self.start()
