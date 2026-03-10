---
name: matlab-run-analyze-fix
description: Use when the task involves running MATLAB scripts or functions, capturing console output, saving generated figures, inspecting resulting plots or metrics, diagnosing failures, and iteratively fixing MATLAB code. Trigger for MATLAB simulation debugging, algorithm verification, figure-based analysis, batch reruns, and any request to automate a run-analyze-fix loop for `.m` files.
---

# MATLAB Run Analyze Fix

Use this skill to execute MATLAB code, persist generated figures, inspect outputs, and iterate on MATLAB fixes until the requested behavior is correct.

## Workflow

1. Verify MATLAB is available with `Get-Command matlab`.
2. Prefer the bundled script `scripts/run_matlab_batch.ps1` instead of calling `matlab -batch` directly.
3. Always run with a writable MATLAB preferences directory inside the working tree.
4. Save figures for every meaningful run into a stable output folder.
5. Use `latest` as the current-run register.
6. Before each new run, archive the previous `latest` contents into `results/MMdd/HHmmss/`.
7. Inspect both console output and saved images before changing code again.
8. When MATLAB fails for environment reasons, stop and report the blocker instead of guessing.

## Standard run loop

1. Identify the exact MATLAB entrypoint to run.
2. Use `scripts/run_matlab_batch.ps1` with:
   - `-WorkDir` set to the repo or experiment folder
   - `-Command` set to the MATLAB entrypoint or statements to run
   - `-SaveFigures` when plots matter
   - optional `-OutputDir` only when the user needs a custom location
3. Read `latest/matlab_output.log`.
4. Open saved figures under `latest/` for visual analysis.
5. Patch the MATLAB code.
6. Re-run the same command.
7. Compare the new `latest` artifacts with the archived run under `results/MMdd/HHmmss/`.

## Commands

Run a script and save figures to the rolling `latest` directory:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_matlab_batch.ps1 -WorkDir "D:\repo" -Command "run_repro_all" -SaveFigures
```

Run with an explicit output directory only when needed:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_matlab_batch.ps1 -WorkDir "D:\repo" -Command "my_function" -OutputDir "D:\repo\output\matlab-runs\custom-test"
```

## Output layout

Default layout under the MATLAB work directory:

```text
output/
  matlab-runs/
    latest/
      matlab_output.log
      figure_01.png
      figure_02.png
      ...
    results/
      0309/
        154210/
          matlab_output.log
          figure_01.png
          ...
```

Rules:
- `latest/` always contains the current run
- if `latest/` already contains files, they are moved into `results/MMdd/HHmmss/` before the next run starts
- use the archived date folder as the historical register for prior runs on that day

## Figure handling

- Use the bundled `scripts/save_open_figures.m` helper to save all open MATLAB figures.
- Save `.png` files for inspection and `.fig` only when future MATLAB-side editing is needed.
- Treat `latest/` as disposable current state and `results/MMdd/HHmmss/` as retained history.

## Analysis rules

- Treat console errors as primary evidence.
- Treat saved figures as algorithm evidence.
- Call out mismatches between configured frequencies, domains, and plotted results.
- When a plot looks wrong, check frequency-axis conventions, scaling reference, and where in the chain suppression is applied.
- For signal-processing tasks, compare:
  - clean baseline
  - interfered signal
  - suppressed output
  - detection mask or beam pattern
  - archived previous run versus current `latest`

## Environment blockers

If MATLAB fails due to license or MathWorks service communication, report that explicitly and do not claim the code was verified.

Common blockers and remedies are documented in `references/troubleshooting.md`.

## Bundled resources

- `scripts/run_matlab_batch.ps1`: preferred wrapper for running MATLAB robustly on Windows
- `scripts/save_open_figures.m`: save all open figures to disk after a run
- `references/troubleshooting.md`: common MATLAB runtime blockers and what they mean
