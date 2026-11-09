# Notes for coding agents

See `docs/development.md` for the development loop, tests and translations.

## README screenshots

When the settings dialog (or the search panel) changes significantly, retake
the README screenshots with `make screenshots` and commit the new images in
`docs/images/` in the same pull request. Always take them in Danish: the
target does this with its own `da_DK` profile without a Bifrost key. Look at
the images before committing; they must not show a real key.

## Releases

Before tagging a release or building a zip for plugins.qgis.org, run
`make publish-check` on the committed release and fix every error (see
"Publishing" in `docs/development.md`). A version that plugins.qgis.org blocks
(a critical bandit or detect-secrets finding) cannot be fixed; only a new version can
replace it. Do not add `.bandit`, `.secrets.baseline` or `.flake8` files to
the plugin to silence the scanners.
