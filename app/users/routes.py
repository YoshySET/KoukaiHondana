from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.users import bp
from app.users.forms import EditProfileForm
from app.models import User, Book, user_books
from sqlalchemy import and_

@bp.route('/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # ユーザーの本棚から追加日時が新しい順に最大5冊を取得
    recent_books = db.session.query(Book, user_books.c.updated_at)\
        .join(user_books, Book.id == user_books.c.book_id)\
        .filter(user_books.c.user_id == user.id)\
        .order_by(user_books.c.updated_at.desc())\
        .limit(5)\
        .all()
    
    # 結果からBookオブジェクトのみを抽出
    recent_books = [book for book, _ in recent_books]
    
    return render_template('users/profile.html', user=user, recent_books=recent_books)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        current_user.privacy_setting = form.privacy_setting.data
        db.session.commit()
        flash('プロフィールを更新しました！')
        return redirect(url_for('users.profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
        form.privacy_setting.data = current_user.privacy_setting
    return render_template('users/edit_profile.html', title='プロフィール編集', form=form)

@bp.route('/<username>/bookshelf')
def bookshelf(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # ユーザーの本と評価情報を取得
    books_with_ratings = db.session.query(
        Book, user_books.c.rating
    ).join(
        user_books, Book.id == user_books.c.book_id
    ).filter(
        user_books.c.user_id == user.id
    ).all()
    
    # 本と評価を分離
    books = []
    ratings = {}
    for book, rating in books_with_ratings:
        books.append(book)
        if rating:  # 評価がある場合のみ追加
            ratings[book.id] = rating
    
    return render_template('users/bookshelf.html', user=user, books=books, ratings=ratings)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash('自分自身をフォローすることはできません！')
        return redirect(url_for('users.profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'{username}さんをフォローしました！')
    return redirect(url_for('users.profile', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash('自分自身のフォローを解除することはできません！')
        return redirect(url_for('users.profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'{username}さんのフォローを解除しました。')
    return redirect(url_for('users.profile', username=username))

@bp.route('/discover')
@login_required
def discover():
    # 同じ本を持っているユーザーを見つける
    similar_users = User.query.join(
        user_books, User.id == user_books.c.user_id
    ).filter(
        user_books.c.book_id.in_([book.id for book in current_user.books]),
        User.id != current_user.id
    ).distinct().all()
    
    # おすすめの本を見つける（同じ本を持つユーザーの本棚から）
    recommended_books = []
    for user in similar_users:
        for book in user.books:
            if book not in current_user.books and book not in recommended_books:
                recommended_books.append(book)
                if len(recommended_books) >= 10:  # 最大10冊まで
                    break
    
    return render_template('users/discover.html', similar_users=similar_users, 
                          recommended_books=recommended_books)

@bp.route('/<username>/following')
def following(username):
    user = User.query.filter_by(username=username).first_or_404()
    followed_users = user.followed.all()
    return render_template('users/user_list.html', 
                          title=f'{user.username}のフォロー', 
                          user=user,
                          users=followed_users,
                          list_type='following')

@bp.route('/<username>/followers')
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    followers = user.followers.all()
    return render_template('users/user_list.html', 
                          title=f'{user.username}のフォロワー', 
                          user=user,
                          users=followers,
                          list_type='followers') 