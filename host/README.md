# Audio Downloader & Channel Recorder (Streamlit)

A web-based application built with **Streamlit + Python** that allows authenticated users to download and manage recordings from single or dual channels.

---

## Features

* User login authentication
* Single channel recording
* Dual channel recording
* Download management
* Recording storage system
* Log tracking
* Simple web UI

---

## Tech Stack

* Python
* Streamlit
* JSON user authentication
* Environment variables (.env)
* FFmpeg

---

## Project Structure

```
app.py                → Main Streamlit UI
auth.py               → Login authentication
downloader.py         → Download controller
single_channel.py     → Single channel processing
dual_channel.py       → Dual channel processing
users.json            → User accounts
logs/                 → Download logs
recordings/           → Saved recordings
```

---

## Installation (Run Locally)

### 1. Clone repository

```
git clone https://github.com/YOUR_USERNAME/audio-downloader.git
cd audio-downloader
```

### 2. Create virtual environment

```
python -m venv venv
```

Activate:

Windows:

```
venv\Scripts\activate
```

Mac/Linux:

```
source venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Setup environment variables

Create `.env` file:

```
DB_HOST=your_host
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_db
```

### 5. Run application

```
streamlit run app.py
```

Open browser:

```
http://localhost:8501
```

---

## Deployment

The project is deployed using **Streamlit Cloud** directly from GitHub.

---

## Security Notice

* `.env` is not uploaded to GitHub
* Credentials are stored using Streamlit Secrets
* `.gitignore` protects sensitive files

---

