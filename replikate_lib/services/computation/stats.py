from typing import List, Union


class Stats:
    @staticmethod
    def min(values: List[Union[float, str]]) -> Union[float, str]:
        if 'T' in values or 'E' in values or len(values) == 0:
            return ''
        _min = values[0]
        for i in range(1, len(values)):
            if values[i] < _min:
                _min = values[i]
        return _min

    @staticmethod
    def max(values: List[Union[float, str]]) -> Union[float, str]:
        if 'T' in values or 'E' in values or len(values) == 0:
            return ''
        _max = values[0]
        for i in range(1, len(values)):
            if values[i] > _max:
                _max = values[i]
        return _max

    @staticmethod
    def first(values: List[Union[float, str]]) -> Union[float, str]:
        if 'T' in values or 'E' in values or len(values) == 0:
            return ''
        return values[0]

    @staticmethod
    def mean(values: List[Union[float, str]]) -> Union[float, str]:
        if 'T' in values or 'E' in values or len(values) == 0:
            return ''
        sum = 0
        for i in range(len(values)):
            sum += values[i]
        return sum / len(values)