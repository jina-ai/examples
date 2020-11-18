<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Jina + Streamlit](#jina--streamlit)
  - [1. Run South Park Docker Image](#1-run-south-park-docker-image)
  - [2. Install requirements](#2-install-requirements)
  - [3. Start up the front end](#3-start-up-the-front-end)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Jina + Streamlit

## 1. Run South Park Docker Image

```bash
docker run -p 45678:45678 jinaai/hub.app.distilbert-southpark
```

## 2. Install requirements

```bash
pip install -r requirements.txt
```

## 3. Start up the front end

```bash
streamlit run app.py
```
