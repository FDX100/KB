#!/usr/bin/env bash
# Turn a logo you have (EPS, PDF, SVG ...) into the transparent PNG the badge uses (apps read PNG only, never EPS).
#
#   ./tools/logo_png.sh Mlogo.eps logos/m.png [width-px]      (480 by default)
#
# Needs Ghostscript (gs) for EPS / PDF, or ImageMagick (convert) for anything else. The result goes in the git-ignored logos/ folder;
# put it on the car with scripts/logos.sh (README, Badges and logos). The artwork stays yours: nothing here is committed.
set -euo pipefail
IN="${1:?usage: logo_png.sh <in.eps|pdf|svg|png> <out.png> [width]}"; OUT="${2:?usage: logo_png.sh <in> <out.png> [width]}"; W="${3:-480}"
mkdir -p "$(dirname "$OUT")"
case "$(printf '%s' "$IN" | tr 'A-Z' 'a-z')" in
    *.eps|*.pdf|*.ps)
        gs -q -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -sDEVICE=pngalpha -r400 -dTextAlphaBits=4 -dGraphicsAlphaBits=4 -sOutputFile="$OUT" "$IN" ;;
    *) convert -background none "$IN" "$OUT" ;;
esac
# trim the empty border and scale to the width
convert "$OUT" -trim +repage -resize "${W}x" "$OUT"
echo "$OUT: $(identify -format '%wx%h' "$OUT")"
