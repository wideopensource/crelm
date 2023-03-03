import matplotlib.pyplot as plt
from crelm import Tube
from infinite_series import InfiniteSeries, PlotAxis, BigNumbers
from enum import IntEnum

PI_REFERENCE = 3.14159265358979323846264338327950288


class AccumulatorType(IntEnum):
    FLOAT = 1,
    DOUBLE = 2,


class AlgorithmType(IntEnum):
    LEIBNIZ = 1,
    NILAKANTHA = 2,


class PiInfiniteSeries(InfiniteSeries):
    xaxis = PlotAxis(1, BigNumbers.billions(1),
                     100).fill_log().smooth().get()

    def __init__(self, type: AccumulatorType, algorithm: AlgorithmType, bug: bool = False):
        self._type = type
        self._algorithm = algorithm
        self._bug = bug

        paste = Tube(f'infinite_series_{self.name}') \
            .set_source_folder_from(__file__) \
            .add_header('pi.h') \
            .add_source('pi.c') \
            .add_macros([f'USE_{self._algorithm.name}',  f'USE_{self._type.name}']) \
            .add_macro_if(self._bug, f'USE_BUG') \
            .build().squeeze()

        state = paste.new('struct infinite_series_state_t')

        super().__init__(paste, state, PiInfiniteSeries.xaxis, PI_REFERENCE)

    @ property
    def name(self) -> str:
        return f'{self._algorithm.name}_{self._type.name}{"_BUG" if self._bug else ""}'


series = [PiInfiniteSeries(type=AccumulatorType.FLOAT,
                           algorithm=AlgorithmType.LEIBNIZ),
          PiInfiniteSeries(type=AccumulatorType.DOUBLE,
                           algorithm=AlgorithmType.LEIBNIZ),
          PiInfiniteSeries(type=AccumulatorType.FLOAT,
                           algorithm=AlgorithmType.NILAKANTHA),
          PiInfiniteSeries(type=AccumulatorType.DOUBLE,
                           algorithm=AlgorithmType.NILAKANTHA),
          PiInfiniteSeries(type=AccumulatorType.DOUBLE,
                           algorithm=AlgorithmType.NILAKANTHA, bug=True), ]

[x.init().run_timed().report() for x in series]

[plt.plot(PiInfiniteSeries.xaxis, a.result, label=a.name) for a in series]
plt.ylim([2.75, 3.5])
plt.xscale('log')
plt.legend()

plt.show()
