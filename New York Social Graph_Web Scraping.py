
# coding: utf-8

# ### Web Scrabing with The New York Social Graph Project

# In[ ]:


# [New York Social Diary](http://www.newyorksocialdiary.com/)  
#The data forms a natural social graph for New York's social elite.  #
#Link = [run-of-the-mill holiday party](http://www.newyorksocialdiary.com/party-pictures/2014/holiday-dinners-and-doers).

# In this project, we will assemble the social graph from photo captions for parties dated December 1, 2014, and before.  Using this graph, we can make guesses at the most popular socialites, the most influential people, and the most tightly coupled pairs.

# We will attack the project in three stages:
# 1. Get a list of all the photo pages to be analyzed.
# 2. Parse all of the captions on a sample page.
# 3. Parse all of the captions on all pages, and assemble the graph.


# ### Stage_1 (Getting a list of all the photo pages to be analyzed)

# In[ ]:


# The first step is to crawl the data.  
#We want photos from parties on or before December 1st, 2014.  
# Link = [Party Pictures Archive](http://www.newyorksocialdiary.com/party-pictures)


# In[ ]:


import requests
import dill
from bs4 import BeautifulSoup
from datetime import datetime
import dill
import nltk
from requests_futures.sessions import FuturesSession


# In[ ]:


page = requests.get('http://www.newyorksocialdiary.com/party-pictures')


# In[ ]:


soup = BeautifulSoup(page.text, "lxml")


# In[ ]:


#using BeautifulSoup's select or find_all methods to get the elements
parent = soup.find('div', attrs={'class':'view-content'})
links = soup.find_all('div', attrs={'class':'views-row'})


# In[ ]:


#50 per page
assert len(links) == 50


# In[ ]:


#extracting the URL of the link, as well as the date using `datetime.strptime`.  
link = links[0]
date=link.find('span', attrs={'class': 'views-field views-field-created'})
print(link.a['href'])
print(date.text)
# Check that the title and date match what you see visually.


# In[ ]:


#returning the URL and date parsed
def cleandate(date):
    import time
    date2=''.join(date.strip().split(',')[1:3])
    date2=time.strftime('%Y, %m, %d', time.strptime(date2, ' %B %d %Y'))
    return date2

def get_link_date(el):
    url=el.a['href']
    date=el.find('span', attrs={'class': 'views-field views-field-created'}).text
    date=cleandate(date)
    return url, date
url, date = get_link_date(links[0])
print(url, date)
print(date)


# In[ ]:


#writing a function to parse all of the links on a page
def get_links(page):
    soup = BeautifulSoup(page.text, "lxml")
    parent = soup.find('div', attrs={'class':'view-content'})
    links = parent.find_all('div', attrs={'class': 'views-row'})
    result =[]
    for link in links:
        result.append(get_link_date(link))
    return result # A list of URL, date pairs
results=get_links(page)


# In[ ]:


print(results[0][1])


# In[ ]:


# to get 50 pairs
assert len(get_links(page)) == 50


# In[ ]:


#writing a function to filter the list of dates to those at or before a cutoff
def filter_by_date(results, cutoff=datetime(2014, 12, 1)):
    import time
    cut_data=[]
    end_time=time.strptime('2014, 12, 1', '%Y, %m, %d')
    for result in results:
        cur_date=result[1]
        cur_date=time.strptime(cur_date, '%Y, %m, %d')
        if cur_date<=end_time:
            cut_data.append(result)
    return cut_data
    # Return only the elements with date <= cutoff


# In[ ]:


cut_data=filter_by_date(results)


# In[ ]:


#Adjusting the cutoff date


# In[ ]:


assert len(filter_by_date(get_links(page))) == 0


# In[ ]:


page1 = requests.get('http://www.newyorksocialdiary.com/party-pictures', params={'page': 0})


# In[ ]:


result=get_links(page1)
len(result)


# In[ ]:


print(result[0])


# In[ ]:


#getting all of the party URLs
from requests_futures.sessions import FuturesSession
def get_page_args(i):
    return {'url': 'http://www.newyorksocialdiary.com/party-pictures', 'params': {'page': i}}

session = FuturesSession(max_workers=5)
futures = [session.get(**get_page_args(i)) for i in range(32)]
all_links=[] #to get all_links without the 2014 date filtering #len of all_links: 1580
for future in futures:
    all_links.extend(get_links(future.result()))

link_list=[]
for future in futures:
    link_list.extend(filter_by_date(get_links(future.result())))
# You can use link_list.extend(others) to add the elements of others
# to link_list.


# In[ ]:


def filter_by_2014date(results, cutoff=datetime(2014, 12, 1)):
    import time
    cut_data=[]
    end_time=time.strptime('2014, 12, 1', '%Y, %m, %d')
    for result in results:
        cur_date=result[1]
        cur_date=time.strptime(cur_date, '%Y, %m, %d')
        if cur_date>end_time:
            cut_data.append(result)
    return cut_data
