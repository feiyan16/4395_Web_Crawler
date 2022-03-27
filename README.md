## If you haven't already:
* Download and install scrapy by following the instructions from https://scrapy.org/download/
* Download and install scikit-learn by following the instructions from https://scikit-learn.org/stable/install.html
* Download and install nltk by following the instructions from https://www.nltk.org/install.html

## Overview:
1) Unzip 4395_webcrawler_proj.zip 
2) Files you should see: 	
	* **crawler.py** 			-	Code for web crawler/scraper
	* **Keyword_Database.sql** 		- 	SQL file that contains the knowledge-base
	* **main.py** 			- 	Code for parsing text, running tf-idf, and creating knowledge-base
	* **processed_texts.example**	- 	Contains text files that are sentences from scraped texts, DO NOT CHANGE
	* **scraped_texts.example**		- 	Contains text files that are text scraped from the urls, DO NOT CHANGE
	* **sys_color.py** 			- 	File that contains functions to pring colored text in terminal to make debugging easier
	* <img width="711" alt="image" src="https://user-images.githubusercontent.com/55895535/160305411-d97049b4-c7e4-4afa-b3c1-d22f41859743.png">

## Steps to Run:
1) Create a copy of processed_texts.example and scraped_texts.example, and rename the copies to **processed_texts** and **scraped_texts** respectively
2) Delete Keyword_Database.sql, it will be rewritten when the code finish running

	<img width="663" alt="image" src="https://user-images.githubusercontent.com/55895535/160305449-6f8e53a9-f67d-450c-807e-624da361e719.png">

4) Navigate into the unzipped directory by using the cd command: ```cd <4395_webcrawler_proj directory's path>``` in terminal
5) In terminal, while in the directory containing all the files run the command: ```python3 main.py```
6) Your scraped text will be in scraped_texts, and your sentences will be in processed_texts, there should be a newly generated Keyword_Database.sql

	<img width="1472" alt="image" src="https://user-images.githubusercontent.com/55895535/160305528-4ede6ef0-7398-49cb-9fef-53d2e3ccbac0.png">


## To see keywords chosen:
* Look for the headers, ```TOP 40 Terms:``` and ```TOP 10 TERMS USING DOMAIN KNOWLEDGE```. You can command/ctrl-f it to make it faster.

	<img width="1181" alt="image" src="https://user-images.githubusercontent.com/55895535/160305558-8abeb30d-88cb-4af8-8549-a4cae5316377.png">
	
* If you want to see the top 25 terms for each url page, you can uncomment ```CREATE KEYWORDS BY TOPICS:``` (cmd/ctrl-f it in the code), and the a csv will be outputted with the terms:

	<img width="749" alt="image" src="https://user-images.githubusercontent.com/55895535/160306001-097cbbe6-ca8c-4d0e-a3b7-c6b5f11d1197.png">


## To see sample query from database:
* Scroll to the bottom, and there should be outputs in bold pink. Those are query result's article's titles, the next line is the article description, and the next line after that is the url.

	Example:
	<img width="1177" alt="image" src="https://user-images.githubusercontent.com/55895535/160305567-64386ff4-c0ae-422b-9b36-124247b8c010.png">


## Note:
### Debugging texts about the crawler
* Text in pink/purple/blue that says ```current page <url>```, this tells what page the crawler is currently at

	Example:
	<img width="577" alt="image" src="https://user-images.githubusercontent.com/55895535/160305593-a1a91efc-f499-4308-a1ec-92de691970bc.png">

* Text in pink/purple/blue that says ```Going to next page <url>```, this tells that the crawler is going to the second page of the sub-reddit discussion

	Example:
	<img width="577" alt="image" src="https://user-images.githubusercontent.com/55895535/160305606-7f456c8e-5f41-42d0-b50a-b090be703e2c.png">

* Text in pink/purple/blue that says ```Parsing <url>```, this tells what url is currently being parsed. It is then followed by text in green that says ```SUCCESS: <url> written successfully as scraped_texts/url_x.txt```, this says that the parsing was sucessfuly and a text file with the scraped text was written out

	Example:
	<img width="1175" alt="image" src="https://user-images.githubusercontent.com/55895535/160305621-74ae0930-0b95-4469-a4e9-651462352db6.png">

* Text in yellow that says ```WARNING: <url> does not have enough data...```, this tells that this url page does not have enough text on it for it to have enough information

	Example:
	<img width="977" alt="image" src="https://user-images.githubusercontent.com/55895535/160305629-8200d2d8-fa5e-4cf7-a2eb-1318eb4ea776.png">

* Text in red that says ```ERROR: No Next Page!```, this tells that there is no more next page in the sub-reddit discussion

	Example:
	<img width="148" alt="image" src="https://user-images.githubusercontent.com/55895535/160305642-1429850a-8277-4822-8a73-7a515d3b977c.png">

* If you see traceback errors like this: 

	Example:
	<img width="868" alt="image" src="https://user-images.githubusercontent.com/55895535/160305661-b559035c-1917-4b1a-9248-b19030582e4b.png">

It's because I have not found a way to peacefully terminate the crawler once I hit a url-link counter of 20, and am using sys.exit(0), so just ignore it for now.

