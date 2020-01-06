class Timeout:
    def __init__(self, duration: int, unit: str):
        self.duration = duration
        if unit not in ['SECONDS', 'MINUTES', 'HOURS', 'DAYS']:
            raise ValueError('invalid unit {0}'.format(unit))
        self.unit = unit

    def to_seconds(self):
        coefficient = 1
        if self.unit != 'SECONDS':
            coefficient *= 60
            if self.unit != 'MINUTES':
                coefficient *= 60
                if self.unit != 'HOURS':
                    coefficient *= 24
        return coefficient * self.duration