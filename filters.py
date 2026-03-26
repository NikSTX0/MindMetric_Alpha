# This file must be next to app.py – add the enumerate filter
# It is imported automatically via app.py

def add_filters(app):
    app.jinja_env.filters['enumerate'] = enumerate
    app.jinja_env.filters['min'] = min
