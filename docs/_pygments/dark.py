from pygments.styles.vim import VimStyle
from pygments.token import Comment, Name, String


class CustomDarkStyle(VimStyle):
    background_color = "#0C0C0C"
    styles = VimStyle.styles
    styles[Comment] = "#0ADB0A"
    styles[Name.Decorator] = "#3399cc"
    styles[String] = "#F91F1F"
    styles[String.Doc] = "#0ADB0A"
