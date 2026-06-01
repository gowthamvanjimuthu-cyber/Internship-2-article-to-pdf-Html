# 📄 Article to PDF & HTML Converter

A powerful hybrid tool designed to instantly convert online articles into beautifully formatted, downloadable PDF and HTML documents. This project combines a robust Python backend with a sleek, client-side web interface.

🔗 **Live Demo (MVP):** 
 https://gowthamvanjimuthu-cyber.github.io/Internship-2-article-to-pdf-Html/
 
🎯 **Project Goal**
To provide a seamless way for readers and researchers to archive web content in high-quality formats, removing ads and clutter while preserving essential typography and structure.

🚀 **Features**
- 🔍 **Smart Content Extraction**: Uses advanced parsing (Trafilatura & Readability.js) to isolate article text, metadata, and images from any public URL.
- 📄 **Premium PDF Generation**: Creates clean, academic-style PDFs with customized branding, justified text, and professional layouts.
- 🌐 **Clean HTML Exports**: Generates self-contained, responsive HTML files that look great on any device, even offline.
- 🌗 **Stunning Dark UI**: Features a modern, glassmorphic dashboard with smooth animations and intuitive controls.
- 📦 **Dual-Mode Architecture**:
  - **Local Model**: A Flask-powered backend for 100% extraction accuracy and high-fidelity ReportLab PDFs.
  - **Static MVP**: A fully browser-based converter optimized for GitHub Pages (no server required).
- 📚 **Massive Pre-Loaded Archive**: Includes over **316** pre-converted articles focused on Battery Technology, EVs, and Energy Storage by Neeraj Kumar Singal.

🧠 **AI & Automation Usage**
- **Automated Extraction Pipelines**: Uses heuristic-based algorithms to identify the main content of a webpage, bypassing banners, sidebars, and trackers.
- **Dynamic Layout Engine**: Automatically adjusts typography and spacing during PDF generation to ensure maximum readability across different article lengths.

🛠️ **Tech Stack**
- **Backend (Model)**: Python 3, Flask, Trafilatura, ReportLab, BeautifulSoup4.
- **Frontend (Web)**: HTML5, CSS3 (Vanilla), JavaScript (ES6+).
- **Client-Side Libraries**: jsPDF (PDF generation), Readability.js (Extraction), DOMPurify (Security).
- **Hosting**: GitHub Pages.

📱 **Application Flow**
1. **Input**: Paste a public article URL into the converter dashboard.
2. **Analysis**: The system fetches the webpage and extracts the title, author, description, and core body text.
3. **Generation**: Real-time generation of a styled HTML document and a formatted PDF.
4. **Download**: One-click download buttons for both formats appear instantly.

🔧 **Setup Instructions**

### Option 1: Local Backend (Full Features)
```bash
# Navigate to the Model directory
cd Model

# Install Python dependencies
pip install -r requirements.txt

# Start the Flask server
python app.py
```
Open your browser and navigate to `http://localhost:5000`.

### Option 2: Static Web Version (MVP)
Simply open the `index.html` file in any modern web browser or visit the live GitHub Pages link.

👨‍💻 **Author**
Gowtham K

📝 **Note**
This project was developed as part of an internship to demonstrate advanced web scraping, document generation pipelines, and modern UI/UX principles.
