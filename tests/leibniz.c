#include "leibniz.h"

// https://en.wikipedia.org/wiki/Leibniz_formula_for_%CF%80

void leibniz_init(struct leibniz_state_t *state) {
  state->i = 0;
  state->d = 1;
  state->pi_over_4 = 0.0f;
}

float leibniz_run(struct leibniz_state_t *state) {

  state->pi_over_4 += (((state->i++ & 1) << 1) - 1) * -1.0f / state->d;

  state->d += 2;

  return state->pi_over_4 * 4;
}
