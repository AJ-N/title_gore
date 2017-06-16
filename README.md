# Title Gore

Sorts a list of book titles/authors by Amazon ranking. Useful for curating a large list of books to find the best ones

## Overview

 * Extract author and title through one or more regular expressions
 * Uses Amazon Affiliate APIs to lookup books ranking, publication date, and page count
 * Sorts results based on ranking
 * JSON-configuration for easy setup
 * Requires Python3

Example

```Bash
python title_gore.py -f ./fantasy_books.txt "^([\w\s]+)-([\w\s])+$"
```

## Configuration

By default, it tries to load config.json. You can override this with the -c/--config option.

Each of these can also be passed in or overridden through CLI args.

```
{
	"aws": {
    	"access_key": "string",   // Your AWS access key
        "secret_key": "string",   // Your AWS secrey key
        "associate_tag": "string" // Your AWS associate tag from the affiliate program
    },
    
    "files": {
    	"input": "string",   // The input file (containing a book title/author on each row)
        "output": "string"   // The output file (sorted with metadata) [If set to null, outputs on stdout]
    },
    
    "title_patterns": [  // One or more patterns for matching title/authors
    	{
       		"pattern": "string", // Regular expression pattern
            "author_index": "",  // Index of the match to pull author from
            "title_index": ""    // Index of the match to pull title from
        }
        ..
    ]
}
```

## Arguments

Each argument is first set via a config file (if present). Then, anything explicity passed in will override this value. View these options with the -h option.

```
title_gore.py [OPTIONS] title_pattern title_pattern ..
        -h      --help          Print usage information
        -c      --config        Configuration input file. Contains these OPTIONS [Default: "config.json"]
        -f      --filename      Input filename (required) [Default: "input.txt"]
        -o      --outfile       Output filename [Default: "output.txt"]
        -a      --access_key    AWS access key (required)
        -s      --secret_key    AWS secret key (required)
        -t      --associate_tag AWS associate tag (required)
 ```
