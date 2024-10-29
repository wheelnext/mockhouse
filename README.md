# mockhouse
A minimalistic warehouse "mock index" to support the METADATA PEP XXX.

This project provides the server component of the metadata proposal.

There are 2 endpoints for this implementation:

* `/simple/<name>/variants`: This endpoint lists several hashes. Each is the
  hash of a particular variant that is available. This endpoint is not intended
  to be human-friendly. It is meant to provide the hashes so that the client can
  match them with its own collection of hashes.

* `/simple/<name>/variant/<variant_hash>`: This endpoint mimics the distribution
  file listing defined by PEPs 503 and 691. It shows the variant values that
  make up the hash. It lists only files that provide the variant.

The goal is that the client follows:

1. Loads local list of variants, precomputed as in https://github.com/wheel-next/variant-combinations
2. Fetches the `/simple/<name>/variants` endpoint
3. Performs a set intersection of 1) and 2), ensuring that the order is preserved (the order carries variant priority)
4. Iterate over variants, assuming index priority, or "first match" behavior, as
  described by uv. This means that the installer will exhaust one variant "index"
  before proceeding to the next variant. Other indexes will only be reached if
  none of variants match.