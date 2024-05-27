# veronica
GPT-4o Powered Discord Chatbot

## Setup

1. **Clone the repository:**

   ```sh
   git clone https://github.com/King-INF3RN0/veronica.git
   cd veronica
   ```

2. **Create and activate the virtual environment:**
`
   ```sh
   python -m venv chatbot_env
   source chatbot_env/bin/activate  # On Windows use: chatbot_env\Scripts\activate
   ```

3. **Install the dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Create a `.env` file based on `.env.example`:**

   ```plaintext
   DISCORD_TOKEN=your_discord_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the bot:**

   ```sh
   python bot.py
   ```

6. **Increment the version number (optional):**

   ```sh
   python increment_version.py
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
