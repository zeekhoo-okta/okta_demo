# Demo App for Okta

#### This project is built with Django. It runs on Python 2.7+

### Local setup
You can run this demo locally:

1. Clone this repository. Then 'cd' into its directory.
2. Create a virtualenv environment.
    ```
    virtualenv -p <path-to-Python2.7> venv
    ```
3. Activate the virtualenv
    ```
    source venv/bin/activate
    ```
4. Install requirements
    ```
    pip install -r requirements.txt
    ```
5. Rename ".env_copy" to ".env".
6. Edit .env and provide your OKTA_API_TOKEN and OKTA domain name. Replace "secret" with your own API token. Replace ```<okta tennant subdomain>``` with your environment's subdomain.
7. Source env.
    ```
    source .env
    ```
8. Make migrations
    ```
    python manage.py migrate
    ```
9. Start the server
    ```
    python manage.py runserver
    ```