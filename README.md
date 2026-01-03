# Email Generator (Mail.tm) 📧

A modern, high-performance desktop application for generating and managing temporary email addresses using the Mail.tm API. Built with Python and Tkinter, optimized for both Windows and macOS.

## ✨ Features

- **Modern & Beautiful UI**: A clean, responsive design with support for both **Dark** and **Light** modes.
- **High DPI Support**: Crystal clear text and icons on high-resolution displays (4K, Retina).
- **Intelligent Generation**: Meaningful, readable email addresses (e.g., `happy-tiger-123@domain.com`) instead of random character strings.
- **Productivity Focused**:
    - **Click-to-Copy**: Just click the email bar to instantly copy it to your clipboard.
    - **Drag & Drop Reordering**: Organize your saved addresses by simply dragging them in the list.
    - **Smart Search**: Filter through your saved addresses with a debounced search bar and instant clear button.
- **Live Inbox**: Automatic background polling for new messages without freezing the interface.
- **Standalone Ready**: Designed to be packaged as a single executable without heavy external dependencies.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- `requests` library

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/panawel/email_generator.git
   cd email_generator
   ```
2. Install dependencies:
   ```bash
   pip install requests
   ```

### Running the App
```bash
python main.py
```

## 🛠 Built With
- **Python**: Core logic and networking.
- **Tkinter/TTK**: Native, fast, and cross-platform GUI.
- **Mail.tm API**: Powering the temporary email service.

## 📝 License
This project is for educational and personal use. Please refer to Mail.tm's terms of service for API usage policies.
