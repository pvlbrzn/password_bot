# 🔐 PasswordBot — Telegram Password Strength Checker Bot

PasswordBot is a Telegram bot that helps users evaluate the strength of their passwords, receive improvement suggestions, and generate secure ones. It also checks if a password has appeared in known data breaches using the [Have I Been Pwned](https://haveibeenpwned.com/) API.

## 🚀 Features

* ⏱ Estimates time to crack a password
* 📉 Checks against common passwords and data breaches (HIBP API)
* 🧠 Generates strong, random passwords
* 💡 Provides best practices for creating secure passwords
* 🤖 User-friendly Telegram interface with reply buttons

## 🧑‍💻 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/pvlbrzn/password_bot.git
cd password_bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a .env File

Create a `.env` file in the root directory with your Telegram bot token:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### 4. Run the Bot

```bash
python main.py
```

## 🛠 Technologies Used

* [Python 3.8+](https://www.python.org/)
* [Aiogram](https://docs.aiogram.dev/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)
* [Have I Been Pwned API](https://haveibeenpwned.com/API/v3)

## 📋 Usage

* Send a password to the bot — it will evaluate and provide recommendations
* Press **"Generate Password"** — get a secure, random password
* Press **"Password Tips"** — learn best practices for creating strong passwords

## 📁 Project Structure

```
password_bot/
├── main.py                # Main bot logic
├── .env                   # Environment variables
├── requirements.txt       # Project dependencies
├── README.md              # Documentation
```

## 🔐 Security Notice

* Passwords are **not stored** or shared.
* Breach checks use secure `k-Anonymity` methods (HIBP).

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for more details.

## 🙋‍♂️ Author

Developed by [Pavel Berezan](https://github.com/pvlbrzn). Feel free to star ⭐ the repo and contribute!
