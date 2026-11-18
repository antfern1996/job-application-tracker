# Job Application Tracker

A web application to help track job applications during the job search process.

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Project Structure](#project-structure)
- [Install](#install)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
- [Usage](#usage)
  - [Example](#example)
  - [Notes](#notes)
- [Contributing](#contributing)
- [License](#license)

## Features

- Track companies and job listings
- Record application submissions
- Manage interview schedules
- Store contact information
- View dashboard statistics and recent application activity
- Rank jobs by skill match percentage and identify missing skills

## Technologies

- MySQL Database
- Python with Flask
- HTML/CSS for the web interface

## Project Structure

```text
job_tracker/
├── app.py              # Main Flask application
├── database.py         # Database connection functions
├── templates/          # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── companies.html
│   ├── jobs.html
│   ├── applications.html
│   ├── contacts.html
│   └── job_match.html
├── static/             # CSS
│   └── style.css
├── schema.sql          # Database creation script
├── AI_USAGE.md         # GenAI documentation
├── README.md           # Project description
└── requirements.txt    # Python dependencies
```

## Install

### Prerequisites

This project requires:
- [Git](https://git-scm.com/)
- [Python 3](https://www.python.org/)
- [MySQL](https://www.mysql.com/)

### Installation Steps

1. Clone this repository:
   ```sh
   git clone https://github.com/antfern1996/job-application-tracker.git
   ```

2. Navigate to the project directory:
   ```sh
   cd job-application-tracker
   ```

3. Create and activate a virtual environment:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate        # macOS/Linux
   # .venv\Scripts\activate         # Windows
   ```

4. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

5. Import the database schema and sample data:
   ```sh
   mysql -u root -p < schema.sql
   ```

6. Run the application:
   ```sh
   python3 app.py
   ```
   The application will be available at `http://127.0.0.1:5000`

## Usage

Once running, open `http://127.0.0.1:5000` in your browser and use the navigation bar to switch between **Dashboard**, **Companies**, **Jobs**, **Applications**, **Contacts**, and **Job Match**.

### Example

- Add a company on the **Companies** page, then create a job listing under **Jobs** with comma-separated required skills.
- Log a submission under **Applications** and record interview details as your process progresses.
- Enter your skills on the **Job Match** page (e.g., `Python, SQL, Git`) to view jobs ranked by match percentage.

### Notes

- `schema.sql` creates the `job_tracker` database automatically (`CREATE DATABASE IF NOT EXISTS job_tracker;`) and loads sample records.
- See `AI_USAGE.md` for documentation on GenAI assistance used during development.

## Contributing

This is a personal course project and is **not open to external contributions**.

Issues may be submitted for reference, but pull requests will not be accepted.

## License

All Rights Reserved © Anthony Fernandez

This code is provided solely for **personal demonstration and portfolio purposes**.