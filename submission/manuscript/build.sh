#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if command -v bibtex >/dev/null 2>&1; then BIBTEX=bibtex
elif command -v bibtex.original >/dev/null 2>&1; then BIBTEX=bibtex.original
else echo 'BibTeX is required; refusing to silently reuse a stale bibliography.' >&2; exit 1; fi
pdflatex -interaction=nonstopmode -halt-on-error main.tex
"$BIBTEX" main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
