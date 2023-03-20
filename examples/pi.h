#pragma once

#ifdef USE_FLOAT
#define ACCUMULATOR_T float
#endif

#ifdef USE_DOUBLE
#define ACCUMULATOR_T double
#endif

struct infinite_series_state_t {
  unsigned long number_of_iterations_completed;
  ACCUMULATOR_T accumulator;
  ACCUMULATOR_T temp;
};

void infinite_series_init(struct infinite_series_state_t *state);

ACCUMULATOR_T infinite_series_run(struct infinite_series_state_t *state,
                                  unsigned long number_of_iterations);