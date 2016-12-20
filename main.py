#pip install -r requirements.txt

#BeautifulSoup is for pullling data from HTML for parsing later
from bs4 import BeautifulSoup
#requests is for pulling and pushing data from the web
import requests
#for performing regular expressions
import re
#is a wrapper around existing python functions i.e. addition
#makes things more readable
import operator
#json helps with parsing data
#is a format for parsing data
import json
#takes a lists of lists and displays a nicely formatted table
from tabulate import tabulate
#make system calls i.e. user input
import sys
#words that don't matter i.e. at, the, to
from stop_words import get_stop_words

##functions
#get the words
def getWordList(url):
    wordList = []
    #get raw data
    sourceCode = requests.get(url)
    #convert data to text
    plainText = sourceCode.text	
    #lxml format
    soup = BeautifulSoup(plainText, 'lxml')
    
    #grab all the words
    for article in soup.findAll():
        if article.text is None:
           continue

        #content in article
        content = article.text

	#saves the article to a text file
	#for checking purposes
		#file = open('batmanarticle.txt', 'w')
		#file.write(content.encode('utf-8'))
		#file.close()
	
	#convert each word to lowercase and split it into an array	
	words = content.lower().split()
	
        #put cleaned words into an array
        for word in words:
            #remove non characters
	    #print(word)
            cleanedWord = cleanWord(word)
	
            if len(cleanedWord) > 0:
                wordList.append(cleanedWord)

	return wordList

def cleanWord(word):
    
    #regex to get rid of any characters that are not letter
    cleanedWord = re.sub('[^A-Za-z]+', '', word)

    return cleanedWord

def createFrequencyTable(wordList):

    wordCount = {}
    for word in wordList:
        #the index is the word
        if word in wordCount:
            wordCount[word] += 1
        else:
            wordCount[word] = 1

    return wordCount

#remove stop words
def removeStopWords(frequencyList):

    stopWords = get_stop_words('en')

    tempList = []

    for key, value in frequencyList:
        if key not in stopWords:
            tempList.append([key, value])

    return tempList

#api link in json
wikipedia_api_link = "https://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srsearch="
wikipedia_link = "https://en.wikipedia.org/wiki/"
#get user input if it's the correct length
if (len(sys.argv) < 2):
    print("Enter a valid string")
    exit()

##This program will be run through the terminal as main.py batman yes
##if there are more that 2 arguments then remove stop words
#get the search word
string_query = sys.argv[1]
if (len(sys.argv) > 2):
    search_mode = True
else:
    search_mode = False

#create the URL
#this url returns all the wikipedia articles related to the search query
url = wikipedia_api_link + string_query

#make the request using a try/accept block
#handle any exceptions that occur
try:

    #use requests library to get the url information
    response = requests.get(url)
    #use JSON to load the data from the response in UTF-8
    data = json.loads(response.content.decode('utf-8'))

    #format the data
    #this retrieves words from the first article
    #wikipediaPageTag stores the first link wikipedia provides
    wikipediaPageTag = data['query']['search'][0]['title']

    #create the new url that leads to the first link wikipedia provides
    url = wikipedia_link + wikipediaPageTag
    #getWordList() gets the words from the wikipedia page
    pageWordList = getWordList(url)
    print(pageWordList[0])
    #createFrequencyTable() creates a frequency table of the words in page_word_list
    pageWordCount = createFrequencyTable(pageWordList)
    #sorts the frequency list from largest count to smallest count	
    sortedWordFrequencyList = sorted(pageWordCount.items(), key = operator.itemgetter(1), reverse = True)

    #remove stop words if that option was specified in command line args
    if(search_mode):
        #remove_stop_words() uses regex to remove stop words
	#returns as a list of lists
        sortedWordFrequencyList = removeStopWords(sortedWordFrequencyList)

    #sum the total words to calculate frequencies
    totalWordSum = 0
    for key, value in sortedWordFrequencyList:
        #for all the words in the list get the sum
        #the sum is the frequency count
        totalWordSum = totalWordSum + value

    #get the top 20 words if the list is greater than 20 words
    if (len(sortedWordFrequencyList) > 20):
        sortedWordFrequencyList = sortedWordFrequencyList[:20]

    #final list, words + frequency + percentage
    finalList = []
    for key, value in sortedWordFrequencyList:
        #how often the word appears as a percentage
        percentageValue = float(value * 100) / totalWordSum
        finalList.append([key, value, round(percentageValue, 4)])

    printHeaders = ["Word", "Frequency", "Frequency Percentage"]
    print(tabulate(finalList, headers = printHeaders, tablefmt = 'orgtbl'))

#throw an exception in case it breaks
except requests.exceptions.Timeout:
    print("The server didn't respond. Please, try again later.")

except requests.exceptions.ConnectionError:
	print("Too many requests. Connection refused")


