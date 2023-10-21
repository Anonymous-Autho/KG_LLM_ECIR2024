# KG_LLM_ECIR2024
Repository for the paper "Using knowledge graphs for semantic grounding of LLMs for query expansion in medical information retrieval"

The extensive use of electric health records has created a substantial volume of diverse patient-related data, all presented in the form of unstructured text, which could be exploited for query refinement and improving search precision. However, querying them in full could present challenges due to their unstructured and lengthy nature. Then, retrieval performance might decline due to the inclusion of irrelevant or noisy terms. Different language processing techniques have been exploited to extract valuable information from clinical narratives to address these limitations. Despite the promising capabilities of large language models, there have been concerns regarding their potential use in the medical domain due to their lack of understanding and reasoning, hallucinations, inconsistent responses, and reliance on outdated knowledge. To tackle these concerns, we present preliminary results of a retrieval-augmented generation approach to combine medical knowledge graphs and large language models for query expansion. Experimental evaluation was based on two benchmark TREC datasets for medical literature retrieval. Results showed that knowledge graphs can be successfully used for grounding LLMs in the medical domain, allowing them to control the information they rely on to provide answers, contributing to the development of explainable techniques based on LLMs.

Knowledge graph schema:
![Knowledge graph schema](https://github.com/Anonymous-Autho/KG_LLM_ECIR2024/blob/1408719e7cce395e0dc41ea917ffa944e3ed4ec5/graph_schema.png)

Included notebooks:
*	``parser-drugbank.ipynb``. Given the [full database.xml](https://go.drugbank.com/releases/help) file (it requires login), extract the relevant information for the prescribed drugs.
*	``parser-ICD9CM.ipynb``. Given the [ICD9CM.ttl](https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD9-CM/2011/) file, parses the information of the ICD9 diagnoses and mixes it with the PDD nodes.
*	``parser-umls.ipynb``. Scrape [https://uts-ws.nlm.nih.gov]( https://uts-ws.nlm.nih.gov) to get the information related to concept relations. Requires API key.
*	``contextual-datasets.ipynb``. Download and pre-process the required datasets. It also obtains the clinical notes and their corresponding ground truth.
*	``KG-extraction.ipynb``. Build the base graph according to [PDD Graph: Bidging Electronic Medical Records and Biomedical Knowledge Graphs via Entity Linking](https://github.com/wangmengsd/pdd-graph). Requires to download the base files from the github. It parses them and creates the node and edge structure.
*	``KG-to-tuples.ipynb``. Based on the extracted entities, build the triples that describe the medical knowledge graph.
*	``KG-neo4j-structure.ipynb``. From the created tuples, it builds some intermediate structures that have a more friendly format for neo4j.
*	``neo4j - db.ipynb``. Builds the neo4j database.
*	``neo4j - queries.ipynb``. DAG + LLM. Interation with the knowledge graph and LLM to create the corresponding queries.

Included scripts:
*	``create_index.py``. Given the downloaded snapshots of the documents, build and store de ``PyTerrier`` index for retrieval.
*	``run_queries.py``. Given a set of queries, execute them using the previously created document index. 

**Disclaimer:** Comments are in Italian, Spanish and English. In future commits, they will be all written in English.
