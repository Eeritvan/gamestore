# Gamestore
The application is a digital gamestore. Users can browse, purchase and rate games. Each user has their own profile, which they can freely edit. The backend is built with Python and Flask, and the frontend uses HTML and CSS (+some JavaScript).

## Features
- Users can:
   - Login, logout and register
   - Browse games, add games to their wishlist, and add games to their cart
   - Search for games by name or categories
   - Add balance to their account (does not include real payment system)
   - View their game libraries, cart and wishlist
   - Review games
   - Visit other users profiles (if set public)
   - View their history
   - Delete their account
- Other features:
   - User roles include:
      - User: Normal user
      - Creator: Ability to add new games as well as discount, edit, delete their games.
      - Moderator: Can generally edit and remove any game or user. Can also view every profile even if set private.
   - Everyone can set their profile picture (if not set there are few default ones)
   - Everyone can edit their profiles and set it private/public

##  Running locally
Prerequisites:
- Python3 installed
- PostgreSQL installed
- Poetry installed

1. Clone this repository
2. Start your PSQL database.
3. Navigate to the gamestore directory and create a .env file:
   ```
   DATABASE_URL = <YOUR URL>
   SECRET_KEY = <YOUR SECRET KEY>
   ```
4. Install all dependencies by running:
     - `$ poetry install --no-root`
5. Create the database by running:
     - `$ psql < schema.sql`
     - `$ psql < inserts.sql`
6. Finally, run the application with the command `poetry run flask run` and navigate to the url `http://127.0.0.1:5000/`

## Running with Docker compose
Prerequisites:
- Docker installed

1. Clone this repository
2. Navigate to the gamestore directory and create a .env file:
   ```
   DB_PASSWORD = <YOUR PASSWORD>
   SECRET_KEY = <YOUR SECRET KEY>
   ```
3. Run `$ docker compose up --build`
4. Navigate to the url `http://127.0.0.1:5000/`

## Additional notes 
- You can change your role to "creator" or "moderator" by editing your profile. Once changed, a link to create new games should appear on "allgames" page.
- If you decide to run the application locally the database will be empty. Instead, the fly.io application will include some AI generated games and reviews already.
   - Most of the usernames / reviews / games were generated with OpenAI's ChatGPT.
   - All the images used in this project have been generated with Stable Diffusion XL 1.0 https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
      - The prompts/keywords used to generate images can be found on each games description