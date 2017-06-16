# Script to parse titles and grab their amazon ratings
import sys
import re
import getopt

import json

from amazon.api import AmazonAPI

# Main function
#   argv - Variable list of arguments
def main(argv):
	# Configuration data
	config = parse_args(sys.argv)
	print(config)

	# Load up apis
	amazon = AmazonAPI(config['aws']['access_key'], config['aws']['secret_key'], config['aws']['associate_tag'])
	items = []
	with open(config['files']['input']) as f:
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


# Load config data
# 	config_filename - The filename of the config to load
def load_config(config_filename):
	with open(config_filename) as config_json:
		return json.load(config_json)

def usage():
	print("Usage here");

# Parse command line arguments
# 		Jesus this is a long function, but it's my first python script to w/evs
#	Inputs
#		argv - Arguments from CLI
#	Outputs
#		config - The configuration oibject
#	Exceptions
#		Invalid parsing
def parse_args(argv):
	DefaultInputFilename = 'input.txt'
	DefaultOutputFilename = 'output.txt'
	DefaultConfigFilename = 'config.json'
	try:
		opts, args = getopt.getopt(argv[1:], 'hdc:f:o:a:s:t:', [
			'help',
			'debug',
			'config={}'.format(DefaultConfigFilename),
			'filename={}'.format(DefaultInputFilename),
			'outfile={}'.format(DefaultOutputFilename),
			'access_key=',
			'secret_key=',
			'associate_tag='
		])
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	# Things to populate
	config_filename = None
	input_filename = None
	output_filename = None
	access_key = None
	secret_key = None
	associate_tag = None

	# Load it
	vefiy_config_exists = False
	for opt,arg in opts:
		# Help
		if opt in ('-h', '--help'):
			usage()
			sys.exit()

		# Debug
		if opt in ('-d', '--debug'):
			global _DEBUG
			_DEBUG = 1
		
		# Config
		elif opt in ('-c', '--config'):
			config_filename = arg
			verify_config_exists = True
		
		# Files
		elif opt in ('-f', '--infile'):
			input_filename = arg
		elif opt in ('-o', '--outfile'):
			output_filename = arg
		
		# AWS
		elif opt in ('-a', '--access_key'):
			access_key = arg
		elif opt in ('-s', '--secret_key'):
			secret_key = arg
		elif opt in ('-t', '--associate_tag'):
			associate_tag = arg

	# Patterns are excess
	title_patterns = args

	# Load config and check existance if it explicitly set
	config = None
	if config_filename is None:
		config_filename = DefaultConfigFilename

	if config_filename is not None:
		try:
			config = load_config(config_filename)
		except:
			if verify_config_exists:
				print("Failed to load config file:", config_filename)
				sys.exit(2)
			else:
				# NOTE: Default loaded below
				pass
	
	# Load default values
	if config is None:
		config = {
			'aws': {
				'access_key': None,
				'secret_key': None,
				'associate_tag': None
			},
			'files': {
				'input': DefaultInputFilename,
				'output': DefaultOutputFilename
			},
			'title_patterns': None
		}
	
	# Override config values
	# AWS
	if access_key is not None:
		config['aws']['access_key'] = access_key
	if secret_key is not None:
		config['aws']['secret_key'] = secret_key
	if associate_tag is not None:
		config['aws']['associate_tag'] = associate_tag
	
	# Files
	if input_filename is not None:
		config['files']['input'] = input_filename
	if output_filename is not None:
		config['files']['output'] = output_filename
	
	# Title patterns
	if title_patterns is list and len(title_patterns) > 0:
		config['title_patterns'] = title_patterns
	
	# Sanity checks
	missing = []
	if config['aws']['access_key'] is None:
		missing.append("AWS access key")
	if config['aws']['secret_key'] is None:
		missing.append("AWS secret key")
	if config['aws']['associate_tag'] is None:
		missing.append("AWS associate tag")
	if config['files']['input'] is None:
		missing.append("Input filename")
	if not isinstance(config['title_patterns'], list) or len(config['title_patterns']) < 1:
		missing.append("Title patterns")
	
	# Exit if we don't have required params
	if len(missing) > 0:
		for m in missing:
			print("Missing required parameter:", m)
		usage()
		sys.exit(2)
	
	return config

# Run the jewels
if __name__ == "__main__": main(sys.argv)

