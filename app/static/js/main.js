// jQueryを使用したフラッシュメッセージの自動非表示
$(document).ready(function() {
  $('.flash-message').each(function() {
    const $message = $(this);
    setTimeout(function() {
      $message.animate({
        opacity: 0
      }, 500, function() {
        $message.hide();
      });
    }, 5000);
  });
  
  // 本棚の表示アニメーション
  $('.book-card').each(function(index) {
    const $card = $(this);
    setTimeout(function() {
      $card.css({
        'opacity': 1,
        'transform': 'translateY(0)'
      });
    }, 100 * index);
  });
  
  // カテゴリフィルターの変更イベント
  $('#category-select').on('change', function() {
    const category = $(this).val();
    const username = $(this).data('username');
    window.location.href = `/users/${username}/bookshelf?category=${category}`;
  });
  
  // 評価の星表示
  $('.rating-select select').on('change', function() {
    const rating = $(this).val();
    const stars = '★'.repeat(rating);
    $(this).siblings('.rating-stars').text(stars);
  });
  
  // 検索フォームの送信前にトリム
  $('.search-form').on('submit', function() {
    const query = $(this).find('input[name="query"]');
    query.val($.trim(query.val()));
  });
  
  // モバイルメニューのトグル
  $('.mobile-menu-toggle').on('click', function() {
    $('.navbar-nav').slideToggle();
  });
}); 