# 🚀 Ultimate Guide: Hosting Django on Namecheap cPanel (2026)

This step-by-step guide ensures a seamless deployment of your Django app onto Namecheap Shared Hosting. Namecheap uses **Phusion Passenger** via cPanel's **Setup Python App** interface. 

Follow this guide precisely to avoid the common `500 Internal Server Error` traps.

---

## Step 1: Prepare Your Project Locally

Before moving files to Namecheap, ensure your project is production-ready.

1. **Update `requirements.txt`**:
   Make sure all your packages are listed.
   ```bash
   pip freeze > requirements.txt
   ```
2. **Database Settings (PostgreSQL/MySQL)**:
   You **can absolutely use PostgreSQL!** Namecheap supports both PostgreSQL and MySQL. Since you are using Postgres, ensure `psycopg2-binary` or `psycopg` is in your `requirements.txt`.
3. **Static Files (WhiteNoise)**:
   Ensure `whitenoise` is installed and added to `MIDDLEWARE` in `settings.py` so your CSS/JS loads correctly.
   ```python
   MIDDLEWARE = [
       # ...
       'django.middleware.security.SecurityMiddleware',
       'whitenoise.middleware.WhiteNoiseMiddleware',
       # ...
   ]
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   ```

---

## Step 2: Create the Python App in cPanel

1. Log into your **Namecheap cPanel**.
2. Scroll down to the **Software** section and click on **Setup Python App**.
3. Click the **Create Application** button.
4. Fill in the configuration:
   * **Python Version**: Select the version that matches your local environment (e.g., `3.9` or `3.10`).
   * **Application root**: Name of the folder where your project will live (e.g., `tutormatch_app`).
   * **Application URL**: Select the domain or subdomain where you want the app to appear.
   * **Application startup file**: Type `passenger_wsgi.py` (cPanel will create this for you).
   * **Application Entry point**: Type `application`.
5. Click **Create** at the top right.

> [!IMPORTANT]
> Once created, cPanel will show a command at the top of the page that looks like:
> `source /home/username/virtualenv/tutormatch_app/3.x/bin/activate`
> **Copy this command.** You will need it in Step 5.

---

## Step 3: Connect to GitHub (Git Version Control)

Instead of manually uploading files, we will link cPanel directly to your GitHub repository so you can easily pull updates.

1. Go back to cPanel Home and scroll to the **Files** section.
2. Click on **Git Version Control**.
3. Click the **Create** button.
4. Fill in the details:
   * **Clone URL**: Paste your GitHub repository URL (e.g., `https://github.com/yourusername/tutormatch.git`).
   * **Repository Path**: Enter the exact name of the folder you created in Step 2 (e.g., `tutormatch_app`).
   * **Repository Name**: Give it a recognizable name.
5. Click **Create**. cPanel will now clone your project files directly from GitHub into your application folder!

> [!TIP]
> **How to update your live site later:** Whenever you push new code to GitHub, simply go back to **Git Version Control** in cPanel, click **Manage** next to your repository, go to the **Pull or Deploy** tab, and click **Update from Remote**. Then, restart your Python app (Step 6) to see the changes!

---

## Step 4: Configure `passenger_wsgi.py`

Namecheap uses `passenger_wsgi.py` as the bridge between the server and your Django app.

1. In the File Manager, inside your `tutormatch_app` folder, you will see a file named `passenger_wsgi.py` (cPanel generated it).
2. Right-click and **Edit** it. 
3. Delete everything inside and replace it with this exact code:

```python
import os
import sys

# Add the project path to sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Replace 'config' with the name of the folder that contains your settings.py and wsgi.py if it ever changes
from config.wsgi import application
```
*(If your main project folder is named `tutor_match`, change `core.wsgi` to `tutor_match.wsgi`)*.

---

## Step 5: Install Dependencies and Migrate

1. Go back to cPanel Home. Scroll down to the **Advanced** section and click **Terminal**.
2. Paste the virtual environment activation command you copied in Step 2 and press Enter.
   *(Your terminal prompt should now show the virtual environment name in brackets).*
3. Run the following commands one by one:

```bash
# 1. Upgrade pip
pip install --upgrade pip

# 2. Install your project dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput
```

> [!CAUTION]
> Ensure you have created your PostgreSQL database and database user in the **PostgreSQL Databases** section of cPanel, assigned the user to the database, and updated your `.env` or `settings.py` before running migrations!

---

## Step 6: Restart and Test

1. Go back to **Setup Python App** in cPanel.
2. Find your application in the list and click the **Restart** icon (the circular arrow).
3. Open your browser and visit your domain. 

Your Django app should now be live! 

> [!TIP]
> If you ever make changes to your python code, you **must** click the "Restart" button in "Setup Python App" for the changes to take effect. Html/CSS changes usually apply instantly.
