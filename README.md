# **AutoClipSocial** – AI-Powered Short Video Automation Platform

**AutoClipSocial** is an automated pipeline for creating and publishing short-form videos across social media platforms using AI. It can fetch short videos from YouTube, generate AI-written captions and voice-overs for those videos, and automatically post the finished videos to platforms like Instagram and YouTube – all without manual intervention. This project leverages modern AI and web automation to streamline social media content creation.

## **Overview and Features**

- **Automated Video Retrieval:** The system uses a scraping module (powered by **yt-dlp**) to download source videos from YouTube. It can target specific videos or channels and automatically fetch trending or relevant short videos.
- **AI-Generated Content:** An AI module (integrated with the **OpenAI API**) creates textual content for each video, such as summaries or commentary. These captions are tailored to the video’s content and can be in multiple languages (configurable per user/platform).
- **Text-to-Speech Voiceover:** The generated captions are converted to speech using OpenAI’s GPT-4 mini TTS model. This produces a natural voiceover (using a selected built-in voice like _“echo”_) which is then combined with the video. The original video audio can be removed and replaced with the AI narration, and background music can be added underneath the voice track for enhanced engagement.
- **Video Composition:** Using **FFmpeg** and Python libraries like **MoviePy** and **Pydub**, the system merges the AI-generated audio with the video file. It also supports adding watermarks or subtitles if needed. (FFmpeg is installed in the Docker container for this purpose.)
- **Automated Posting:** Completed videos are uploaded automatically to social platforms. For Instagram, the project uses a **Playwright** (headless Chromium) automation bot to simulate user actions for uploading posts. This includes clicking the “New Post” button, filling in captions, and submitting the post on the user’s behalf. Similar automation or API integration can be configured for YouTube uploads as well.
- **Scheduling and Queueing:** A task scheduling system is in place (using **Celery** workers and a message broker) to queue and execute the video processing and posting tasks in the background. Users can configure how many posts per day to publish and set priorities for tasks. The architecture supports scheduling posts ahead of time and managing multiple tasks concurrently.
- **Multi-Platform Support:** The design is modular – new “platform” modules can be added. Currently, modules exist for Instagram (direct posting via bot) and YouTube (content sourcing). The project includes a framework for managing multiple social accounts (Instagram pages, YouTube channels, etc.) with settings like target language and posting frequency for each.
- **Web Dashboard (Front-end):** A front-end web interface (built with **TypeScript**, **JavaScript**, and **CSS**) allows users to monitor and control the pipeline. Through this dashboard, users can add content “prompts” (templates for the AI to follow when writing captions), view the list of fetched videos (referred to as “products” or content items), and see posting status or logs. The front-end communicates with the backend via RESTful API endpoints (provided by the FastAPI server).
- **Admin & Analytics:** Although still in progress, the project structure includes models for tracking post performance (views, likes) and logs of actions. Future versions will likely present analytics on how each AI-generated post performs across platforms.

## **Tech Stack**

**Backend (Python):** Built with **FastAPI** (for the REST API) and **Celery** (for task queue management). It follows a modular architecture: for example, the modules/content package handles video content processing, modules/ai handles AI prompt generation, and modules/platform contains platform-specific automation (Instagram bot, etc.). Key libraries and frameworks include:

