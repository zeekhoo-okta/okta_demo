# Demo App for Okta

### Local setup
You can run this demo locally:

1. Clone this repository. Then 'cd' into its directory.
1. Create a virtualenv environment.
    ```bash
    virtualenv venv
    source venv/bin/activate
    ```
1. Install requirements.
    ```bash
    pip install -r requirements.txt
    ```
1. Rename ".env_copy" to ".env".
1. Edit .env and provide your OKTA_API_TOKEN and OKTA domain name.
    Below, replace "secret" with your own API token. Replace <okta tennant subdomain> with your environment's subdomain
    ```
    export OKTA_API_TOKEN="secret"
    export OKTA_ORG="<okta tennant subdomain>.oktapreview.com"
    ```
1. Source env.
    ```bash
    source .env
    ```
1. Start the server.
    ```bash
    python manage.py runserver
    ```
