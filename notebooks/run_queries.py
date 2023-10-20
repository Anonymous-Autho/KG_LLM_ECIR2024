import pandas as pd
import os
import pickle
from tqdm import tqdm
import argparse

def get_formulated_queries(which_entities, which_evaluation):
    if isinstance(which_entities, str):
        which_entities = [which_entities]

    df_queries = None
    for we in which_entities:
        df = pd.read_pickle(clinical_trials_dir + we.replace('.pickle','_queries.pickle'))
        df = df.rename(columns={x: x + '__' + we for x in df.columns if x.startswith('q')})
        if df_queries is None:
            df_queries = df
        else:
            df_queries = df_queries.merge(df, on=['number', 'topics'])

    df_queries = df_queries[df_queries['topics'] == which_evaluation]
    df_queries = df_queries[[x for x in df_queries.columns if x.startswith('query') or x.startswith('q-exp') or x == 'number' or x == 'description']]

    for x in df_queries.columns:  # todo como str listo para ser buscado
        df_queries[x] = [y if isinstance(y, str) else ' '.join(y) for y in df_queries[x].values]
    
    for c in df_queries.columns:
        df_queries[c] = [x.replace("'",'').replace('?','').replace('+','').replace(':','').replace('/',' ').replace('\\','') for x in df_queries[c]]

    return df_queries


def get_base_queries(all_topics, which_evaluation):  # para obtener las queries de base del dataset en particular
    queries = []
    topics = all_topics[which_evaluation]
    for i in range(0, len(topics)):
        queries.append({'number': str(topics[i]['number']),
                        'topics': which_evaluation,
                        'description': topics[i]['description'].replace("'",'').replace('?','').replace('+','').replace(':','').replace('/',' ').replace('\\',''),
                        'query_summary': topics[i]['summary'].replace("'", '').replace('?', '').replace('+', '').replace(':','').replace('/',' ').replace('\\','')})

    queries = pd.DataFrame(queries)
    
    if '2021' not in which_evaluation:
    #if '2014' in which_evaluation or '2015' in which_evaluation:  # agregamos las queries de keywords que teníamos para 2021
        topics = all_topics['adhoc-queries.json']
        trec = which_evaluation.replace('topics', 'trec').split('.')[0]
        new_queries = []
        for i in range(0, len(topics)):

            if trec not in topics[i]['number'] and 'adhoc' not in which_evaluation:
                continue
                
            if 'adhoc' in evaluation:
                qq = {'number': str(topics[i]['number']),
                                        'topics': which_evaluation}
            else:
                qq = {'number': str(topics[i]['number'].split('-')[1]),
                                        'topics': which_evaluation}
                
           # qq = {'number': str(topics[i]['number'].split('-')[1]),
            #      'topics': which_evaluation}
            for key in topics[i]['keywords']:
                qq[f'query_{key["person"]}_{str(key["order"])}'] = key['keywords'].replace("'",'').replace('?','').replace('+','').replace(':','').replace('/','').replace('\\','')
            new_queries.append(qq)
        new_queries = pd.DataFrame(new_queries)
        queries = queries.merge(new_queries, left_on=['number', 'topics'], right_on=['number', 'topics'])

    return queries.fillna('')


def get_qrels(all_judgements,which_evaluation):
    evals = all_judgements[which_evaluation][0]
    listi = []
    for query,documents in evals.items():
        for d,r in documents.items():
            listi.append({'qid':str(query),'docno':str(d),'label':r})
    return pd.DataFrame(listi)


def search_queries(df_queries,retriever,path_s):
    # df_queries = df_queries.rename(columns={'number':'qid'})
    
    if os.path.exists(path_s):
        with open(path_s,'rb') as file:
            searches = pickle.load(file)
    else:
        searches = {}
    for c in tqdm(df_queries.columns):
        if not c.startswith('q'):
            continue
        if c not in searches:
            print('_______',c)
            searches[c] = retriever.transform(df_queries[['number',c]].rename(columns={'number': 'qid', c:'query'}))[['qid', 'docno', 'score', 'rank']]
            with open(path_s,'wb') as file:
                pickle.dump(searches,file)
    return searches


from pyterrier.measures import *

def compute_results(searches,df_all_queries,perquery=False,baseline=None,correction=None):

    # check whether dfs have results, remove those they don't, other solution would be to avoid saving with 0 results
    keys = set(searches.keys())
    for k in keys:
        if len(searches[k]) == 0:
            del searches[k]
    del keys

    results = pt.Experiment(
        list(searches.values()),
        df_all_queries.rename(columns={'number':'qid','description':'query'})[['qid','query']],
        q_rels,
        names=list(searches.keys()),
        eval_metrics=[AP(rel=2)@1,AP(rel=2)@5,AP(rel=2)@10,AP(rel=2)@20,AP(rel=2)@25,AP(rel=2)@1000,
                      AP(rel=1)@1,AP(rel=1)@5,AP(rel=1)@10,AP(rel=1)@20,AP(rel=1)@25,AP(rel=1)@1000,

                      RR(rel=2)@1,RR(rel=2)@5,RR(rel=2)@10,RR(rel=2)@20,RR(rel=2)@25,RR(rel=2)@1000,
                      RR(rel=1)@1,RR(rel=1)@5,RR(rel=1)@10,RR(rel=1)@20,RR(rel=1)@25,RR(rel=1)@1000,

                      P(rel=2)@1,P(rel=2)@5,P(rel=2)@10,P(rel=2)@20,P(rel=2)@25,P(rel=2)@1000,
                      P(rel=1)@1,P(rel=1)@5,P(rel=1)@10,P(rel=1)@20,P(rel=1)@25,P(rel=1)@1000,

                      Rprec(rel=2),

                      nDCG@1,nDCG@5,nDCG@10,nDCG@15,nDCG@20,nDCG@25,nDCG@1000,

                      R(rel=2)@1,R(rel=2)@5,R(rel=2)@10,R(rel=2)@15,R(rel=2)@20,R(rel=2)@25,R(rel=2)@1000,
                      R(rel=1)@1,R(rel=1)@5,R(rel=1)@10,R(rel=1)@15,R(rel=1)@20,R(rel=1)@25,R(rel=1)@1000,

                      NumRelRet(rel=2),
                      NumRelRet(rel=1),
                      NumRel,

                      Bpref(rel=2),
                      Bpref(rel=1)

                    ],
        baseline=baseline, # int indice de columna, no puedo pasar nombre
        perquery = perquery, # False/True
        correction=correction, # None, 'b'
        highlight= 'color',
        filter_by_topics = False, # no tiene ningún efecto, pero sin estos hay un problema interno de tipos
        #filter_by_qrels = False
    )
    return results

