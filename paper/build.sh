#!/bin/sh

case $1 in
clean)
  rm -f *.log *.aux *.toc *.blg *.pdf *.out *.bbl
  ;;
*)
  pdflatex main.tex
  bibtex bu1
  bibtex bu2
  bibtex main
  pdflatex main.tex
  pdflatex main.tex
  ;;
esac
