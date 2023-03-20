from matplotlib import pyplot as plt
from crelm import Factory
from infinite_series import InfiniteSeries, PlotAxis, BigNumbers
from enum import IntEnum

print("Initialising libcrelm factory")

factory = Factory()


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
    number_of_iterations = 1

    def __init__(self, type: AccumulatorType, algorithm: AlgorithmType, bug: BugType = BugType.NONE):
        self._type = type
        self._algorithm = algorithm
        self._bug = bug

        x_axis = PlotAxis(1, PiInfiniteSeries.number_of_iterations,
                          100).fill_log().smooth().get()

        paste = factory.create_Tube(f'infinite_series_{self.name}') \
            .set_source_folder_from(__file__) \
            .add_header_file('pi.h') \
            .add_source_file('pi.c') \
            .add_macros([f'USE_{self._algorithm.name}',  f'USE_{self._type.name}']) \
            .add_macro_if(BugType.OVERFLOW == self._bug, f'USE_OVERFLOW_BUG') \
            .squeeze()

        state = paste.new('struct infinite_series_state_t')

        super().__init__(paste, state, x_axis, PiInfiniteSeries._PI_REFERENCE)

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


PiInfiniteSeries.number_of_iterations = BigNumbers.billions(1)

series = [PiInfiniteSeries(type=AccumulatorType.FLOAT,
                           algorithm=AlgorithmType.LEIBNIZ),
          PiInfiniteSeries(type=AccumulatorType.DOUBLE,
                           algorithm=AlgorithmType.LEIBNIZ),
          PiInfiniteSeries(type=AccumulatorType.FLOAT,
                           algorithm=AlgorithmType.NILAKANTHA),
          PiInfiniteSeries(type=AccumulatorType.DOUBLE,
                           algorithm=AlgorithmType.NILAKANTHA),
          PiInfiniteSeries(type=AccumulatorType.FLOAT,
                           algorithm=AlgorithmType.EULER),
          PiInfiniteSeries(type=AccumulatorType.DOUBLE,
                           algorithm=AlgorithmType.EULER),
          PiInfiniteSeries(type=AccumulatorType.DOUBLE,
                           algorithm=AlgorithmType.NILAKANTHA, bug=BugType.OVERFLOW)]

print(
    f"running {len(series)} algorithms over {PiInfiniteSeries.number_of_iterations} iterations")
[x.init().run().analyse().report() for x in series]

plot_colours = {AlgorithmType.LEIBNIZ: 'blue',
                AlgorithmType.NILAKANTHA: 'red',
                AlgorithmType.EULER: 'yellow'}

plot_linestyles = {(AccumulatorType.FLOAT, BugType.NONE,): 'dashed',
                   (AccumulatorType.DOUBLE, BugType.NONE,): None,
                   (AccumulatorType.FLOAT, BugType.OVERFLOW,): 'dotted',
                   (AccumulatorType.DOUBLE, BugType.OVERFLOW,): 'dotted'}

fig, (estimates, errors,) = plt.subplots(1, 2)

[estimates.plot(a._xaxis, a.result, label=a.name,
                linestyle=plot_linestyles[(a.type, a.bug,)],
                color=plot_colours[a.algorithm]) for a in series]
estimates.set_xscale('log')
estimates.set_ylim([2.75, 3.5])
estimates.set_title('Pi Estimates')
estimates.set_xlabel('Number of iterations (log)')
estimates.set_ylabel('Estimate')
estimates.legend(loc="lower right")

[errors.plot(a._xaxis, a.diff, label=a.name,
             linestyle=plot_linestyles[(a.type, a.bug,)],
             color=plot_colours[a.algorithm]) for a in series]
errors.set_xscale('log')
errors.set_yscale('log')
errors.set_title('Pi Errors')
errors.set_xlabel('Number of iterations (log)')
errors.set_ylabel('Absolute error (log)')

plt.subplots_adjust(left=0.06, right=0.97, top=0.94, bottom=0.1)
fig.set_size_inches((10.24, 7.68,))

plt.savefig("pi.png", dpi=100)
plt.show()
