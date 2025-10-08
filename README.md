#  ReelMatch API

**ReelMatch** is a movie recommendation backend built with **Django REST Framework**.  
It integrates with **The Movie Database (TMDb) API** to fetch trending movies, search results, and personalized recommendations.  
Users can also manage their favorite movies and get real-time recommendations.

---

 Features

-  Fetch **trending movies** from TMDb  
-  Search for movies by title  
-  Get **movie recommendations** based on a selected movie  
-  Add or remove **favorite movies** for each user  
-  Secure authentication with JWT (JSON Web Tokens)  
-  Caching via **Redis** for performance  
-  Scheduled background jobs with **Celery + Redis**  
-  Auto-generated API documentation using **drf-spectacular** (Swagger / Redoc)  
-  PostgreSQL database hosted on Render  
-  Deployable instantly to **Render**

---

##  Tech Stack

| Component        | Technology Used                  |
|------------------|----------------------------------|
| Backend Framework | Django REST Framework (DRF)     |
| Database          | PostgreSQL                      |
| Cache / Queue     | Redis + Celery                  |
| API Docs          | drf-spectacular (Swagger UI)    |
| Deployment        | Render (Gunicorn + Docker)      |
| External API      | TMDb (The Movie Database)       |

---

##  Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/reelmatch.git
cd reelmatch
2. Create and Configure Environment Variables
Create a .env file in your project root:

bash
Copy code
# ============================
# Database (Postgres)
# ============================
POSTGRES_DB=reelmatch
POSTGRES_USER=reelmatch
POSTGRES_PASSWORD=reelmatchpass
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# ============================
# Redis
# ============================
REDIS_HOST=redis
REDIS_PORT=6379

# ============================
# Django
# ============================
DJANGO_SECRET_KEY=supersecretdevkey
DJANGO_DEBUG=True

# ============================
# External APIs
# ============================
TMDB_API_KEY=<your_tmdb_api_key>
3. Build and Run with Docker
bash
Copy code
docker-compose up --build
Once the containers are running, open the app in your browser:

bash
Copy code
http://localhost:8000/api/docs/
 Deployment on Render
Push your latest code to GitHub

bash
Copy code
git add .
git commit -m "Deploy ReelMatch API to Render"
git push origin main
Create a new Render Web Service

Connect your GitHub repo

Environment: Python 3

Start command:

bash
Copy code
gunicorn reelmatch_api.wsgi:application --bind 0.0.0.0:$PORT
Add environment variables:

DATABASE_URL → your Render PostgreSQL connection string

PORT=8000

TMDB_API_KEY, DJANGO_SECRET_KEY, etc.

Visit your live API

ruby
Copy code
https://reelmatch-api.onrender.com/api/docs/
 Running Tests
Run all tests locally using:

bash
Copy code
pytest
Or inside Docker:

bash
Copy code
docker-compose run web pytest
API Endpoints Overview
Endpoint	Method	Description
/movies/trending/	GET	Fetch trending movies
/movies/{movie_id}/recommendations/	GET	Get movie recommendations
/movies/search/?query=<title>	GET	Search movies by title
/api/favorites/	GET / POST	Manage favorite movies
/api/docs/	GET	Swagger UI documentation

 Developer Notes
The API documentation is available at /api/docs/ (Swagger UI) and /api/redoc/ (ReDoc).

Use JWT tokens for authentication:

Obtain a token via /api/token/

Refresh token via /api/token/refresh/

 Useful Commands
Command	Description
python manage.py migrate	Apply database migrations
python manage.py createsuperuser	Create an admin user
docker-compose up --build	Start the full stack
docker-compose logs -f web	View web service logs
python manage.py collectstatic --noinput	Collect static files for production

 License
This project is licensed under the MIT License.
Feel free to modify and use for your own educational or commercial projects.

 Author
Collinsthegreat
Backend Developer | Django REST | DevOps | API Design
 GitHub Profile
Reach out for collaborations or feedback!