- **FastAPI** – High-performance Python web framework for building the API backend. It enables easy creation of asynchronous endpoints and integrates with Pydantic for data validation.
- **SQLAlchemy & Alembic** – Database ORM (with async support) and migrations. The project uses a SQL database (e.g. PostgreSQL) to store users, content metadata, prompts, platform accounts, etc. Models and CRUD operations are defined for products, posts, user accounts, and more.
- **Celery** – Background job processing for long-running tasks (video download, AI generation, uploading). A Celery worker process executes tasks from a message broker queue (such as Redis or RabbitMQ), enabling asynchronous and scheduled job execution.
- **Playwright (Chromium)** – Used for web automation in the Instagram bot. Playwright runs a headless Chrome browser in the container (installed via playwright install chromium during build) to mimic user actions on the Instagram web interface for uploading posts.
- **AI and NLP** – Integration with OpenAI’s API for both text generation and text-to-speech. The OpenAI API key and model are configurable. By default, the project might use models like GPT-4 for text and _gpt-4o-mini-tts_ for voice. (The openai Python client is utilized to call these endpoints.)
- **MoviePy & Pydub** – These libraries handle video and audio editing in Python. MoviePy’s VideoFileClip is used for reading and manipulating video files, and Pydub’s AudioSegment for audio processing (concatenating speech clips and inserting pauses). FFmpeg, installed in the Docker image, powers the encoding/decoding under the hood.
- **Mako Templating** – Used in the project for rendering dynamic content (possibly for HTML templates or for templating prompts). Mako provides a Python templating engine to generate text output, which could be used for creating prompt strings for AI or generating parts of the web interface.

**Frontend (TypeScript & JS):** A single-page application (SPA) or web dashboard built with modern JavaScript (with TypeScript). It likely uses a framework such as **React** or **Vue** (with a TypeScript setup) to provide a responsive UI. The front-end communicates with the FastAPI backend via REST endpoints to display data (like video lists, task statuses) and send user actions (like adding a new YouTube URL to process or creating a new AI prompt template). Styling is managed with CSS (and possibly a UI framework or preprocessor).

**Containerization:** The project is fully containerized with **Docker**. The repository includes a Dockerfile for the backend and a docker-compose.yml for orchestrating multiple services. Docker Compose sets up the required services, which likely include: the FastAPI backend, the frontend (perhaps served as a static site or via a Node server), a PostgreSQL database, and a Redis broker for Celery. Environment variables are used to configure these containers at runtime.

## **Installation and Setup**

**Prerequisites:** Ensure you have **Docker** and **Docker Compose** installed on your system. Also, obtain required API keys and credentials (OpenAI API key, etc.) before starting.

1. **Clone the Repository:**  

- git clone <https://github.com/jalalsadeghi/social-platform.git>  
    cd social-platform

1. **Configure Environment Variables:** Create a .env file in the project root (or export environment variables) with the necessary configuration. Below are the key variables to define:
2. **DATABASE_URL** – Connection string for the database (e.g., a PostgreSQL URI). Example:  

- DATABASE_URL=postgresql://postgres:postgres@db:5432/socialdb

1. **JWT_SECRET_KEY** – Secret key for JWT token generation (for authenticating requests to the API).
2. **OPENAI_API_KEY** – Your OpenAI API key for content generation and TTS. (Required for the AI features to work.)
3. **OPENAI_MODEL** – _\[Optional\]_ Model name for text generation (e.g. "gpt-4" or "gpt-3.5-turbo"). The code defaults can be used if not set.
4. **CELERY_BROKER_URL** – URL for the Celery message broker. For example, if using Redis in Docker: redis://redis:6379/0.
5. **CELERY_RESULT_BACKEND** – Backend for storing task results (could be the same Redis instance or a database URL).
6. **INSTAGRAM_CLIENT_ID** – _\[Optional\]_ Instagram API client ID (if using official Instagram Graph API for some features). Not required for the default web automation mode.
7. **INSTAGRAM_USERNAME** / **INSTAGRAM_PASSWORD** – _\[Optional\]_ Credentials for the Instagram account that will post videos, if you plan to login via the bot. (In the current implementation, a logged-in session cookie is used instead, so this may not be needed unless you modify the login flow.)
8. **OTHER SETTINGS:** There are additional settings for token expiration, external API keys (if any), etc. Review backend/src/core/config.py for all available configurations.
9. **Docker Compose Up:** Once the environment variables are set, start the application using Docker Compose:

