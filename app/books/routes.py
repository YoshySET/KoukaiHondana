from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.books import bp
from app.books.forms import SearchBookForm, AddBookReviewForm
from app.models import Book, user_books
from app.utils.google_books import search_books, get_book_by_id
from sqlalchemy import and_

@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchBookForm()
    results = []
    
    if form.validate_on_submit() or request.args.get('query'):
        query = form.query.data or request.args.get('query')
        results = search_books(query)
        
    return render_template('books/search.html', title='書籍検索', form=form, results=results)

@bp.route('/add/<google_id>', methods=['GET', 'POST'])
@login_required
def add_book(google_id):
    # Google Books APIから書籍情報を取得
    book_data = get_book_by_id(google_id)
    
    if not book_data:
        flash('書籍情報が見つかりませんでした。')
        return redirect(url_for('books.search'))
    
    # データベースに既に存在するか確認
    book = Book.query.filter_by(google_id=google_id).first()
    
    # 存在しない場合は新規作成
    if not book:
        book = Book(
            google_id=google_id,
            title=book_data.get('title', '不明'),
            authors=', '.join(book_data.get('authors', ['不明'])),
            publisher=book_data.get('publisher', ''),
            published_date=book_data.get('publishedDate', ''),
            description=book_data.get('description', ''),
            isbn=book_data.get('industryIdentifiers', [{}])[0].get('identifier', ''),
            page_count=book_data.get('pageCount', 0),
            categories=', '.join(book_data.get('categories', [])),
            thumbnail=book_data.get('imageLinks', {}).get('thumbnail', ''),
            language=book_data.get('language', '')
        )
        db.session.add(book)
        db.session.commit()
    
    # ユーザーの本棚に追加
    if book not in current_user.books:
        current_user.books.append(book)
        db.session.commit()
        flash(f'「{book.title}」を本棚に追加しました！')
    else:
        flash(f'「{book.title}」は既に本棚に追加されています。')
    
    return redirect(url_for('users.bookshelf', username=current_user.username))

@bp.route('/review/<int:book_id>', methods=['GET', 'POST'])
@login_required
def review_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    # ユーザーと本の関連を取得
    user_book = db.session.query(user_books).filter(
        and_(user_books.c.user_id == current_user.id, user_books.c.book_id == book_id)
    ).first()
    
    form = AddBookReviewForm()
    
    if form.validate_on_submit():
        # 既存のレビューを更新
        stmt = user_books.update().where(
            and_(user_books.c.user_id == current_user.id, user_books.c.book_id == book_id)
        ).values(
            rating=int(form.rating.data) if form.rating.data else None,
            review=form.review.data,
            is_public=(form.is_public.data == 'public')
        )
        db.session.execute(stmt)
        db.session.commit()
        flash('レビューを保存しました！')
        return redirect(url_for('users.bookshelf', username=current_user.username))
    
    # フォームに現在の値を設定
    if user_book and not form.is_submitted():
        form.rating.data = str(user_book.rating) if user_book.rating else None
        form.review.data = user_book.review
        form.is_public.data = 'public' if user_book.is_public else 'private'
    
    return render_template('books/review.html', title='レビュー', form=form, book=book)

@bp.route('/remove/<int:book_id>', methods=['POST'])
@login_required
def remove_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if book in current_user.books:
        current_user.books.remove(book)
        db.session.commit()
        flash(f'「{book.title}」を本棚から削除しました。')
    
    return redirect(url_for('users.bookshelf', username=current_user.username))

@bp.route('/detail/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('books/detail.html', title=book.title, book=book) 