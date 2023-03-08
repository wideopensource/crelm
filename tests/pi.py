import matplotlib.pyplot as plt
from crelm import Tube
from infinite_series import InfiniteSeries, PlotAxis, BigNumbers
from enum import IntEnum


class AccumulatorType(IntEnum):
    FLOAT = 1,
    DOUBLE = 2,


class AlgorithmType(IntEnum):
    LEIBNIZ = 1,
    NILAKANTHA = 2,
    EULER = 3,


class BugType(IntEnum):
    NONE = 0,
    OVERFLOW = 1,


class PiInfiniteSeries(InfiniteSeries):
    _PI_REFERENCE = 3.14159265358979323846264338327950288
    xaxis = PlotAxis(1, BigNumbers.millions(100),
                     100).fill_log().smooth().get()

    def __init__(self, type: AccumulatorType, algorithm: AlgorithmType, bug: BugType = BugType.NONE):
        self._type = type
        self._algorithm = algorithm
        self._bug = bug

        paste = Tube(f'infinite_series_{self.name}') \
            .set_source_folder_from(__file__) \
            .add_header('pi.h') \
            .add_source('pi.c') \
            .add_macros([f'USE_{self._algorithm.name}',  f'USE_{self._type.name}']) \
            .add_macro_if(BugType.OVERFLOW == self._bug, f'USE_OVERFLOW_BUG') \
            .build().squeeze()

        state = paste.new('struct infinite_series_state_t')

        super().__init__(paste, state, PiInfiniteSeries.xaxis, PiInfiniteSeries._PI_REFERENCE)

    @property
    def type(self) -> AccumulatorType:
        return self._type

    @property
    def algorithm(self) -> AlgorithmType:
        return self._algorithm

    @ property
    def name(self) -> str:
        return f'{self._algorithm.name}_{self._type.name}{"_OVERFLOW" if BugType.OVERFLOW==self._bug else ""}'

    @property
    def bug(self) -> BugType:
        return self._bug


series = [PiInfiniteSeries(type=AccumulatorType.FLOAT,
                           algorithm=AlgorithmType.LEIBNIZ),
          PiInfiniteSeries(type=AccumulatorType.DOUBLE,
                           algorithm=AlgorithmType.LEIBNIZ),
          PiInfiniteSeries(type=AccumulatorType.FLOAT,
                           algorithm=AlgorithmType.EULER),
          PiInfiniteSeries(type=AccumulatorType.DOUBLE,
                           algorithm=AlgorithmType.EULER),
          PiInfiniteSeries(type=AccumulatorType.FLOAT,
                           algorithm=AlgorithmType.NILAKANTHA),
          PiInfiniteSeries(type=AccumulatorType.DOUBLE,
                           algorithm=AlgorithmType.NILAKANTHA),
          PiInfiniteSeries(type=AccumulatorType.DOUBLE,
                           algorithm=AlgorithmType.NILAKANTHA, bug=BugType.OVERFLOW)]

[x.init().run().analyse().report() for x in series]

plot_colours = {AlgorithmType.LEIBNIZ: 'blue',
                AlgorithmType.NILAKANTHA: 'red',
                AlgorithmType.EULER: 'yellow'}

plot_linestyles = {(AccumulatorType.FLOAT, BugType.NONE,): 'dashed',
                   (AccumulatorType.DOUBLE, BugType.NONE,): None,
                   (AccumulatorType.FLOAT, BugType.OVERFLOW,): 'dotted',
                   (AccumulatorType.DOUBLE, BugType.OVERFLOW,): 'dotted'}

_, (estimates, diffs,) = plt.subplots(1, 2)

[estimates.plot(PiInfiniteSeries.xaxis, a.result, label=a.name,
                linestyle=plot_linestyles[(a.type, a.bug,)],
                color=plot_colours[a.algorithm]) for a in series]
estimates.set_xscale('log')
estimates.set_ylim([2.75, 3.5])
estimates.legend(loc="lower right")

[diffs.plot(PiInfiniteSeries.xaxis, a.diff, label=a.name,
            linestyle=plot_linestyles[(a.type, a.bug,)],
            color=plot_colours[a.algorithm]) for a in series]
diffs.set_xscale('log')
diffs.set_yscale('log')

plt.show()
