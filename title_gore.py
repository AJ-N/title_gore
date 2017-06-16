# Script to parse titles and grab their amazon ratings
import sys
import re
from amazon.api import AmazonAPI
access_key = 'REPLACE'
secret_key = 'REPLACE'
assoc_tag = 'REPLACE'
amazon = AmazonAPI(access_key, secret_key, assoc_tag)

# Main function
#   argv - Variable list of arguments
def main(argv):
	items = []
	with open('input.txt') as f:

		for line in f:
			# Extract Author - Title
			m = re.search('REPLACE', line) 
			if m is None:
				print('No matches for line: ', line, end='')
				continue

			# Sanity checks
			grps = m.groups()
			if grps is None:
				print('Groups error for line: ', line, end='')
				continue
			
			# Correct lengths
			if len(grps) != 2:
				print('Invalid extraction. Got: ', grps, ' for line: ', line, end='')
				continue

			author = grps[0].strip()
			title = grps[1].strip()

			print('Lookup "', title, '" by ', author, sep='')
			try:
				products = amazon.search_n(1, Power='author:{} and title:{}'.format(author, title), SearchIndex='Books')
				if products is None or len(products) < 1:
					print('\tNo matches')
					continue
				
				product = products[0]
				if product is None:
					print('\tEmpty match')
					continue

				print('\tRank = ', product.sales_rank, ', Pages = ', product.pages, ', Pubdate = ', product.publication_date, sep='')
				items.append(product)
			except:
				print('\tSearch failed')
	
	# Sort
	items.sort(key=lambda x: x.sales_rank)
	with open('output.txt', 'w') as w:
		for item in items:
			w.write('rank={}, asin={}, title={}, pages={}, published={}'.format(item.sales_rank, item.asin, item.tile, item.pages, item.publication__date))


# Run the jewels
if __name__ == "__main__": main(sys.argv)
