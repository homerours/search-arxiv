import argparse
import feedparser
import urllib
import os

parser = argparse.ArgumentParser(description = 'Search the arXiv')

parser.add_argument('-d', '--download', action = 'store_true',
        help = "download papers")
parser.add_argument('-f', '--format',
        default = '%i',
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
        default = 'submitted',
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
print 'Results:'

response = urllib.urlopen(base_url + query).read()
response = response.replace('author', 'contributor')

feed = feedparser.parse(response)

for entry in feed.entries:
    print ''
    print ''
    print '  arXiv-id: %s' % entry.id.split('/abs/')[-1]
    print '  Published: %s' % entry.published
    print '  Title: %s' % entry.title
    print '  Authors: %s' % ', '.join(author.name for author in
            entry.contributors)

    if args.download:
        print ''
        print '  Downloading to:'
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

                print('    ' + file_name + '.pdf')
                urllib.urlretrieve(link.href, file_name + '.pdf')
