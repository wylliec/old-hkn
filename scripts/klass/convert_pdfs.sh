#!/bin/sh

FILES=pdf/*.pdf
for f in $FILES
do
   psFile=`echo "$f" | sed -e 's/pdf\//ps\//' | sed -e 's/\.pdf/.ps/'`
   pdftops "$f" "$psFile"
done

