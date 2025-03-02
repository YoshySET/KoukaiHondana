// jQueryを使用したフラッシュメッセージの自動非表示
$(document).ready(function() {
  // フラッシュメッセージの自動非表示
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
  
  // 検索フォームの送信前にトリム
  $('.search-form').on('submit', function() {
    const query = $(this).find('input[name="query"]');
    query.val($.trim(query.val()));
  });
  
  // モバイルメニューのトグル
  $('.mobile-menu-toggle').on('click', function() {
    $('.navbar-nav').slideToggle();
  });
  
  // 本の削除確認
  $('.book-delete-form').on('submit', function(e) {
    e.preventDefault();
    const $form = $(this);
    const bookTitle = $form.data('book-title');
    
    // ポップアップメッセージを設定
    $('#popupMessage').text(`「${bookTitle}」を本棚から削除してもよろしいですか？`);
    
    // ポップアップを表示
    $('#confirmPopup').addClass('active');
    
    // 確認ボタンのイベントハンドラ
    $('#popupConfirm').off('click').on('click', function() {
      // ポップアップを閉じる
      $('#confirmPopup').removeClass('active');
      // フォームを送信
      $form[0].submit();
    });
    
    // キャンセルボタンのイベントハンドラ
    $('#popupCancel').off('click').on('click', function() {
      // ポップアップを閉じるだけ
      $('#confirmPopup').removeClass('active');
    });
  });
  
  // ポップアップの外側をクリックしても閉じる
  $('#confirmPopup').on('click', function(e) {
    if (e.target === this) {
      $(this).removeClass('active');
    }
  });
}); 