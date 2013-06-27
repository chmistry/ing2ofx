#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       ing2ofx.py
#       
#       Copyright 2013 Arie van Dobben <avandobben@gmail.com>
#       
#       This program is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
The intend of this script is to convert ing (www.ing.nl) csv files to ofx files 
that can be read by a program like GnuCash (www.gucash.org).

This script is adapted from pb2ofx.pl Copyright 2008, 2009, 2010 Peter Vermaas,
originally found at http://blog.maashoek.nl/2009/07/gnucash-en-internetbankieren/ 
which is now dead.

The ofx specification can be downloaded from http://www.ofx.net/
"""

import csv
import argparse
import datetime
import os

""" First parse the command line arguments. """
parser = argparse.ArgumentParser(prog = 'ing2ofx', description= """
                                 This program converts ING (www.ing.nl) CSV files to OFX format.
                                 The default output filename is the input filename.
                                 """)
parser.add_argument('csvfile', help='A csvfile to process')
parser.add_argument('-o, --outfile', dest = 'outfile', 
   help = 'Output filename', default=None)
parser.add_argument('-d, --directory', dest = 'dir', 
   help = 'Directory to store output, default is ./ofx', default='ofx')
parser.add_argument('-c, --convert', dest = 'convert', 
   help = "Convert decimal separator to dots (.), default is false", action='store_true')
args = parser.parse_args()

""" Read the csv file into a list, which is mapped to ofx fields """
class csvfile():
   def __init__(self):
      #Mapping of codes to TRNTYPE
      codesx = {'GT': 'PAYMENT', 'BA': 'POS', 'GM': 'ATM', 'DV': 'xx', 
                'OV': 'xx', 'VZ': 'xx', 'IC': 'DIRECTDEBIT', 'ST': 'DIRECTDEP'}
      self.transactions = list()
      #transnr = 0

      with open(args.csvfile, 'rb') as csvfile:
         #Open the csvfile as a Dictreader
         spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
         for row in spamreader:
            #Map ACCOUNT to "Rekening"
            account = row['Rekening'].replace(" ", "")
            
            #Map the code into ofx TRNTYPE
            if row['Code'] in codesx:
               if codesx[row['Code']] == 'xx':
                  if row['Af Bij'] == 'Bij':
                     trntype = 'CREDIT'
                  else:
                     trntype = 'DEBIT'
               else:
                  trntype = codesx[row['Code']]
            else:
               trntype = 'OTHER'
            
            #The DTPOSTED is in yyyymmdd format, which is compatible with ofx
            dtposted = row['Datum']
            
            #The TRNAMT needs to be converted to negative if applicable,
            #When convert is set, comma decimal separator is replaced with dot.
            if args.convert:
               row['Bedrag (EUR)'] = row['Bedrag (EUR)'].replace(",", ".")
            if row['Af Bij'] == 'Bij':
               trnamt = row['Bedrag (EUR)']
            else:
               trnamt = "-"+row['Bedrag (EUR)']
            
            #the FITID is composed of the date and amount
            fitid = dtposted+trnamt.replace(",","").replace("-","").replace(".","")
            
            #NAME maps to "Naam / Omschrijving", the while loop removes any double spaces.
            while row['Naam / Omschrijving'].strip().find("  ") > 0:
               row['Naam / Omschrijving'] = row['Naam / Omschrijving'].strip().replace("  ", " ")
            #Replace & symbol with &amp to make xml compliant
            name = row['Naam / Omschrijving'].replace("&", "&amp")
            
            #BANKACCTTO maps to "Tegenrekening" 
            accountto = row['Tegenrekening']
            
            #MEMO maps to "Mededelingen", the while loop removes any double spaces.
            while row['Mededelingen'].strip().find("  ") > 0:
               row['Mededelingen'] = row['Mededelingen'].strip().replace("  ", " ")
            #Replace & symbol with &amp to make xml compliant
            memo = str(row['Mededelingen']).replace("&", "&amp")
            
            self.transactions.append({'account': account, 'trntype': trntype, 'dtposted': dtposted, 
                                          'trnamt': trnamt, 'fitid': fitid, 'name': name, 'accountto': accountto, 
                                          'memo': memo})

class ofxwriter():
   def __init__(self):
      date = datetime.date.today()
      nowdate = str(date.strftime("%Y%m%d"))
      
      message_header = """   
