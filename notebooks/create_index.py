import os

os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-11-openjdk'

print(os.environ['JAVA_HOME'])

import jnius_config
jnius_config.vm_running = False

import pyterrier as pt
if not pt.started():
    pt.init()


import pandas as pd
from tqdm import tqdm

def get_index(clinical_trials_dir, fields=['journal', 'title', 'abstract', 'body']):  # 'body'
    
    if os.path.exists(clinical_trials_dir + '/indices/' + clinical_trials_dir.split('.')[0] + '/data.properties'):
        index = pt.IndexFactory.of(clinical_trials_dir + '/indices/' + clinical_trials_dir.split('.')[0] + "/data.properties")
    else:
        
        documents = {}
        for documents_path in tqdm(os.listdir(clinical_trials_dir)):
            
            if not documents_path.endswith('.pickle'):
                continue
            
            print(documents_path)
            documents.update(pd.read_pickle(clinical_trials_dir + documents_path))
            print(len(documents))
            
        documents_to_pyt = []
        for k,d in documents.items():
            d['docno'] = k
            documents_to_pyt.append(d)
        
        print('Starting index...',len(documents_to_pyt))
        
        indexer = pt.IterDictIndexer(clinical_trials_dir + '/indices/' + clinical_trials_dir.split('.')[0], blocks=True, verbose=True)
        index_ref = indexer.index(documents_to_pyt, fields=fields)
        index = pt.IndexFactory.of(index_ref)
    
    print(index.getCollectionStatistics().toString())
    print(index.getMetaIndex().getKeys())
    
    return index
    
    
clinical_trials_dir = './'
get_index(clinical_trials_dir)