- docker-compose up --build
- This will build the Docker images and start all services (backend, frontend, database, broker). The FastAPI backend should start on an exposed port (e.g., <http://localhost:8000>) and the front-end on its dev server (e.g., <http://localhost:3000>), unless configured otherwise in the compose file.

1. **Playwright Setup:** The first time the backend container runs, it will install the necessary browser for Playwright (Chromium). The Dockerfile already handles installing Chromium with all dependencies. No additional action is required, but if running locally outside Docker, you’d need to install Playwright and run playwright install.
2. **Access the Dashboard:** Open the front-end URL in your browser (if it’s a React/Vue app, <http://localhost:3000> by default) to access the AutoClipSocial dashboard. You may need to register or log in, depending on the auth setup. Once logged in, you can start adding content sources and watch the automation in action.

## **Usage**

Once running, the typical workflow is: 1. **Add a Content Source:** Through the UI or an API call, provide a link or query for YouTube videos to scrape. The system will download the video file automatically using the scraper module. 2. **AI Content Generation:** When a video is downloaded, a Celery task is triggered to generate the caption script for the video. It uses the saved AI prompt templates (which you can customize via the UI) and the OpenAI API to produce a textual narrative or description for the video. 3. **Audio & Video Synthesis:** Another task takes the AI script and calls the TTS service to generate voice clips. It then merges those clips with appropriate pauses and background music (if configured) and overlays the resulting audio onto the video. The final output video is stored (the path or URL is saved in the system’s “Media” model). 4. **Auto Publishing:** Based on the schedule and platform settings, the system will log in to the social platform and upload the video. For Instagram, the Playwright bot navigates the web UI to upload the video file, paste the AI-generated caption, and share the post. For YouTube, an upload could be done via the YouTube Data API or a similar automated process. 5. **Monitoring:** You can monitor the status of each task (e.g., “Downloading”, “Processing”, “Posted”) on the dashboard. Logs and any errors (for example, if the Instagram upload fails due to a popup or timeout) are recorded – screenshots on failure are saved for debugging.

_Currently, the project is in an alpha stage._ Basic functionality (video download, AI narration, and Instagram posting) has been implemented and demonstrated, but some features may not be fully stable or complete. For instance, multi-platform support beyond Instagram/YouTube is in progress, and the web dashboard is under active development. Expect that you may need to tweak configurations or code for your specific use case.

## **Development Status**

🚧 **Under Active Development:** This project is not yet fully functional and is actively being developed. Recent commits show ongoing improvements (e.g., refining the task scheduling, adding multi-language support, and fixing upload issues). The current focus is on ensuring reliability of the end-to-end pipeline – from content scraping to posting.

Planned enhancements and TODOs include: refining the scheduling system (e.g., a calendar view of upcoming posts), improving error handling and retries for the social media bots, implementing the official APIs for platforms where feasible, and providing a richer analytics dashboard for posted content. (Some of these items are noted in the repository’s TODO file and commit history.)

Users and contributors are welcome to try out AutoClipSocial and provide feedback. Please note that running automation bots on platforms like Instagram may violate their terms of service – use responsibly and consider using official APIs where possible.

## **Getting Started for Contributors**

If you’d like to contribute or run the project for development: - Ensure you have Python 3.10+ and Node.js (if building the frontend) installed locally. - Install the backend requirements with pip install -r requirements.txt. This includes FastAPI, Celery, SQLAlchemy, Playwright, etc. (Don’t forget to run playwright install after installing to set up browsers.) - For the frontend, install dependencies (likely with npm install or yarn) and start the dev server (npm start or equivalent). - You can run the FastAPI app with Uvicorn for local development and test the API endpoints (e.g., using Swagger UI at <http://localhost:8000/docs> which FastAPI provides by default). - Run the Celery worker with the command (adjusted to your broker):  

celery -A src.core.celery_app worker --loglevel=info

This will start a Celery worker listening for tasks. You might also need to run a Celery beat service if scheduled tasks are used. - Ensure a local Postgres (or SQLite for testing) is running and DATABASE_URL is set accordingly. Use Alembic migrations to create tables (alembic upgrade head).

Please refer to the project’s documentation and comments for further guidance on the code structure.

