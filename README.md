# Gamestore
This repository is for a project made for a University of Helsinki course. The application is supposed to act like a digital gamestore. Users can browse, purchase and rate games. Each user also has their own profile, which they are free to edit.

## Features
- Users can:
   - Login, logout and register
   - Browse games, add games to their wishlist, and add games to their cart
   - Add balance to their account (does not include real payment system)
   - View their game libraries, cart and wishlist
   - Review games
   - Visit other users profiles
- Other features:
   - User roles include:
      - User: Normal user
      - Creator: Ability to add new games as well as discount, edit, delete their games.
      - Moderator: Can generally edit and remove any game or user. Can also view every profile even if set private.
   - Users can search for games by name or categories
   - Everyone can set their profile picture (if not set there are few default ones)
   - Everyone can edit their profiles and set it private/public
   - Users can view their history
   - Users can also delete their account

## Progress
Currently this project is well underway. Basically, all the features and functionality have been added and the final app probably won't see any new major functionality. In the coming weeks the primary focus is on enhancing the user interface and overall experience as well as properly coding and fixing the mess that all the HTML templates currently are.

## Testing app on fly.io
The application can be tested at https://tsoha-pelikauppa.fly.dev/. The fly.io version of the application also includes some games and reviews already instead of being completely empty. Please note that loading might sometimes be a bit slow, especially if site happens to contain images. Also the timezone is a few hours behind on fly.io.

##  Running locally
Prerequisites:
- Python3 installed
- PostgreSQL installed

1. Clone this repository
2. Start your PSQL database. If you downloaded PSQL with the script provided in the material you can start it with command: `$ start-pg.sh`. Make sure to keep the database running in the background.
3. Navigate to the TSOHA-pelikauppa directory and create a .env file:
   ```
   DATABASE_URL = <YOUR URL>
   SECRET_KEY = <YOUR SECRET KEY>
   ```
4. Inside the directory create virtual environment with following commands:
     - `$ python3 -m venv venv`
     - `$ source venv/bin/activate`
5. Install all dependencies by running:
     - `(venv) $ pip install -r requirements.txt`
6. Create the database by running:
     - `(venv) $ psql < schema.sql`
7. Finally, run the application with the command `flask run` and navigate to the url `http://127.0.0.1:5000/`

## Additional notes 
- You can change your role to "creator" or "moderator" by editing your profile. Once changed, a link to create new games should appear on "allgames" page.
- If you decide to run the application locally the database will be empty. Instead, the fly.io application will include some games and reviews already. 
- All the images have been locally generated with Stable Diffusion XL 1.0 https://github.com/Stability-AI/generative-models
    - The prompts used to generate these images can be found on each games description