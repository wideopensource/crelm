#pragma once

struct leibniz_state_t {
  int i;
  int d;
  float pi_over_4;
};

void leibniz_init(struct leibniz_state_t *state);

float leibniz_run(struct leibniz_state_t *state);