# Jina + Streamlit

A simple front-end for [Jina](http://www.jina.ai) neural search framework, written in [Streamlit](http://www.streamlit.io), that supports querying with image, text, or drawing on a canvas.

## 1. Clone repo, install requirements

```bash
git clone https://github.com/alexcg1/jina-streamlit-frontend.git
cd jina-streamlit-frontend
pip install -r requirements.txt
```

## 1. Run Docker image

For text:

```bash
docker run -p 45678:45678 jinaai/hub.app.distilbert-southpark
```

For image:

```bash
docker run -p 65481:65481 -e "JINA_PORT=65481" jinaai/hub.app.bitsearch-pokedex search
```

## 3. Start up Streamlit front end

```bash
streamlit run app.py
```

## 4. Set endpoint

Use whatever Docker says is the right URL and port (in examples above, `45678` or `65481`)

![](.github/images/endpoint.png)

## 5. Search!

<table>
<tr>
<td>Text</td>
<td>Image</td>
<td>Draw</td>
</tr>


<tr>
<td>
<img src=".github/images/text.gif" width=300>
</td>
<td>
<img src=".github/images/image.gif" width=300>
</td>
<td>
<img src=".github/images/draw.gif" width=300>
</td>
</tr>
</table>
