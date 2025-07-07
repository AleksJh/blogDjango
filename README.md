# BlogDjango

Blog application from Antonio Melé's book *Django 4 By Example*. This project is a full-featured blog web application built with Django 4.x, adhering to the MTV (Model-Template-View) architectural pattern. It uses Python as the backend language and supports PostgreSQL for robust data management, including advanced full-text search capabilities. Core functionalities include comprehensive data modeling for posts, an auto-generated Django Admin site, and both function-based and Class-Based Views for content display. The application features pagination, SEO-friendly canonical URLs, and a custom template system with unique tags and filters for Markdown rendering. A commenting system is integrated using Django Forms, alongside a flexible tagging functionality for posts. Crucially, it implements full-text search powered by PostgreSQL, leveraging SearchVector, SearchRank, and TrigramSimilarity for advanced query processing and relevance scoring. Additional features like email recommendations, Sitemaps, and RSS/Atom Feeds enhance the user experience. 

## Requirements

- Python 3.10.6
- Poetry 2.1.3
- Django 4.1.0

## Setup

```bash
poetry install
poetry run python manage.py runserver
```

## Notes

This requires an old version of Python. You can use "pyenv" for Linux, or "pyenv-win" for Windows
to handle different versions of interpreter.
DB file is added to the repository in presentation purposes.
