## If you haven't already:
* Download and install scrapy by following the instructions from https://scrapy.org/download/
* Download and install scikit-learn by following the instructions from https://scikit-learn.org/stable/install.html
* Download and install nltk by following the instructions from https://www.nltk.org/install.html

## Overview:
1) Unzip 4395_webcrawler_proj.zip 
2) Files you should see: 	
	crawler.py 					-	Code for web crawler/scraper
	Keyword_Database.sql 		- 	SQL file that contains the knowledge-base
	main.py 					- 	Code for parsing text, running tf-idf, and creating knowledge-base
	processed_texts.example		- 	Contains text files that are sentences from scraped texts, DO NOT CHANGE
	scraped_texts.example		- 	Contains text files that are text scraped from the urls, DO NOT CHANGE
	sys_color.py 				- 	File that contains functions to pring colored text in terminal to make debugging easier

## Steps to Run:
1) Create a copy of processed_texts.example and scraped_texts.example, and rename the copies to *processed_texts* and *scraped_texts* respectively
2) Delete Keyword_Database.sql, it will be rewritten when the code finish running
3) Navigate into the unzipped directory by using the cd command: ```cd <4395_webcrawler_proj directory's path>``` in terminal
4) In terminal, while in the directory containing all the files run the command: ```python3 main.py```
5) Your scraped text will be in scraped_texts, and your sentences will be in processed_texts, there should be a newly generated Keyword_Database.sql

## To see keywords chosen:
* Look for the headers, ```TOP 40 Terms:``` and ```TOP 10 TERMS USING DOMAIN KNOWLEDGE```. You can command/ctrl-f it to make it faster.

## To see sample query from database:
* Scroll to the bottom, and there should be outputs in bold pink. Those are query result's article's titles, the next line is the article description, and the next line after that is the url.
Example:
'The Batman' flies high with its dark and serious Dark Knight, but hangs around too long *in bold pink*
"The Batman" presents a muscular vision of the Dark Knight that hardcore fans have long desired, a dark and serious epic that's somewhat offset by two disclaimers: At nearly three hours, the movie hangs around too long, really feeling it down the stretch; and…
https://www.cnn.com/2022/03/04/entertainment/the-batman-review/index.html

## Note:
### Debugging texts about the crawler
* Text in pink/purple/blue that says ```current page <url>```, this tells what page the crawler is currently at
* Text in pink/purple/blue that says ```Going to next page <url>```, this tells that the crawler is going to the second page of the sub-reddit discussion
* Text in pink/purple/blue that says ```Parsing <url>```, this tells what url is currently being parsed. It is then followed by text in green that says ```SUCCESS: <url> written successfully as scraped_texts/url_x.txt```, this says that the parsing was sucessfuly and a text file with the scraped text was written out
* Text in yellow that says ```WARNING: <url> does not have enough data...```, this tells that this url page does not have enough text on it for it to have enough information
* Text in red that says ```ERROR: No Next Page!```, this tells that there is no more next page in the sub-reddit discussion
* If you see traceback errors like this: 
```Traceback (most recent call last):```
  ```File "/Users/feiyansu/Library/Python/3.8/lib/python/site-packages/twisted/internet/defer.py", line 857, in _runCallbacks```
    ```current.result = callback(  # type: ignore[misc]```
  ```File "/Users/feiyansu/Desktop/webcrawlerproj/crawler.py", line 49, in parse_page```
    ```sys.exit(0)```
```SystemExit: 0```
It's because I have not found a way to peacefully terminate the crawler once I hit a url-link counter of 20, and am using sys.exit(0), so just ignore it for now.

