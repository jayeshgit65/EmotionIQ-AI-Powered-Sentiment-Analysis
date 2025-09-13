# EmotionIQ – AI-Powered Sentiment Analysis

**EmotionIQ** is a Flask-based web application that performs **sentiment analysis** on **text input**, **uploaded files** (TXT, PDF, DOCX), or **web pages**.
It uses **TextBlob** and **VADER** to provide a reliable sentiment classification with confidence levels and emotion mapping.
Users can also **download a detailed PDF report** of the analysis.

---

## Features

* **Multiple Input Sources**

  * Direct text entry
  * File uploads (`.txt`, `.pdf`, `.docx`)
  * Website URLs
* **Multimodal Sentiment Detection**

  * TextBlob polarity and subjectivity
  * VADER compound score
  * Combined confidence calculation
* **Emotion Mapping**

  * Positive → Joy / Satisfaction
  * Negative → Anger / Sadness
  * Neutral → Calm / Neutral
* **PDF Report Generation**

  * Detailed sentiment report with preview, word & character counts
  * Downloadable for sharing or documentation
* **Real-Time Analysis**

  * Instant feedback via Flask session management
* **Secure File Handling**

  * Only allows TXT, PDF, DOCX
  * Files automatically deleted after processing
* **CORS Support**

  * Ready for frontend integration or external calls

---

## Notes on URL Analysis

* When analyzing website content, **EmotionIQ scrapes raw text from the page** using `requests` and `BeautifulSoup`.
* To prevent overly long processing, the **text is sliced to the first \~5000 characters** if large.

  * This is why `char_count` often appears around 5000 for web pages.
* Scripts, styles, and HTML elements are removed for cleaner sentiment analysis.

---

## Requirements

* Python 3.8+
* Flask, Flask-CORS
* TextBlob, NLTK (`punkt`, `stopwords`)
* VADER Sentiment (`vaderSentiment`)
* PyPDF2, python-docx
* Requests, BeautifulSoup4
* ReportLab

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/jayeshgit65/EmotionIQ-AI-Powered-Sentiment-Analysis.git
cd EmotionIQ-AI-Powered-Sentiment-Analysis
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Download NLTK data (once)**

```bash
python -m nltk.downloader punkt stopwords
```

---

## Usage

1. **Start the Flask server**

```bash
python app.py
```

2. **Open in browser**

```
http://localhost:5000
```

3. **Perform analysis**

* Enter text directly
* Upload a `.txt`, `.pdf`, or `.docx` file
* Enter a website URL

4. **View results**

* Sentiment, emotion, confidence, word count, character count
* Text preview and confidence bar chart

5. **Download PDF Report**

* Click **"Download PDF Report"** to save the analysis

---

## Project Structure

```
.
├── app.py              # Main Flask application
├── templates/
│   ├── index.html      # Home page input UI
│   └── results.html    # Results page with sentiment display and chart
├── uploads/            # Temporary file uploads (auto-cleaned)
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## API Endpoints

* `GET /` – Home page
* `POST /` – Process sentiment analysis from text, file, or URL
* `GET /results` – View sentiment analysis results
* `GET /download` – Download sentiment analysis report as PDF

---

## License

MIT License