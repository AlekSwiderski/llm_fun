# Personal Finance Tracker

A minimal web app to track income and expenses. Built with Flask.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Initialize the database:
   ```bash
   flask --app backend.app init-db
   ```
3. Run the server:
   ```bash
   flask --app backend.app run
   ```

Open `http://127.0.0.1:5000` in your browser.

After registering or logging in, use the **Add** link to record new transactions.
Click **All** to see transactions from every user.
Use **Report** to view a summary of this month's spending by category.
You can edit or delete your entries from the list on the home page.
