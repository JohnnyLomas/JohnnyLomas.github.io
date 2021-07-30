#!/bin/bash
cd /Users/jslomas/Documents/JohnnyLomas.github.io/
Rscript -e "rmarkdown::render('Training_Log.Rmd', 'html_document')"
cp Training_Log.html index.html
git add index.html
git commit -m "committing new training log"
git push