import os

os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-11-openjdk'
print(os.environ['JAVA_HOME'])

import jnius_config
jnius_config.vm_running = False

import pyterrier as pt
if not pt.started():
    pt.init()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Running queries')
    parser.add_argument('--data_path', type=str, default='./', metavar='N', help='where to find the data')
    parser.add_argument('--index_path', type=str, default='./', metavar='N', help='where to find the index')
    parser.add_argument('--which_evaluation', type=str, default=None, metavar='N', help='which evaluation to use: topics2014.xml, topics2015B.xml, topics2021.xml, adhoc-queries.json')
    parser.add_argument('--queries_path', type=str, default=None, metavar='N', help='queries file to use as input')

    args = parser.parse_args()

    clinical_trials_dir = args.data_path
    index_dir = args.index_path
    which_evaluation = args.which_evaluation

    matching_files = {} # matching = {name : {topics: XX, qrels: XX}}
    matching_files['topics2014.xml'] = 'qrels2014.txt'
    matching_files['topics2015B.xml'] = 'qrels-treceval-2015.txt'
    matching_files['topics2021.xml'] = 'qrels2021.txt' # este lleva otro
    matching_files['adhoc-queries.json'] = 'qrels-clinical_trials.txt' # las queries de este pueden matchear con el topics2014

    all_topics = pd.read_pickle(clinical_trials_dir + '__all_topics.pickle')
    print(all_topics.keys())

    all_judgements = pd.read_pickle(clinical_trials_dir + '__all_judgements.pickle')
    print(all_judgements.keys())

    which_entities__ = ['df_clinical_bert.pickle',
                        'df_stanza_craft.pickle',
                        'df_spacy_model_en_ner_bionlp13cg_md.pickle',
                        'df_spacy_model_en_ner_craft_md.pickle',
                        'df_spacy_model_en_core_sci_lg.pickle',
                        'df_spacy_model_en_ner_bc5cdr_md.pickle',
                        'df_spacy_model_en_core_med7_trf.pickle',
                        'df_topics_biobert.pickle']
    
    if args.queries_path is None:
        print('Building queries...')
        df_queries = get_formulated_queries(which_entities__,which_evaluation) # esto tiene todas las queries para el which_evaluation

        df_base_queries = get_base_queries(all_topics,which_evaluation)
        df_base_queries = df_base_queries[df_base_queries['topics'] == which_evaluation]

        df_all_queries = df_base_queries.merge(df_queries,on=['number'],how='left')

        print(df_all_queries.columns)

        df_all_queries.to_csv(clinical_trials_dir + f'__df_all_queries_{which_evaluation}.csv')
        df_all_queries.to_pickle(clinical_trials_dir + f'__df_all_queries_{which_evaluation}.pickle')
    else:
        print('Loading queries...')
        df_all_queries = pd.read_pickle(clinical_trials_dir + args.queries_path)
        for x in df_all_queries.columns: # this should not be needed, but, just in case
            df_all_queries[x] = [str(y).replace("'",'').replace('?','').replace('+','').replace(':','').replace('/','').replace('\\','') for y in df_all_queries[x]]
     

    q_rels = get_qrels(all_judgements,matching_files[which_evaluation])
    print('len qrels:',len(q_rels))

    print(q_rels)


    index = pt.IndexFactory.of(index_dir + "/data.properties")
    bm25 = pt.BatchRetrieve(index, wmodel="BM25") #properties={"termpipelines" : "Stopwords,PorterStemmer"}
    
    path_searches = clinical_trials_dir + f'__searches_{which_evaluation}.pickle'
    if args.queries_path is not None:
        path_searches = path_searches.replace('.pickle','__' + args.queries_path)
        
    if not os.path.exists(path_searches):
        print('---------------- searching queries')
        searches = search_queries(df_all_queries,bm25,clinical_trials_dir + path_searches.replace('__searches_','__searches_aux_'))
        #searches.keys()
        with open(path_searches,'wb') as file:
            pickle.dump(searches,file)
    else:
        searches = pd.read_pickle(path_searches)
  
    perquery = False  # True, False
    baseline = None  # 0, None
    correction = None  # 'b', None
    path_results = clinical_trials_dir + f'retrieval_results_perquery-{str(perquery)}_baseline-{str(baseline)}_{which_evaluation}.xlsx'
    if args.queries_path is not None:
        path_results = path_results.replace('.pickle','__' + args.queries_path)
    
    if not os.path.exists(path_results):
        print('Computing results')
        results = compute_results(searches,df_all_queries,perquery=perquery,baseline=baseline,correction=correction)
        results.to_excel(path_results)
    
    print('--------------------------------------- done')