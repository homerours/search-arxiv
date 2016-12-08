#!/usr/bin/python2
# A cmd line tool for searching the arxiv and downloading documents from it
# Copyright 2015 Fabian Kirchner <kirchner@posteo.de>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import feedparser
import urllib
import os

# Colors
MAGENTA='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'
NORMAL='\033[0;39m'
PURPLE='\033[0;35m'

parser = argparse.ArgumentParser(description = 'Search the arXiv')

parser.add_argument('-d', '--download', action = 'store_true',
        help = "download papers")
parser.add_argument('-f', '--format',
        default = '%a - %t',
        help = "how to format the files")

parser.add_argument("-a", "--author", nargs = '+',
        help = "search by author(s)")
parser.add_argument("-t", "--title",
        help = "search by title")
parser.add_argument("--abstract",
        help = "search by abstract")
parser.add_argument("-c", "--category",
        help = "search in the category")
parser.add_argument("--comment",
        help = "search by comment")
parser.add_argument("query", nargs = "*",
        help = "give explicit arXiv query(s)")

parser.add_argument("-m", "--max-results", type = int, default = 10,
        help = "maximal number of results to display (defaults to 10)")

parser.add_argument("--sort-by",
        choices = ['relevance', 'updated', 'submitted'],
        default = 'relevance',
        help = "sort results either by relevance, by the date of the last update or by the date of submission (defaults to submitted)")
parser.add_argument("--sort-order",
        choices = ['ascending', 'descending'],
        default = 'descending',
        help = "how to order the results (defaults to descending)")

args = parser.parse_args()


search_query = ''

if args.author:
    for author in args.author:
        if search_query != '':
            search_query = search_query + '+AND+'
        search_query = search_query + 'au:' + author

if args.title:
    if search_query != '':
        search_query = search_query + '+AND+'
    search_query = search_query + 'ti:' + args.title.replace(' ', '+AND+ti:')

if args.abstract:
    if search_query != '':
        search_query = search_query + '+AND+'
    search_query = search_query + 'abs:' + args.abstract.replace(' ', '+AND+abs:')

if args.comment:
    if search_query != '':
        search_query = search_query + '+AND+'
    search_query = search_query + 'co:' + args.comment.replace(' ', '+AND+co:')

if args.query:
    for query in args.query:
        if search_query != '':
            search_query = search_query + '+AND+'
        search_query = search_query + 'all:' + query


if args.sort_by == 'relevance':
    sort_by = 'relevance'
elif args.sort_by == 'updated':
    sort_by = 'lastUpdatedDate'
elif args.sort_by == 'submitted':
    sort_by = 'submittedDate'

if args.sort_order == 'ascending':
    sort_order = 'ascending'
elif args.sort_order == 'descending':
    sort_order = 'descending'


query = ('search_query=' + search_query
         + '&start=' + '0'
         + '&max_results=%i' % args.max_results
         + '&sortBy=' + sort_by
         + '&sortOrder=' + sort_order)

base_url = 'http://export.arxiv.org/api/query?';

print 'Searching the arXiv using the following query:'
print '  ' + query
print ''
print ''
print MAGENTA + '----- Results -----' + NORMAL

response = urllib.urlopen(base_url + query).read()
response = response.replace('author', 'contributor')

feed = feedparser.parse(response)

index=0
for entry in feed.entries:
    index+=1
    print ''
    print ''
    print 'INDEX: ' + PURPLE + `index` + NORMAL
    print '  arXiv-id: '+ GREEN +'%s' % entry.id.split('/abs/')[-1] + NORMAL
    print '  Published: %s' % entry.published
    print '  Title: ' + ORANGE + '%s' % entry.title +NORMAL
    print '  Authors: ' + CYAN + '%s' % ', '.join(author.name for author in
            entry.contributors) +NORMAL

    # if args.download:
        # print ''
        # print '  Downloading to:'
        # for link in entry.links:
            # if link.type == 'application/pdf':
                # file_name = args.format
                
                # arxiv_id = link.href.split('/')[-1]
                # file_name = file_name.replace('%i', arxiv_id)
                # file_name = file_name.replace('%t', entry.title)
                # authors = ', '.join(author.name for author in entry.contributors)
                # file_name = file_name.replace('%a', authors)
                # published = entry.published.split('T')[0]
                # file_name = file_name.replace('%p', published)

                # print('    ' + file_name + '.pdf')
                # urllib.urlretrieve(link.href, file_name + '.pdf')

print ''
downIndex=raw_input('Which papers would you like to download (ex: 1,3 or *) ?  ')
try:
    if (downIndex=='*'):
        downItems=range(len(feed.entries))
    else:
        downItems =[int(i)-1 for i in downIndex.split(',')]
except:
    print 'No download'
    downItems=[]
for index in downItems:
    entry=feed.entries[index]
    print ''
    print '  Downloading :'
    for link in entry.links:
        if link.type == 'application/pdf':
            file_name = args.format

            arxiv_id = link.href.split('/')[-1]
            file_name = file_name.replace('%i', arxiv_id)
            file_name = file_name.replace('%t', entry.title)
            authors = ', '.join(author.name for author in entry.contributors)
            file_name = file_name.replace('%a', authors)
            published = entry.published.split('T')[0]
            file_name = file_name.replace('%p', published)
            print('  ' + GREEN + file_name + '.pdf' + NORMAL)
            urllib.urlretrieve(link.href, file_name + '.pdf')

print ''
print 'Goodbye :)'
