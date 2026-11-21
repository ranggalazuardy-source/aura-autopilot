# Cloudflare Python Worker local module packaging

The Cloudflare Worker entrypoint imports repository-local modules from the `app` namespace. `pywrangler sync` vendors third-party dependencies, but it does not by itself guarantee that the repository's local `app/` source tree is present in the Worker's Python module search path.

Before a Worker dry run or production deployment, the workflow therefore:

1. Runs `pywrangler sync` to prepare the dependency environment.
2. Copies the repository-local `app/` tree into `python_modules/app/`, the Worker's local module directory.
3. Verifies the repair modules required by the Worker entrypoint are present.
4. Parses every packaged Python source file with `ast` before any Cloudflare resource is changed.

The quality workflow performs the same packaging checks and runs `pywrangler deploy --dry-run`. Production deployment remains a separate manual workflow requiring an explicit `yes` confirmation; passing CI does not deploy or migrate production.
