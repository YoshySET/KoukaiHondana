from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.books import bp
from app.books.forms import SearchBookForm, AddBookReviewForm
from app.models import Book, User, user_books as user_books_table
from app.utils.google_books import search_books, get_book_by_id
from sqlalchemy import and_
from datetime import datetime
from app.utils.sanitize import sanitize_html

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
    
    # Ajaxリクエストの場合はJSONを返す
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': f'「{book.title}」を本棚に追加しました！',
            'book_id': book.id
        })
    
    # 検索ページに戻る（クエリパラメータを保持）
    query = request.args.get('query', '')
    if query:
        return redirect(url_for('books.search', query=query))
    else:
        return redirect(url_for('books.search'))

@bp.route('/review/<int:book_id>', methods=['GET', 'POST'])
@login_required
def review_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    # ユーザーと本の関連を取得
    user_book = db.session.query(user_books_table).filter(
        and_(user_books_table.c.user_id == current_user.id, user_books_table.c.book_id == book_id)
    ).first()
    
    form = AddBookReviewForm()
    
    if form.validate_on_submit():
        # 既存のレビューを更新
        stmt = user_books_table.update().where(
            and_(user_books_table.c.user_id == current_user.id, user_books_table.c.book_id == book_id)
        ).values(
            rating=int(form.rating.data) if form.rating.data else None,
            review=form.review.data,
            is_public=(form.is_public.data == 'public'),
            updated_at=datetime.utcnow()
        )
        db.session.execute(stmt)
        db.session.commit()
        flash('レビューを保存しました！')
        return redirect(url_for('books.book_detail', book_id=book_id))
    
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
    
    # 概要をサニタイズ
    if book.description:
        book.sanitized_description = sanitize_html(book.description)
    else:
        book.sanitized_description = None
    
    # 公開されているレビューを取得（最新3件）
    reviews_query = db.session.query(
        User.username,
        User.id.label('user_id'),
        user_books_table.c.rating,
        user_books_table.c.review,
        user_books_table.c.updated_at
    ).join(
        user_books_table, User.id == user_books_table.c.user_id
    ).filter(
        user_books_table.c.book_id == book_id,
        user_books_table.c.is_public == True,
        user_books_table.c.review != None,
        user_books_table.c.review != ''
    ).order_by(
        user_books_table.c.updated_at.desc()
    ).limit(3)
    
    reviews = reviews_query.all()
    
    # 現在のユーザーのレビュー
    user_review = None
    if current_user.is_authenticated:
        user_review = db.session.query(user_books_table).filter(
            and_(user_books_table.c.user_id == current_user.id, user_books_table.c.book_id == book_id)
        ).first()
    
    # この本を持っているユーザーのリストから自分自身を除外
    other_users = []
    if current_user.is_authenticated:
        other_users = [user for user in book.users if user.id != current_user.id]
    else:
        other_users = book.users.all()
    
    return render_template('books/detail.html', title=book.title, book=book, reviews=reviews, user_review=user_review, other_users=other_users)

@bp.route('/user_books')
@login_required
def get_user_books():
    # ユーザーの本棚にある本のGoogle IDのリストを返す
    google_ids = [book.google_id for book in current_user.books]
    return jsonify({'books': google_ids})

@bp.route('/detail/<int:book_id>/reviews')
def book_reviews(book_id):
    book = Book.query.get_or_404(book_id)
    page = request.args.get('page', 1, type=int)
    
    # 公開されているレビューを取得（ページネーション付き）
    reviews_query = db.session.query(
        User.username,
        User.id.label('user_id'),
        user_books_table.c.rating,
        user_books_table.c.review,
        user_books_table.c.updated_at
    ).join(
        user_books_table, User.id == user_books_table.c.user_id
    ).filter(
        user_books_table.c.book_id == book_id,
        user_books_table.c.is_public == True,
        user_books_table.c.review != None,
        user_books_table.c.review != ''
    ).order_by(
        user_books_table.c.updated_at.desc()
    )
    
    # ページネーション（1ページあたり10件）
    total_reviews = reviews_query.count()
    reviews = reviews_query.limit(10).offset((page - 1) * 10).all()
    
    # 総ページ数を計算
    total_pages = (total_reviews + 9) // 10  # 切り上げ除算
    
    return render_template('books/reviews.html', 
                          title=f'{book.title}のレビュー', 
                          book=book, 
                          reviews=reviews, 
                          page=page,
                          total_pages=total_pages,
                          total_reviews=total_reviews)

# 検索結果から書籍詳細を表示するためのルート
@bp.route('/view/<google_id>')
@login_required
def view_book(google_id):
    # データベースに既に存在するか確認
    book = Book.query.filter_by(google_id=google_id).first()
    
    # 存在しない場合は一時的に作成（保存はしない）
    if not book:
        book_data = get_book_by_id(google_id)
        if not book_data:
            flash('書籍情報が見つかりませんでした。')
            return redirect(url_for('books.search'))
            
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
    
    # 書籍詳細ページにリダイレクト
    return redirect(url_for('books.book_detail', book_id=book.id)) 