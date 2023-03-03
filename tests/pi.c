#include "pi.h"
#include <stdio.h>

// https://en.wikipedia.org/wiki/Pi
// https://en.wikipedia.org/wiki/Leibniz_formula_for_%CF%80

#define ACCUMULATOR_CAST(N) ((ACCUMULATOR_T)(N))

#ifdef USE_LEIBNIZ
#define INITIAL_NUMBER_OF_ITERATIONS_COMPLETED 0
#define INITIAL_ACCUMULATOR 0
#define IMPL(S, D) ((S) / ((D)-1))
#endif

#ifdef USE_NILAKANTHA
#define INITIAL_NUMBER_OF_ITERATIONS_COMPLETED 1
#define INITIAL_ACCUMULATOR 3
#define IMPL(S, D) ((S) / (((D) * ((D) + 1) * ((D) + 2))))
#endif

void infinite_series_init(struct infinite_series_state_t *state) {
  state->number_of_iterations_completed =
      INITIAL_NUMBER_OF_ITERATIONS_COMPLETED;
  state->accumulator = ACCUMULATOR_CAST(INITIAL_ACCUMULATOR);
}

ACCUMULATOR_T infinite_series_run(struct infinite_series_state_t *state,
                                  unsigned long number_of_iterations) {
  ACCUMULATOR_T acc = state->accumulator;
  unsigned long i = state->number_of_iterations_completed;

  ACCUMULATOR_T s = ACCUMULATOR_CAST(4) * (i & 1 ? 1 : -1);

#ifdef USE_BUG
  for (int d = i * 2; i < number_of_iterations; ++i, s = -s, d += 2)
#else
  for (unsigned long d = i * 2; i < number_of_iterations; ++i, s = -s, d += 2)
#endif
  {
    acc += IMPL(s, d);
  }

  state->accumulator = acc;
  state->number_of_iterations_completed = i;

  return state->accumulator;
}
