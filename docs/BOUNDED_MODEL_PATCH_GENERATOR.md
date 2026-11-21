# Bounded model patch generator

`BoundedModelPatchGenerator` implements the existing injected `PatchGenerator`
contract without selecting a provider or accessing GitHub directly.

- Reads only the exact candidate paths persisted by owner triage.
- Reads each source file at the immutable incident commit SHA.
- Caps each source file at 12,000 characters, total source context at 30,000
  characters, and model response/diff size at 256 KB.
- Sends only incident ID, category, base SHA, allowed paths and those source
  files to the injected model callback. Raw CI logs and run URLs are excluded.
- Requires strict JSON with only a unified diff and file metadata. Boolean,
  non-integer and malformed metadata are rejected.
- Marks itself as a non-mock generator, so the existing IT/AI Engineer adapter
  blocks it unless a future owner-authorized runtime explicitly permits provider
  inference.
- The existing repair pipeline independently validates diff headers, hunk
  counts, path allowlists, exact candidate-path equality and the patch digest.

The source reader and model invoker are injected. This module does not configure
credentials, perform network requests, call a live provider, write files, create
PRs, merge or deploy. CI uses fake readers and fake model callbacks.
