"""
Main Flask Application

This file handles:
1. Flask app setup
2. MongoDB connection
3. Routes:
   - "/" (index): shows paginated list of books with filters (search + category)
   - "/book/<upc>": shows a detailed page for a single book
"""

from flask import Flask, render_template, request, abort
from flask_scss import Scss
from pymongo import MongoClient
import math

# --- Flask setup ---
app = Flask(__name__)

# Enable SCSS -> CSS auto compilation
Scss(app, static_dir='static', asset_dir='assets')

# --- MongoDB connection ---
password = "7zejV520X22r1HMx"
uri = f"mongodb+srv://test:{password}@book-scraper.i3nbzid.mongodb.net/?retryWrites=true&w=majority&appName=book-scraper"
client = MongoClient(uri)

# Select the database and collection
db = client["scrapy_data"]
collection = db["books"]


# --- Home Page Route ---
@app.route("/")
def index():
    """
    Displays a list of books with:
    - Pagination (20 per page)
    - Search by title
    - Filter by category
    """
    # --- Pagination setup ---
    page = int(request.args.get("page", 1))  # current page (default = 1)
    per_page = 20  # items per page

    # --- Filters from query parameters ---
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    # --- Build MongoDB query ---
    query = {}
    if search:
        # case-insensitive search in title
        query["title"] = {"$regex": search, "$options": "i"}
    if category:
        query["category"] = category

    # --- Fetch books from MongoDB ---
    total_books = collection.count_documents(query)  # total matching books
    books = (
        collection.find(query)
        .skip((page - 1) * per_page)  # skip previous pages
        .limit(per_page)              # limit to current page size
    )

    # --- Get unique categories for dropdown filter ---
    categories = collection.distinct("category")

    # --- Calculate total pages for pagination ---
    total_pages = math.ceil(total_books / per_page)

    # Render template with data
    return render_template(
        "index.html",
        books=books,
        categories=categories,
        search=search,
        category=category,
        page=page,
        total_pages=total_pages
    )


# --- Book Detail Page Route ---
@app.route("/book/<upc>")
def book_detail(upc):
    """
    Displays a single book detail page.
    Uses UPC (unique identifier) to fetch the book.
    """
    book = collection.find_one({"upc": upc})  # fetch by UPC
    if not book:
        abort(404, description="Book not found")  # show error if not found

    return render_template("book.html", book=book)


# --- Run the app ---
if __name__ == "__main__":
    app.run(debug=True)