link_list2014=[]
for future in futures:
    link_list2014.extend(filter_by_2014date(get_links(future.result()))) #387 links after 2014


# In[ ]:


dill.dump(link_list2014, open('link_list_after2014.pkd','wb'))


# In[ ]:


#total of 1193 parties
assert len(link_list) == 1193


# In[ ]:


#in case,  saving the information to a file using `dill`
dill.dump(link_list, open('nysd-links.pkd', 'wb'))


# In[ ]:


#loading the list from the file to restore
link_list = dill.load(open('nysd-links.pkd', 'rb'))


# In[ ]:


#Getting the number of party pages for the 95 months
link_list[1]


# In[ ]:


import time
dates=time.strftime('%b-%Y', time.strptime(link_list[1][1], '%Y, %m, %d'))


# In[ ]:


def get_month_party_counts(link_list):
    count={}
    for link in link_list:
        dates=time.strftime('%b-%Y', time.strptime(link[1], '%Y, %m, %d'))
        count[dates]=count.get(dates, 0)+1
    return count


# In[ ]:


count=get_month_party_counts(link_list)
result=list(count.items())
def histogram():
    return result  # Replace with the correct list


# ### Stage_2 (Parsing all of the captions on a sample page.)
# 

# In[ ]:


#getting the names out of captions for a given page. 
#[Link 1](http://www.newyorksocialdiary.com/party-pictures/2015/celebrating-the-neighborhood) 
#[Link 2](http://www.lenoxhill.org/)


# In[ ]:


import requests
import dill
from bs4 import BeautifulSoup
from datetime import datetime


# In[ ]:


cap_response=requests.get('http://www.newyorksocialdiary.com/party-pictures/2015/celebrating-the-neighborhood')
captions_parent = BeautifulSoup(cap_response.text, 'lxml')
captions=captions_parent.find_all('div', attrs={'class': 'photocaption'})


# In[ ]:


#there are about 110
assert abs(len(captions) - 110) < 5


# In[ ]:


#As with the links pages, to avoid downloading a given page, 
#the next time we need to run the notebook.  
#While we could save the files by hand, as we did before, a checkpoint library 
#like [ediblepickle](https://pypi.python.org/pypi/ediblepickle/1.1.3) 
#can handle this.  


# In[ ]:


import spacy
import re
def clean(caption):
    caption = re.sub('\\t+|\\n+', '', str(caption.text).strip())
    caption = re.sub(r'Photograph.*', ' ', caption)
    caption = caption.strip()
    return caption

def get_captions(path):
    captions=[]
    response=requests.get('http://www.newyorksocialdiary.com{}'.format(path))
    soup = BeautifulSoup(response.text, 'lxml')
    captions.extend(list(set([clean(caption) for caption in soup.select('.photocaption')])))
    if len(captions)==0:  
        captions.extend(list(set([clean(caption) for caption in soup.select('.field__items td font')])))
    if len(captions)==0: 
        captions.extend(list(set([clean(caption) for caption in soup.select('div.collageformatter-collage-image__caption_content')])))
    if len(captions)==0:
        print(path)
    return captions


# In[ ]:


captions=get_captions('/party-pictures/2015/celebrating-the-neighborhood')
print([caption for caption in captions])


# In[ ]:


#getting the same captions
assert captions == get_captions("/party-pictures/2015/celebrating-the-neighborhood")


# In[ ]:


#there are sample captions, let's start parsing names out of those captions
import spacy
import re
nlp=spacy.load('en')
def get_names_from_captions(captions):   
    all_names=[] #names in each caption is saved as a list element in all_names
    i=0
    for caption in captions:
        names=[]
        i+=1
        if i%500==0:
            print(caption)
            print('{} captions have been processed by spacy'.format(i))
        caption = re.sub('’s|\'s|Jr\.', '', str(caption).strip())
        caption = re.sub('\&', 'and', caption)
        caption = re.sub('\\t+|\\n+| +', ' ', caption)
        caption = re.sub(r'Photograph*', '', caption)
        caption = re.sub(r'Mrs.', 'Amyy', caption)
        caption =caption.strip()
        if len(caption)==0:
            continue
        doc=nlp(caption)
        for obj in doc.ents:
            if obj.label_=='PERSON':
                name= re.sub(r'[A-Z]\.', '', str(obj).strip())
                name= re.sub(' +', ' ', name)
                name=name.strip()
                names.append(name)
        for idx in range(len(names)-1):
            if len(names[idx].split(' '))==1:
                names[idx]=names[idx]+' '+names[idx+1].split(' ')[-1]
        if len(names)!=0:
            all_names.append(names)
    return all_names


# In[ ]:


all_names=get_names_from_captions(captions)
print(len(captions))
print(len(all_names))


# In[ ]:


#all_names
name_res=[]
for names in all_names:
    name_res.extend(names)


# In[ ]:


