🎓 AI-Powered Tutoring Call Analyzer
An advanced speech-to-text analysis tool designed to evaluate tutoring sessions for educational effectiveness. Supports both Kannada and English languages.
✨ Features
🎯 Smart Audio Chunking - Analyzes key moments throughout the session
🗣️ Speaker Diarization - Separates teacher and student speech (Sarvam STT)
📈 Learning Progress Tracking - Monitors student understanding evolution
💡 Teaching Effectiveness Analysis - Evaluates instructional methods
🌏 Multi-language Support - Kannada and English
📊 Comprehensive Reporting - Detailed insights and recommendations
🚀 Quick Start
Option 1: Use Deployed Version
Visit the live app: [Your App URL Here]
Option 2: Run Locally
Clone the repository:
bash
git clone https://github.com/yourusername/tutoring-call-analyzer.git
cd tutoring-call-analyzer
Install dependencies:
bash
pip install -r requirements.txt
Run the app:
bash
streamlit run app.py
🔑 API Keys Required
OpenAI API Key: For GPT-4 analysis and Whisper STT
Sarvam API Key: For advanced Indian language STT (optional)
Get your keys from:
OpenAI Platform
Sarvam AI
📁 Supported File Formats
WAV
MP3
M4A
FLAC
🎯 How It Works
Upload your tutoring call recording
Select STT provider (Whisper or Sarvam)
Enter API keys in the UI
Get comprehensive analysis including:
Learning progression
Teaching effectiveness
Student engagement levels
Recommendations for improvement
📊 Analysis Output
The tool provides:
Session Summary - Overview of the tutoring session
Learning Analysis - Student progress and mastery areas
Teaching Quality - Evaluation of instructional methods
Actionable Recommendations - Next steps and improvements
Speaker Diarization - Separate analysis of teacher/student speech
🌐 Language Support
Kannada (kn-IN) - Optimized with Sarvam STT
English (en-IN) - Available with both providers
Auto-detection - Whisper automatically detects language
🛠️ Technical Requirements
Python 3.8+
Streamlit
OpenAI Python SDK
Sarvam AI SDK
pydub for audio processing
📝 Contributing
Fork the repository
Create a feature branch
Make your changes
Submit a pull request
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
🤝 Support
For support and questions:
Create an issue in this repository
Contact the development team
🙏 Acknowledgments
OpenAI for Whisper and GPT-4 APIs
Sarvam AI for Indian language STT capabilities
Streamlit for the web framework
Built with ❤️ for better education
