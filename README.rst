=======
ing2ofx
=======
Intro
-----
The intend of this script is to convert ing (www.ing.nl) csv files to ofx files 
that can be read by a program like GnuCash (www.gucash.org).

This script is adapted from pb2ofx.pl Copyright 2008, 2009, 2010 Peter Vermaas,
originally found at http://blog.maashoek.nl/2009/07/gnucash-en-internetbankieren/ 
which is now offline.

The ofx specification can be downloaded from http://www.ofx.net/

Usage
-----
::

   usage: ing2ofx [-h] [-o --outfile] [-d --directory] [--convert] csvfile

   positional arguments:
     csvfile         A csvfile to process

   optional arguments:
     -h, --help      show this help message and exit
     -o --outfile    output filename
     -d --directory  directory to store output, default is ./ofx
     --convert       Convert decimal separator to dots (.), default is false

Output
------
#. An ofx file converted from the csv file (default in the folder ./ofx)
#. Some statistics:

::

   TRANSACTIONS: 349
   IN:           test2.csv
   OUT:          test2.ofx

