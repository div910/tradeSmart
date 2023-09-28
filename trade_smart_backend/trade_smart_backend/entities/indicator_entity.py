class IndicatorEntity:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.start_time = kwargs.get('start_time')
        self.time_delta = kwargs.get('time_delta')
        self.interval = kwargs.get('interval')
        self.data = kwargs.get('data')

    def populate_data(self):
        self.data = "data Populated"