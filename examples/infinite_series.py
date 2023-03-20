from timeit import timeit
from crelm import Tube


class BigNumbers:
    @staticmethod
    def billions(how_many: float) -> int:
        return int(how_many * 1000 * 1000 * 1000)

    @staticmethod
    def millions(how_many: float) -> int:
        return int(how_many * 1000 * 1000)


class PlotAxis:
    def __init__(self, min: int, max: int, number_of_points: int):
        self._min = min
        self._max = max
        self._number_of_points = number_of_points
        self._points = []

    def _generate_base(self) -> float:
        return float(self._max) ** (1.0 / self._number_of_points)

    def merge(self, points: list):
        self._points = sorted(set(self._points + points))

    def fill_log(self) -> list:
        base = self._generate_base()
        self.merge([int(1 * pow(base, x))
                   for x in range(0, self._number_of_points + 1)])
        return self

    def smooth(self):
        self.merge(list(range(1, 500)) + list(range(1, 1000, 11)))
        return self

    def get(self) -> list:
        return [x for x in self._points if x >= self._min and x <= self._max]


class InfiniteSeries:
    def __init__(self, paste: Tube.Paste, state, xaxis: list, reference: float):
        self._paste = paste
        self._state = state
        self._xaxis = xaxis
        self._reference = reference

        self.result = None
        self.diff = None
        self.elapsed_seconds = None

    def init(self):
        self._paste.infinite_series_init(self._state)
        self.result = []
        return self

    def _run(self):
        for x in self._xaxis:
            p = self._paste.infinite_series_run(self._state, int(x))
            self.result.append(p)
        return self

    def run(self):
        self.elapsed_seconds = round(timeit(stmt=self._run, number=1), 3)
        return self

    def analyse(self):
        self.diff = [abs(x - self._reference) for x in self.result]
        return self

    def report(self):
        value = self.result[-1]
        error = self._reference - value
        elapsed = self.elapsed_seconds
        print(f'{self.name}: {value}, error: {(error):.2e}, time: {elapsed}')
        return self
