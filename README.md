# veronica
GPT-4o Powered Discord Chatbot

## Setup Instructions

1. **Clone the repository:**
    ```sh
    git clone https://github.com/King-INF3RN0/veronica.git
    cd veronica
    ```

2. **Create a virtual environment:**
    ```sh
    python -m venv chatbot_env
    source chatbot_env/bin/activate  # On Windows use `chatbot_env\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up your environment variables:**
    - Create a `.env` file in the root directory with the following content:
        ```env
        DISCORD_TOKEN=your_discord_token
        OPENAI_API_KEY=your_openai_api_key
        ```

5. **Run the bot:**
    ```sh
    python bot.py
    ```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
