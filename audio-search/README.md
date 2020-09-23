# Build an Audio Search 

A demo of neural search for audio data based on **Mel Frequency Cepstral Coefficients** 


Install Prerequisites
---------------------

    click
    pillow
    librosa
    jina[devel]==0.4.1
    
    
Download Data
-------------

To download the dataset run the below command 

    sh ./get_data.sh
    
## Run

| Command                  | Description                  |
| :---                     | :---                         |
| ``python app.py index``  | To index files/data          |
| ``python app.py search`` | To run query on the index    |
    