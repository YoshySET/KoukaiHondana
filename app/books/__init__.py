from flask import Blueprint

bp = Blueprint('books', __name__, url_prefix='/books')

from app.books import routes 