import bs4
import re
import os
import csv
import json
import argparse
from bs4 import Tag, NavigableString


def get_parent_table(elem):
    """Returns the parent table of the element passed to it."""
    # print(elem.parent.name)
    if elem.parent.name == 'table':
        # print("found parent")
        return elem.parent
    else:
        return get_parent_table(elem.parent)


def compile_species(elem, some_str=''):
    """Compiles a species list from a very specific part of the 'esddetail' table"""
    if elem.string:
        some_str += elem.string.strip()
        # print('some_str now:', some_str)
    if isinstance(elem.next_sibling, Tag):
        # print("tag:", elem.next.name)
        if elem.next_sibling.name == 'br':
            some_str += '\n'
        if elem.next_sibling.attrs.get('class'):
            # print('class:', elem.next_sibling.attrs.get('class'))
            if elem.next_sibling.attrs.get('class')[0] == 'esdtag2':
                return some_str.replace(' / ', '/').replace(' - ', '-').strip()
    return compile_species(elem.next_sibling, some_str)


def grab_eco_attr(file):
    """Will take an Ecological Site Description file in html format downloaded from ESIS and grab metadata. Returns
    a dictionary."""
    soup = bs4.BeautifulSoup(open(file), 'lxml')
    start = soup.find_all(text=re.compile("Site stage:"))
    if start:
        start_table = get_parent_table(start[0])
        ecodict = dict()
        tag = start_table.find_all(attrs={'class': 'esdtag3Italicized'})
        for t in tag:
            if t.get_text().strip() == 'Site stage:':
                if t.find_next_sibling().name == 'span':
                    ecodict['site_stage'] = t.find_next_sibling().get_text().strip()
            elif t.get_text().strip() == 'Site name:':
                if t.find_next_sibling().name == 'b':
                    ecodict['site_name'] = t.find_next_sibling().get_text().strip()
        tag = start_table.find(attrs={'class': 'esddetaili'})
        if tag:
            veg = compile_species(tag)
            veg_list = veg.split('\n')
            if veg_list:
                ecodict['veg_sci'] = veg_list[0]
                if len(veg_list) > 1:
                    ecodict['veg_com'] = ' : '.join(veg_list[1:])
        tag = start_table.find_all(attrs={'class': 'esdtag2'})
        for t in tag:
            if t.get_text().strip() == 'Site type:':
                if isinstance(t.next_sibling, NavigableString):
                    ecodict['site_type'] = t.next_sibling.string.strip()
            elif t.get_text().strip() == 'Site ID:':
                if isinstance(t.next_sibling, NavigableString):
                    ecodict['site_id'] = t.next_sibling.string.strip()
            elif t.get_text().strip() == 'Major land resource area (MLRA):':
                if isinstance(t.next_sibling, NavigableString):
                    ecodict['mlra'] = t.next_sibling.string.strip()
        return ecodict


if __name__ == "__main__":
    """Will take a search path populated with ESD files from ESIS (html) and pulls metadata from them, and populates
    either a json file or csv file."""
    parser = argparse.ArgumentParser()
    parser.add_argument('scanpath', help='path to scan for html ecosite files (from ESIS)')
    parser.add_argument('outfile', help='file path to which the scraped data will be saved (.csv or .json)')
    args = parser.parse_args()

    if not os.path.isdir(args.scanpath):
        print(args.scanpath, "is not a valid existing directory.")
        quit()

    results = []
    for root, dirs, files in os.walk(args.scanpath):
        for f in files:
            if os.path.splitext(f)[1] == '.html':
                print("scraping attribute data from", f)
                result = grab_eco_attr(os.path.join(root, f))
                if result:
                    result['path'] = os.path.join(root, f)
                    results.append(result)
    if os.path.splitext(args.outfile)[1] == '.csv':
        with open(args.outfile, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['path', 'site_stage', 'site_type', 'site_id', 'mlra', 'site_name', 'veg_sci', 'veg_com']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
            writer.writeheader()
            for row in results:
                writer.writerow(row)
    elif os.path.splitext(args.outfile)[1] == '.json' or not os.path.splitext(args.outfile)[1]:
        with open(args.outfile, 'w', encoding='utf-8') as jsonfile:
            json.dump(results, jsonfile, ensure_ascii=False, indent=4)

    print('\nScript finished.\n')




