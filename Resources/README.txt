README
Required Files

App.py - Flask application entry point
Backendjune24.py - Constraint algorithm backend
GraphVisualisation.py - Node diagram generator (optional, used for dissertation write up)
static/
index.html
styles.css
script.js

==========================================================================================

Overview:
This application is a full-stack website that helps generate guitar chord positions using a combination of Python (for backend logic) and JavaScript (for frontend interaction).

How to Run the Application:
1. If you wish you can create a virtual Python environment to safely install the correct packages
to run the code. The following commands should create a venv (virtual environment) for you:

python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
Install Python Dependencies

2. The requirements.txt file included has all the libraries needed to run the python application. 
To install the dependencies simply use this command line code:

pip install -r requirements.txt

3. There is one JavaScript dependency that is also needed to be installed which can be installed with:
npm install

4. Run the Flask App to actually access the code/website
This will launch the website on local server port. 

Troubleshooting:
If the application fails to run locally, you can still access a live version of the project hosted at: https://guitar-survey.onrender.com.
Note: The hosted version may be slow and is not optimized for mobile devices.

File Descriptions
App.py: The Flask application that serves the website and handles API requests.
Backendjune24.py: The backend logic, including the constraint algorithm for generating chord positions.
GraphVisualisation.py: Not essential for the core project, but included for visualizing node diagrams used in the dissertation.
static/: Contains the front-end files (HTML, CSS, JavaScript) that run in the browser.
Enjoy! :)