<OFX>
   <SIGNONMSGSRSV1>
      <SONRS>                            <!-- Begin signon -->
         <STATUS>                        <!-- Begin status aggregate -->
            <CODE>0</CODE>               <!-- OK -->
            <SEVERITY>INFO</SEVERITY>
         </STATUS>
         <DTSERVER>%(nowdate)s</DTSERVER>   <!-- Oct. 29, 1999, 10:10:03 am -->
         <LANGUAGE>ENG</LANGUAGE>        <!-- Language used in response -->
         <DTPROFUP>%(nowdate)s</DTPROFUP>   <!-- Last update to profile-->
         <DTACCTUP>%(nowdate)s</DTACCTUP>   <!-- Last account update -->
         <FI>                            <!-- ID of receiving institution -->
            <ORG>NCH</ORG>               <!-- Name of ID owner -->
            <FID>1001</FID>              <!-- Actual ID -->
         </FI>
      </SONRS>                           <!-- End of signon -->
   </SIGNONMSGSRSV1>
   <BANKMSGSRSV1>
      <STMTTRNRS>                        <!-- Begin response -->
         <TRNUID>1001</TRNUID>           <!-- Client ID sent in request -->
         <STATUS>                     <!-- Start status aggregate -->
            <CODE>0</CODE>            <!-- OK -->
            <SEVERITY>INFO</SEVERITY>
         </STATUS>""" % {"nowdate": nowdate}
      #print message_header
      
      #create path to ofxfile
      if args.outfile:
         filename = args.outfile
      else:
         filename = args.csvfile.lower().replace("csv", "ofx")
      
      #if directory does not exists, create it.
      if not os.path.exists(os.path.join(os.getcwd(), args.dir)):
         os.makedirs(os.path.join(os.getcwd(), args.dir))
      
      filepath = os.path.join(os.getcwd(), args.dir, filename)
      
      #Initiate a csv object that contains all the data in a set.
      csv = csvfile()
      
      #Determine unique accounts and start and end dates
      accounts = set()
      mindate = 999999999
      maxdate = 0
      
      #print some statistics:
      print "TRANSACTIONS: "+str(len(csv.transactions))
      print "IN:           "+args.csvfile
      print "OUT:          "+filename
      
      for trns in csv.transactions:
         accounts.add(trns['account'])
         if int(trns['dtposted']) < mindate:
            mindate = int(trns['dtposted'])
         if int(trns['dtposted']) > maxdate:
            maxdate = int(trns['dtposted'])
      
      #open ofx file, if file exists, gets overwritten
      with open(filepath, 'w') as ofxfile:
         ofxfile.write(message_header)
         
         for account in accounts:
            message_begin = """
         <STMTRS>                         <!-- Begin statement response -->
            <CURDEF>EUR</CURDEF>
            <BANKACCTFROM>                <!-- Identify the account -->
               <BANKID>121099999</BANKID> <!-- Routing transit or other FI ID -->
               <ACCTID>%(account)s</ACCTID> <!-- Account number -->
               <ACCTTYPE>CHECKING</ACCTTYPE><!-- Account type -->
            </BANKACCTFROM>               <!-- End of account ID -->
            <BANKTRANLIST>                <!-- Begin list of statement trans. -->
               <DTSTART>%(mindate)s</DTSTART>
               <DTEND>%(maxdate)s</DTEND>""" % {"account": account, "mindate": mindate, "maxdate": maxdate}
            ofxfile.write(message_begin)
            
            for trns in csv.transactions:
               if trns['account'] == account:
                  message_transaction = """
               <STMTTRN>
                  <TRNTYPE>%(trntype)s</TRNTYPE>
                  <DTPOSTED>%(dtposted)s</DTPOSTED>
                  <TRNAMT>%(trnamt)s</TRNAMT>
                  <FITID>%(fitid)s</FITID>
                  <NAME>%(name)s</NAME>
                  <BANKACCTTO>
                     <BANKID></BANKID>
                     <ACCTID>%(accountto)s</ACCTID>
                     <ACCTTYPE>CHECKING</ACCTTYPE>
                  </BANKACCTTO>
                  <MEMO>%(memo)s</MEMO>
               </STMTTRN>""" % trns
                  ofxfile.write(message_transaction)

            message_end = """
            </BANKTRANLIST>                   <!-- End list of statement trans. -->
            <LEDGERBAL>                       <!-- Ledger balance aggregate -->
               <BALAMT>0</BALAMT>
               <DTASOF>199910291120</DTASOF><!-- Bal date: 10/29/99, 11:20 am -->
            </LEDGERBAL>                      <!-- End ledger balance -->
         </STMTRS>"""
            ofxfile.write(message_end)

         message_footer = """
      </STMTTRNRS>                        <!-- End of transaction -->
   </BANKMSGSRSV1>
</OFX>
      """
         ofxfile.write(message_footer)
         
if __name__ == "__main__":
   ofx = ofxwriter()

   