#parsing all of the captions and extracting all the names mentioned. 
#Sorting them alphabetically, by first name, and 
#returning the first 100
def sample_names():
    return sorted(list(set(name_res)))[:100]


# ### Stage_3 (Parsing all of the captions on all pages)
# 

# In[ ]:


#running caption scraper and parser for all pages, 
#and all of the pages could take 10 minutes or so.


# In[ ]:


i=0
all_captions_revised = []
for link in link_list:
    if i%50==0:
        print('{} links of captions have been downloaded...'.format(i))
    all_captions_revised.extend(get_captions(link[0]))
    i+=1


# In[ ]:


print(len(all_captions_revised)) #101713


# In[ ]:


text= [str(caption) for caption in all_captions_revised[190:200]]
print(text)
print(len(all_captions_revised))


# In[ ]:


import itertools
def get_name_edges(all_names):
    edges=[]
    for names in all_names:
        edges.extend(list(itertools.combinations(names, 2))) #two-pair edge generation for the names in each caption
    return edges #lists of lists of edge tuples, each list element from one caption [[(p1, p2), (p1, p3), (p2,p3)], [(p4, p5)]]


# In[ ]:


from tqdm import tqdm_notebook as tqdm


# In[ ]:


get_ipython().run_cell_magic('time', '', 'all_links_names = get_names_from_captions(all_captions_revised)')


# In[ ]:


dill.dump(links_names, open('all_link_names_2014spacy_complete_{}.dpk'.format(i), 'wb'))


# In[ ]:


all_links_names=dill.load(open('all_link_names_2014spacy_complete.dpk', 'rb'))


# In[ ]:


all_links_names=dill.load(open('all_link_names_2014spacy_complete.dpk', 'rb'))


# In[ ]:


len(all_links_names) #92982


# In[ ]:


pop2={}
for i in all_links_names:
    for name in i:
        pop2[name]=pop2.get(name, 0)+len(i)-1
print(len(pop2))


# In[ ]:


import itertools
def get_name_edges(all_names):
    edges=[]
    for names in all_names:
        if len(names)<2:
            continue
        edges.extend(list(itertools.combinations(sorted(names), 2))) #two-pair edge generation for the names in each caption
    return edges #lists of lists of edge tuples, each list element from one caption [[(p1, p2), (p1, p3), (p2,p3)], [(p4, p5)]]

all_links_edges=get_name_edges(all_links_names) #197337
print(len(all_links_edges))


# In[ ]:


len(all_links_names)


# In[ ]:


len(all_captions_revised)


# In[ ]:


all_captions_revised[-10:]


# In[ ]:


all_links_names[-10:]


# In[ ]:


all_links_edges[-10:]


# In[ ]:


list(filter(lambda x: ('Susan Johnson' in x) and ('Henry Johnson' in x), all_links_edges))


# In[ ]:


list(filter(lambda x: 'Susan Johnson' in x[0], counts.items()))


# In[ ]:


from collections import Counter
counts=Counter(all_links_edges)
weighted_edges=[(i[0][0],i[0][1],i[1]) for i in counts.items()]
print(len(weighted_edges))
ques5=sorted(counts.items(), key=lambda x: x[1], reverse=True)[:100]


# In[ ]:


ques5[:5]


# In[ ]:


pop={}
for i in weighted_edges:
    pop[i[0]]=pop.get(i[0], 0)+i[2]
    pop[i[1]]=pop.get(i[1], 0)+i[2]


# In[ ]:


test=sorted(pop.items(), key=lambda x: x[1], reverse=True)[:100]


# In[ ]:


import pandas as pd
df=pd.DataFrame(test, columns=['name','popcount'])


# In[ ]:


df.describe()


# In[ ]:


test2=sorted(pop2.items(), key=lambda x: x[1], reverse=True)[:100]


# In[ ]:


df2=pd.DataFrame(test2,columns=['name','popcount'])
df2.describe()


# In[ ]:


dill.dump(test2, open('test2.dpk', 'wb'))


# In[ ]:


dill.dump(test2, open('test2.dpk', 'wb'))


# In[ ]:


import networkx as nx
G = nx.Graph()
G.add_weighted_edges_from(weighted_edges)
rank_res=nx.pagerank(G) #dictionary of ranking of each node
res=sorted(rank_res.items(), key=lambda x: x[1], reverse=True)[:100] #question 4 result
df3=pd.DataFrame(res,columns=['name','rank'])
df3.describe()


# In[ ]:


#analyzing the social graph of the New York social elite, using python's networkx library.
import itertools  # itertools.combinations may be useful
import networkx as nx


# ### The most popular
# 

# In[ ]:


import heapq  # Heaps are efficient structures for tracking the largest
              # elements in a collection.  Use introspection to find the
              # function you need.
def degree():
    return test2


# In[ ]:


def best_friends():
    return sorted(ques6, key=lambda x: x[1], reverse=True)

grader.score(question_name='graph__best_friends', func=best_friends)

