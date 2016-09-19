from threading import Timer


class RepeatingTimer():

    def __init__(self, interval, func, repeat=True, *args, **kwargs):
        self.interval = interval
        self.func = func
        self.repeat = repeat
        self.args = args
        self.kwargs = kwargs

        self.timer = None

    def _callback(self):
        self.func(*self.args, **self.kwargs)

        if self.repeat is True:
            self.start()
        else:
            self.cancel()

    def cancel(self):
        self.timer.cancel()

    def start(self):
        self.timer = Timer(self.interval, self._callback)
        self.timer.start()
