# KORA full-project migration — blocked, not ready to merge

This is a **temporary migration control document**, not the completed project copy.

## Intended source and destination

- Source: private `TimLL123456/HKU` at commit `bd473bc5dbe4f4286ef70a3d5f36a7d1147a654b`.
- Source directory: `2026-2027/Sem1/COMP7608 - Large language models/COMP7608 - Large language models - Group Project/`.
- Destination: public `TimLL123456/COMP7608-Large-language-models-Group-Project` on this migration branch.
- Expected source contents at the inspected revision: **1,025 tracked files**, including **six experiment archives**.

## Blocking technical limitation

The current GitHub connector cannot read a subset of the large compressed binary experiment artifacts (>1 MB) and five notebooks are tracked in HKU as Git LFS pointers. Copying only files accessible through the API would produce an **incomplete and potentially unverified** public research archive. Cross-repository Git blob SHA reuse was tested and rejected by GitHub. Accordingly, **no incomplete bulk source copy has been committed**.

## One-shot completion procedure (authenticated local/VPS environment)

Run the migration helper provided with the ChatGPT migration session from a clone of this public repository checked out on `migration/full-kora-project-20261115`. Prerequisites: authenticated GitHub access to the private HKU repository, `git-lfs`, Python, `uv`, `gh` and `gitleaks`.

The helper:
1. Performs a read-only private HKU Git checkout using sparse checkout and resolves the five Git LFS notebooks.
2. Copies the **entire tracked project subdirectory** into the public repository root, preserving byte-for-byte experimental artifacts.
3. Merges `.gitignore` safely, adapts current README and setup docs to the Group repo, retains historical provenance.
4. Checks source file count, byte hashes, all six experiment checksum manifests, staged notebook bytes, new Markdown links, secrets (`gitleaks`) and offline unit tests.
5. Only after all checks pass: commits/pushes the complete project to this existing branch, marks the PR ready and squash-merges into `main`.

Do **not** merge this PR while this temporary status file is present. The helper deletes the `.migration/` directory before final delivery.

## Safety boundaries

Never copy private keys, provider tokens or unexpected local data. Do not change source HKU files, downloaded BIRD datasets, historical score manifests or reference data. If validation fails, preserve the branch and keep the pull request unmerged for troubleshooting. This temporary branch tracks preparation only, **not successful migration**.
