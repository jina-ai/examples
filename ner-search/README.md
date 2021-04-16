query:

restaurants in San Francisco

NER: [San Francisco] --> GEO

matches:

food in [San Francisco] -- higher match because same entity 

restaurants in [Los Angeles] -- higher because same entity type

bars in [New York] -- same as above
 
tomatoes are red -- irrelevant
 
horses on the field -- irrelevant

--- 

inedxing as normal

---

query

we get matches into the ranker

the ranker needs to know the original query -- in order to extract it and get its type

the ranker needs the model name -- passed as argument