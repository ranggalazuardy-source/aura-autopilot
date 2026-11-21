# Async runtime repair generator

The asynchronous generator adapts the bounded patch contract to Cloudflare
Worker I/O. It accepts injected async source-reader and model-invoker
capabilities, reads only owner-triaged candidate paths at the immutable CI
commit SHA, and applies the same path/context/response bounds as the sync
generator.

The runtime adapter must independently require explicit owner confirmation,
the global model execution switch, provider-specific enabled flags and
Free-tier confirmations, and the shared daily call cap. This class itself does
not authorize or contact providers. Existing diff and metadata validators
remain the final authority before a proposal is returned.

It never writes repository files, creates branches, issues or consumes approval
receipts, merges, or deploys.
