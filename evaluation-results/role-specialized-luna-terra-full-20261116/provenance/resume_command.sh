#!/bin/bash
set -u
cd '/home/devuser/HKU/2026-2027/Sem1/COMP7608 - Large language models/COMP7608 - Large language models - Group Project' || exit 1
logdir='/home/devuser/kora-sequential-operations/luna-terra-sequential-20261115T150108Z'
uv run python -u -m scr.agents.role_specialized.cli infer \
 --dataset-root '/home/devuser/HKU/2026-2027/Sem1/COMP7608 - Large language models/Group Project/data/bird/mini-dev-2026' \
 --result-root '/home/devuser/rubric-full-20261113' --selection-id sr-full-20261113 \
 --split all --run-id luna-terra-sequential-20261115T150108Z \
 --shard-index 1 --shard-count 1 --generator-provider chatgpt-siwc --generator-model gpt-6-luna \
 --reviewer-provider chatgpt-siwc --reviewer-model gpt-6.1-terra --prompt-variant generalized-v1 \
 --check-models --start-position 108 --replace-existing > "$logdir/resume-3aaa618.log" 2>&1
status=$?
printf '%s\n' "$status" > "$logdir/resume-3aaa618.exit"
