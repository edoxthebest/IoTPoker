#!/bin/sh
set -eu

mode="${1:-case-study}"

case "$mode" in
  case-study)
    python case_study_demo.py
    ;;
  benchmark)
    python real_world_benchmark.py tests/policies/policy_benchmark/FLAW1 -c 30 --seq 20 40 60 80 100 120 140 160 180 200 220 240 258 -C
    ;;
  benchmark-solvers)
    python real_world_benchmark_solvers.py tests/policies/policy_benchmark/FLAW1
    ;;
  *)
    echo "Usage: docker run <image> [case-study|benchmark|benchmark-solvers]" >&2
    exit 1
    ;;
esac
