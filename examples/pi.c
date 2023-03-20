#include "pi.h"
#include <stdio.h>

// foss: algorithms similar to (possibly from):
// https://en.wikipedia.org/wiki/Pi
// https://en.wikipedia.org/wiki/Leibniz_formula_for_%CF%80

#define ACCUMULATOR_CAST(N) ((ACCUMULATOR_T)(N))

#ifdef USE_LEIBNIZ
#define INITIAL_NUMBER_OF_ITERATIONS_COMPLETED 0
#define INITIAL_ACCUMULATOR 0
#define NUMERATOR 4
#define ALT_SIGN(N) (-(N))
#define IMPL(A, I, S, D, ...) A += ((S) / ((D)-1))
#define RESULT(A) (A)
#endif

#ifdef USE_NILAKANTHA
#define INITIAL_NUMBER_OF_ITERATIONS_COMPLETED 1
#define INITIAL_ACCUMULATOR 3
#define NUMERATOR 4
#define ALT_SIGN(N) (-(N))
#define IMPL(A, I, S, D, ...) A += ((S) / (((D) * ((D) + 1) * ((D) + 2))))
#define RESULT(A) (A)
#endif

#ifdef USE_EULER
#define INITIAL_NUMBER_OF_ITERATIONS_COMPLETED 1
#define INITIAL_ACCUMULATOR 1
#define NUMERATOR 1
#define ALT_SIGN(N) ((N))
#define IMPL(A, I, S, D, T, ...)                                               \
  T *= (ACCUMULATOR_CAST(I)) / (1 + (D));                                      \
  A += T
#define RESULT(A) (A * 2)
#endif

void infinite_series_init(struct infinite_series_state_t *state) {
  state->number_of_iterations_completed =
      INITIAL_NUMBER_OF_ITERATIONS_COMPLETED;
  state->accumulator = ACCUMULATOR_CAST(INITIAL_ACCUMULATOR);
  state->temp = 1;
}

ACCUMULATOR_T infinite_series_run(struct infinite_series_state_t *state,
                                  unsigned long number_of_iterations) {
  ACCUMULATOR_T acc = state->accumulator;
  ACCUMULATOR_T temp = state->temp;
  unsigned long i = state->number_of_iterations_completed;

  ACCUMULATOR_T s = ACCUMULATOR_CAST(NUMERATOR) * (i & 1 ? 1 : ALT_SIGN(1));

#ifdef USE_OVERFLOW_BUG
  for (int d = i * 2; i < number_of_iterations; ++i, s = -s, d += 2)
#else
  for (unsigned long d = i * 2; i < number_of_iterations; ++i, s = -s, d += 2)
#endif
  {
    IMPL(acc, i, s, d, temp);
  }

  state->accumulator = acc;
  state->temp = temp;
  state->number_of_iterations_completed = i;

  return RESULT(state->accumulator);
}
