import stackexchange
import os 
import pandas as pd
import datetime 
from dotenv import load_dotenv
from sklearn.feature_extraction.text import CountVectorizer 

load_dotenv()  # take environment variables from .env.

pagesize = 10
so = stackexchange.Site(stackexchange.StackOverflow, app_key=os.getenv("API_KEY"), impose_throttling=True)

def find_ngrams(input_lists_of_strings, n):
    
    vectorizer = CountVectorizer(ngram_range=(n,n), token_pattern=r'\b\w+\b', min_df=1)
    analyzer = vectorizer.build_analyzer()
    
    # create tuple of (ngram, count, type (unigram, bigram, trigram))
    ngrams = [(ngram, count, n) for ngram, count in zip(analyzer(' '.join(input_lists_of_strings)), vectorizer.fit_transform(input_lists_of_strings).toarray().sum(axis=0))]
    
    # sort by count
    ngrams.sort(key=lambda x: x[1], reverse=True)
    
    return ngrams


if __name__ == '__main__':
    # qs = so.search(intitle='python')
    # recent_questions = so.recent_questions(pagesize=100)
    
    # get yesterday epoch time
    yesterday = int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())
    
    # get all questions asked yesterday
    recent_questions = so.questions(pagesize=pagesize, fromdate=yesterday, todate=yesterday)
    
    recent_questions = recent_questions[:10]
        
    all_so_dicts = []
    
    for index, q in enumerate(recent_questions):
        print(index, q)

        dict_obj = {}
        
        all_attributes = dir(q)
        end_attributes = ["id", "title", "creation_date", "link", "score", "view_count", "tags","answer_count", "is_answered"] #  "owner", 
        
        # check if the attribute is in the list of attributes. 
        # If it is, then add it to the dictionary. If it's not, then add None to the dictionary for that attribute.
        for attribute in end_attributes:
            if attribute in all_attributes:
                dict_obj[attribute] = getattr(q, attribute)
            else:
                dict_obj[attribute] = None
        
        all_so_dicts.append(dict_obj)
    
    
    titles = [q['title'] for q in all_so_dicts]
    
    unigrams = find_ngrams(titles, 1)
    bigrams = find_ngrams(titles, 2)
    trigrams = find_ngrams(titles, 3)
    
    # merge all ngrams into one list
    ngrams = unigrams + bigrams + trigrams
    
    # convert to df
    df = pd.DataFrame(ngrams, columns=['ngram', 'count', 'type'])    
    df['type'] = df['type'].apply(lambda x: 'unigram' if x == 1 else 'bigram' if x == 2 else 'trigram')
    
    df_2 = pd.DataFrame(all_so_dicts)
    
    yesterday_string = datetime.datetime.fromtimestamp(yesterday).strftime('%Y-%m-%d')

    df['export_date'] = yesterday_string
    df_2['export_date'] = yesterday_string
    
    print(df)
    print(df_2)
    
    df.to_csv('ngrams.csv', index=False)
    df_2.to_csv('questions.csv', index=False)
    
    # create excel file with two sheets
    # writer = pd.ExcelWriter('stack_overflow_api_export.xlsx', engine='xlsxwriter')
    
    # write each dataframe to a different worksheet
    # df.to_excel(writer, sheet_name='ngrams')
    # df_2.to_excel(writer, sheet_name='questions')