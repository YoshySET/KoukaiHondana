from bleach import clean

def sanitize_html(text, allowed_tags=None, allowed_attributes=None):
    """
    HTMLテキストを安全にサニタイズする関数
    
    Args:
        text: サニタイズするHTMLテキスト
        allowed_tags: 許可するHTMLタグのリスト（デフォルトは基本的な書式タグのみ）
        allowed_attributes: 許可する属性のディクショナリ（デフォルトは空）
    
    Returns:
        サニタイズされたHTMLテキスト
    """
    if text is None:
        return ""
    
    if allowed_tags is None:
        allowed_tags = ['br', 'p', 'wbr', 'b', 'i', 'strong', 'em']
    
    if allowed_attributes is None:
        allowed_attributes = {}
    
    return clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    ) 