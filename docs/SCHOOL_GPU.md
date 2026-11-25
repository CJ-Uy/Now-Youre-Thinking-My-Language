# School GPU setup

Verified on 10 November 2026 for the Opus pilot: 33 original tests, dependency checks, locked-data audit, unchanged-model inference, two LoRA updates and adapter inference all pass. The subsequent queue passed 43 tests locally and remotely. The authorized Steps 1–7 completed on `ughost03` at 00:46 on 11 November (+08:00); the pipeline is now `awaiting_human_review` at Step 8. See the [screening report](pilots/2026-11-10-opus55-screening.md) and [experiment log](EXPERIMENT_LOG.md). No reviewed series or official test has run.

The [course cluster guide](https://github.com/hkust-nlp/COMP4901B-LLMs/blob/main/assignment2/school_cluster.md) documents the head node, allocator and RTX 2080 Ti compute nodes. The Self Study chat and its 3 November handoff confirmed the previously working method: Windows PowerShell launches Ubuntu WSL's SSH client, using an interactive CSE UG UNIX password prompt. Do not put passwords in project files.

## Connect

Run from PowerShell:

```powershell
rtk proxy wsl -d Ubuntu --exec ssh cjuy@ugcnode01.cse.ust.hk
```

On the head node, run `check_usage`, then `ssh ughostXX` using the node it permits. Type `bash` on the compute node. Only one compute node may be occupied at a time; release it when finished. Run models and installations on the compute node, not the head node. The allocation can change between sessions.

This setup used `ughost03`. Earlier connections to `ughost15` did not persist, and a subsequent allocation check returned `ughost03`. A real interactive compute session (`ssh -tt`) remained usable; a connection with `-N` did not. The verified automation route uses these WSL control sockets:

- Head: `/home/charl/.ssh/comp4901b-pilot/head-20261110.sock`
- Compute: `/home/charl/.ssh/comp4901b-pilot/compute-20261110.sock`

They are temporary sessions, not permanent credentials. Direct compute connections use the head's `nc %h %p` proxy; ordinary SSH forwarding is disabled by the cluster. Reconnect and check allocation if the sockets have expired. The existing Self Study helper `tmp/ssh-tty-bridge.py` was used to expose SSH's interactive password prompt to the terminal tools; normal interactive SSH does not need that helper.

## Project location and environment

```text
/store/cjuy/comp4901b-pilot-20261110/repo
```

The enclosing directory is private (mode 700). The guide's `/store/comp4901b` directory was not writable by this account, so the setup uses the existing private `/store/cjuy` location also used for earlier coursework. It does not modify the HW2 or HW3 environments.

- Branch: `opus55-pilot-pipeline`, source commit `615956bc60a58326719a5d60af574b8a848a01a3`.
- Source transferred with a Git bundle, without committing or pushing. The current README, this guide, team guide and experiment log were copied as a documented working-tree overlay.
- Python 3.12.10, installed privately with uv 0.13.7. Project environment: `repo/.venv`.
- Dependencies installed from the unchanged `requirements.txt` and `requirements-lock.txt`. Linux's additional dependencies are recorded in the verification's `requirements-linux.txt`.
- GPU observed: RTX 2080 Ti, 11 GB; driver 610.57.04; CUDA runtime used by PyTorch: 12.8.
- The unchanged runtime chooses BF16 because `torch.cuda.is_bf16_supported()` returns true. The native-only check returns false on compute capability 7.5: this is emulated BF16 support. Do not silently switch precision or compare timing against the laptop as though hardware were identical.
- The pinned Qwen3-0.6B revision is cached under `repo/.cache/huggingface`. No dataset download or `research prepare` was needed.

The private input transfer contains 450 files: locked train/calibration/development inputs, both Opus imports, relevant teacher prompts/raw outputs/provenance, human-review records, local preflight evidence and the two documentation overlays. Every file and the source bundle were hash-checked before and after extraction. Personal recordings, unrelated outputs, credentials, model weights and existing experiment adapters were not part of that input archive.

## Verification and continuation

Setup evidence on the server:

```text
repo/artifacts/school-setup/verification-20261110/
repo/artifacts/preflight/opus55-school-20261110/
repo/artifacts/runs/school-smoke-unchanged-20261110/
repo/artifacts/runs/school-smoke-original-20261110/
repo/artifacts/runs/school-smoke-adapter-20261110/
```

The smoke procedure runs the offline tests, doctor, dependency checks, data preflight, one development example at budget 128, two original-solution optimizer updates, and the same one-example evaluation with that smoke adapter. Runs are serial. A smoke adapter cannot be used for official testing. Check `verification.json` and the prediction records for completion; command exit status alone does not establish successful generation.

Both one-example evaluations completed without runtime errors or truncation. The unchanged output was unparseable (count 1); the adapter output was parseable (count 0 unparseable). Both raw outputs are retained. The three model commands took 48.14 seconds of wall time including loading; the two training updates used 1.85 GB peak allocated VRAM. These checks establish that the pipeline executes, not research accuracy or a school-versus-laptop speed comparison. Copies are saved locally under the same artifact paths; the private handoff archive is `artifacts/handoff/2026-11-10-opus55-school-setup.zip`.

From the remote repository root, Step 1 is:

```bash
.venv/bin/python -m research score --split calibration --candidates artifacts/rewrites/opus55-pilot-calibration-20261110/candidates.jsonl --output artifacts/scores/opus55-calibration-a2-20261110
```

Follow [the original pipeline instruction](../prompts/codex-pilot-pipeline.md), including its stop points and pre-registered rules. Keep the entire compared series on the same school hardware/runtime and record any node change. Calibration produced `configs/pilot-opus55.json` with length penalty 1.0 and two feedback attempts; its SHA-256 is `4c2cce25f583d483688ba9013809c054509a8cfcfb9e3fe15d6e32fb9a305604`. `configs/pilot.json` stays unchanged. Existing laptop results and school smoke checks are separate evidence. No official-test access or freeze is authorized by setup. The command above is historical: its output already exists, so do not rerun into that directory.

Archive new outputs privately after each phase and copy them back to the laptop. Git does not back up the data, adapters or predictions, and a persistent SSH window is not a job checkpoint or backup.

## Unattended screening queue, 10 November

The one-shot `python -m scripts.run_opus_screening` continuation waits for the already-running Step 1, then runs Steps 2–7 serially. Do not launch it a second time. It saves exact commands, logs, timestamps and an atomic `status.json` under `artifacts/pipeline/opus55-school-screening-20261110/`. It refuses existing outputs, changed source/configuration and competing GPU processes; failed commands or non-reproducing stability attempts stop the queue. The original research runtime is unchanged.

The queue archives every completed phase under remote `artifacts/handoff/`, with member hashes and a ZIP checksum. Its artifacts include the exact source snapshot. The remote experiment log and team guide receive phase updates; pull those updates and the verified archives back before editing those documents locally again.

It ends at `awaiting_human_review`, after producing screening comparisons and the two worksheets. It cannot freeze settings, open the official test or infer review decisions. `queue.done` marks termination (successful or failed). The dedicated compute login exits after that marker; the detached queue itself does not depend on keeping this chat open. A failed queue is not automatically restarted.

## Completed screening and review handoff, 11 November

The completed run retained 88 identical training question IDs across all five adapters, then evaluated those adapters and the unchanged student on the first 50 development questions at budget 256. All runtime error counts were zero; truncations and unparseable outputs remain in the records. Its 4.533 hours are command wall time, including loading and CPU comparisons, not measured GPU utilization. These are unreviewed screening results.

All 18 phase ZIPs and their manifests were copied to local `artifacts/handoff/` and verified against the remote checksums, ZIP CRCs and every member hash. All five adapters and six evaluation runs are available locally. The final `2026-11-10-opus55-school-screening-complete.zip` is a lightweight handoff; it does not replace the separate adapter archives. Ignored artifacts still need a private backup independent of Git.

The private human-review Google Doc (link shared with the team directly and kept out of this public repository) has Mandarin and English tabs with 111 and 110 unique rewrites respectively. All A/R/U cells are blank. The owner must grant the teammate access; sharing permissions were not changed. See `artifacts/human-review/pilot-20261110/google-doc-manifest.json` for source hashes and tab IDs. No GPU job is needed while reviewers work. The later `ughost11` session was used only to read and copy shared-storage files, not to run another research series.
