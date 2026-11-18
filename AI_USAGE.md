# AI Usage Documentation

## Tools Used
- Google Gemini for boilerplate Flask CRUD routes, debugging, and the Job Match algorithm

## Key Prompts
1. "Write Flask CRUD routes and parameterized MySQL queries for the companies and jobs tables."
2. "Debug why the Bootstrap Add/Edit modal is not opening when clicking Edit."
3. "Help integrate my existing CSS theme into Flask Jinja2 templates with consistent Add/Edit modals."
4. "Create a Python function to calculate skill match percentage and list missing required skills."

## What Worked Well
- AI-generated the repetitive CRUD routes and SQL queries quickly
- Helpful at pinpointing why inline modal scripts ran before Bootstrap loaded in `base.html`
- Made it easy to adapt my existing UI styling from a previous project into Jinja2 templates
- Provided a clean skill-matching function for the Job Match page

## What I Modified
- Changed column and variable names to match my actual `schema.sql` (`posting_url`, `job_description`, `first_name`, `last_name`, `response_date`)
- Added `try/except` error handling on delete routes to prevent foreign-key crashes
- Cleaned up `schema.sql` so the database imports cleanly on another machine
- Customized my existing CSS theme and modal layouts to fit all four tables

## Lessons Learned
- Always test AI code and cross-check it against your actual database schema
- AI is great for boilerplate routes, debugging, and adapting existing UI styles, but needs customization
- Asking for explanations helped me understand script execution order and JSON handling in Flask