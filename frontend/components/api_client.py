"""API client for Streamlit frontend."""

import requests

API_BASE = "http://localhost:5001/api"


def get(endpoint, params=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=10)
        return r.json() if r.ok else {"error": r.text}
    except requests.RequestException as e:
        return {"error": str(e)}


def post(endpoint, data=None, files=None):
    try:
        if files:
            r = requests.post(f"{API_BASE}{endpoint}", data=data, files=files, timeout=30)
        else:
            r = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=10)
        return r.json() if r.ok else {"error": r.text}
    except requests.RequestException as e:
        return {"error": str(e)}


def put(endpoint, data=None):
    try:
        r = requests.put(f"{API_BASE}{endpoint}", json=data, timeout=10)
        return r.json() if r.ok else {"error": r.text}
    except requests.RequestException as e:
        return {"error": str(e)}


def delete(endpoint):
    try:
        r = requests.delete(f"{API_BASE}{endpoint}", timeout=10)
        return r.json() if r.ok else {"error": r.text}
    except requests.RequestException as e:
        return {"error": str(e)}
