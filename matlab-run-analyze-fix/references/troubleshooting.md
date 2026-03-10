# MATLAB troubleshooting

## Writable preferences directory

Symptom:
- MATLAB reports that the preferences directory is not writable.

Response:
- Set `MATLAB_PREFDIR` to a writable folder inside the repo or experiment directory.
- Prefer using `scripts/run_matlab_batch.ps1`, which does this automatically.

## MathWorks service or license failure

Symptom:
- MATLAB reports service communication errors such as `5202`.

Response:
- Treat this as an environment blocker.
- Do not claim runtime verification succeeded.
- Report that the code changes were made but MATLAB verification could not be completed because the local MATLAB license/service could not be reached.

## Figures not saved

Symptom:
- MATLAB runs but no figure artifacts are produced.

Response:
- Re-run using `-SaveFigures`.
- Confirm the code actually creates figures.
- If figures are created conditionally, inspect the relevant branch conditions.

## Shared workspace issue with `run`

Symptom:
- A parent script loses variables after calling a child script with `run`.

Response:
- Remember that `run` executes in the caller workspace.
- If child scripts use `clear`, recompute required parent variables after each `run`, or refactor the scripts into functions.

## Output history layout

Default behavior:
- Current run goes to `output/matlab-runs/latest/`
- Previous contents of `latest/` are moved to `output/matlab-runs/results/MMdd/HHmmss/`

Use this when:
- you want a stable place to inspect the latest figures
- you want prior runs preserved for same-day comparison
