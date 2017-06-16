# Script to parse titles and grab their amazon ratings
import sys
import re
import getopt
import json

from amazon.api import AmazonAPI

# Globals
_DEBUG = False

# Main function
#   argv - Variable list of arguments
def main(argv):
	# Configuration data
	config = parse_args(sys.argv)

	# Load up apis
	amazon = AmazonAPI(config['aws']['access_key'], config['aws']['secret_key'], config['aws']['associate_tag'])

	# Parse 'em
	items = []
	last_item = None
	unknowns = []
	with open(config['files']['input']) as f:
		for line in f:
			# Extract Author - Title
			matches = None
			for pattern in config['title_patterns']:
				matches = re.search('REPLACE', line) 
				if matches is not None:
					break
			
			if matches is None:
				debug('No matches for:', line, end='')
				unknowns.append({
					'line': line,
					'author': None,
					'title': None
				})
				continue

			# Sanity checks
			grps = m.groups()
			if grps is None:
				debug('Groups error for line: ', line, end='')
				unknowns.append({
					'line': line,
					'author': None,
					'title': None
				})
				continue
			
			# Correct lengths
			if len(grps) != 2:
				debug('Invalid extraction. Got: ', grps, ' for line: ', line, end='')
				unknowns.append({
					'line': line,
					'author': None,
					'title': None
				})
				continue

			author = grps[0].strip()
			title = grps[1].strip()

			debug('Lookup "', title, '" by ', author, sep='')
			try:
				products = amazon.search_n(1, Power='author:{} and title:{}'.format(author, title), SearchIndex='Books')
				if products is None or len(products) < 1:
					debug('\tNo matches')
					unknowns.append({
						'line': line,
						'author': author,
						'title': title
					})
					continue
				
				product = products[0]
				if product is None:
					debug('\tEmpty match')
					unknowns.append({
						'line': line,
						'author': author,
						'title': title
					})
					continue

				debug('\tRank = ', product.sales_rank, ', Pages = ', product.pages, ', Pubdate = ', product.publication_date, sep='')
				items.append(product)
			except:
				debug('\tSearch failed')
	
	# Sort
	items.sort(key=lambda x: x.sales_rank)

	# Output
	w = None
	if config['files']['output'] is not None:
		w = open(config['files']['output'], 'w')
	else:
		w = sys.stdout

	# Spit ranked items first, then not founds
	for item in items:
		w.write('rank={}, asin={}, title={}, pages={}, published={}\r\n'.format(item.sales_rank, item.asin, item.tile, item.pages, item.publication__date))
	for unknown in unknowns:
			w.write('rank={}, author={}, title={}, line={}\r\n'.format(None, None, unknown['author'], unknown['title'], unknown['line']))

# Load config data
# 	Inputs
# 		config_filename - The filename of the config to load
#	Outputs
#		config - Configuration dictionary
def load_config(config_filename):
	with open(config_filename) as config_json:
		return json.load(config_json)

# Prints out usage information
def usage():
	print("Usage here")

# Debug printing
# 	Inputs
# 		args - Variable number of args to print
def debug(*args, end=None, sep=None):
	if _DEBUG:
		print(*args, end=end, sep=sep)

# Parse command line arguments
# 		Jesus this is a long function, but it's my first python script to w/evs
#	Inputs
#		argv - Arguments from CLI
#	Outputs
#		config - Configuration dictionary
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
			_DEBUG = True
		
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

