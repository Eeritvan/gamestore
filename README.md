# Gamestore
This repository is for a project made for a University of Helsinki course. The application is supposed to act like a digital gamestore. Users can browse, purchase and rate games. Each user also has their own profile, which they are free to edit.

## Features
- Users can:
   - Login, logout and register
   - Browse games, add games to their wishlist, and add games to their cart
   - search for games by name or categories
   - Add balance to their account (does not include real payment system)
   - View their game libraries, cart and wishlist
   - Review games
   - Visit other users profiles (if set public)
   - view their history
   - delete their account
- Other features:
   - User roles include:
      - User: Normal user
      - Creator: Ability to add new games as well as discount, edit, delete their games.
      - Moderator: Can generally edit and remove any game or user. Can also view every profile even if set private.
   - Everyone can set their profile picture (if not set there are few default ones)
   - Everyone can edit their profiles and set it private/public

## Progress (21.4)
- The layout is mostly done but still might need some tweaking. I'll especially try to improve the website's accessibility by tweaking some colors and adding borders to some of the elements for better visibility. Also the buttons might be a bit hard to see sometimes and should be improved. Currently the website also works fairly well on older browsers but there's an issue with some of the icons showing up as text. I'll try to investigate a way to only render such elements on modern browsers.
- I might redo some of the error messages to show up on the same page error occurred for better user experience.
- The frontpage is still empty. I'll probably add a few random games to the frontpage to make it more appealing.

## Testing app on fly.io (last update: 21.4)
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
- All the images have been generated with Stable Diffusion XL 1.0 https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
    - The prompts used to generate these images can be found on each games description