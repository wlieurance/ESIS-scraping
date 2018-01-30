#!/usr/bin/env python3
import os
import bs4
import urllib.request
import urllib.parse
import argparse
import csv
import pathlib
import imghdr
import http

parser = argparse.ArgumentParser()
parser.add_argument("esdlist", help="path to the ESD list text file.")
parser.add_argument("outpath", help="path where the exports will be saved.")
args = parser.parse_args()

### parts of the download link for NRCS ESIS
l = ['https://esis.sc.egov.usda.gov','ESDReport','fsReportPrt.aspx?id={!s}&rptLevel=all&approved={!s}&repType=regular&scrns=&comm=']

with open(args.esdlist, 'r') as f: #get ESDs from csv file
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        esd = row[0]
        print('grabbing', esd)
        link =  '/'.join((l[0], l[1], l[2].format(esd, 'no'))) #construct link
        pathlib.Path(os.path.join(args.outpath, esd)).mkdir(parents=True, exist_ok=True) #makes directories if they dont exist
        try:
            r = urllib.request.urlopen(link).read() #grab link data
        except (urllib.error.HTTPError, http.client.HTTPException):
            print('Could not open', link)
        else:
            soup = bs4.BeautifulSoup(r, 'lxml') #parse link
            isError = False
            for form in soup.find_all('form'):
                if form['action'].find('EsisError') >= 0:
                    isError = True
            if not isError:
                imgs = soup.find_all('img') # find images embeded in link
                srcs = []

                ### extracts the source information for each picture link in the html
                for i in imgs:
                    srcs.append(i.get('src'))

                unique = list(set(srcs)) # makes a unique list of the links to avoid double downloading
                tracker = [] # init a dict for keeping track of changes to the links names
                for u in unique:
                    img_link = urllib.parse.urljoin(link, u) # constructs the image link url
                    
                    ### some images are returned via retieving an actual image (i.e. space.gif) while some are retrieved from a database BLOB (i.e. id=####)
                    if u.find('id=') >=0:
                        filename = u[u.find('id=')+3:]
                    else:
                        uparts = u.split('/')
                        filename = uparts[len(uparts)-1]
                    try:
                        urllib.request.urlretrieve(img_link, os.path.join(args.outpath, esd, filename)) #grabs the actual images
                    except (urllib.error.HTTPError, http.client.HTTPException):
                        print('Could not find', img_link)
                    else:
                        tracker.append({'src': u, 'link': img_link, 'fullpath': os.path.join(args.outpath, esd, filename), 'renamed': False})

                ### scans the downloaded database images with no extension, determines their filetype, and gives them an extenstion.
                processed = []
                for t in tracker:
                    fullpath = t.get('fullpath')
                    fname = os.path.basename(fullpath)
                    basedir = os.path.dirname(fullpath)
                    ext = os.path.splitext(fname)[1]
                    if not ext:
                        new_ext = imghdr.what(fullpath) #determines pic type
                        if new_ext:
                            try:
                                os.rename(fullpath, '.'.join((fullpath, new_ext))) #renames with proper file extension
                            except FileExistsError:
                                os.remove('.'.join((fullpath, new_ext)))
                                os.rename(fullpath, '.'.join((fullpath, new_ext)))
                            else:
                                t['fullpath'] = '.'.join((fullpath, new_ext))
                                t['renamed'] = True
                    t['relpath'] = os.path.join('.',os.path.basename(t['fullpath']))
                    processed.append(t)
                    
                ### replace html picture path with new pic path            
                for p in processed:
                    for i in soup.find_all('img'):
                        if p['src'] == i['src']:
                            i['src'] = p['relpath']
                        
                with open(os.path.join(args.outpath, esd, '.'.join((esd, 'html'))), 'w') as out:
                    out.write(soup.prettify())
            else:
                print('No data for', esd)
                with open(os.path.join(args.outpath, esd, '.'.join((esd, 'txt'))), 'w') as out:
                    out.write(''.join(('No data for ', esd, '.')))
print('\nScript finished.\n')
        
