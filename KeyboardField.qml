import QtQuick
import qs.Ui as Ui

// Qt 6.12 probes the clipboard whenever an editable TextInput receives
// dataChanged, even without a paste. Keep the native input read-only for its
// entire lifetime; never toggle it for typing. Programmatic edits below do not
// access QClipboard. Native selection/navigation and validation are retained.
Ui.TextField {
  id: root
  signal keyboardEdited()
  readOnly: true
  selectByMouse: true
  cursorVisible: activeFocus

  function replaceSelection(value, backward, forward) {
    var before = text, position = cursorPosition
    var start = selectionStart, end = selectionEnd
    if (start === end) {
      start = Math.max(0, position - (backward || 0))
      end = Math.min(text.length, position + (forward || 0))
    }
    // Preserve surrogate pairs when deleting a character.
    if (start > 0 && /[\uDC00-\uDFFF]/.test(text[start])) start--
    if (end < text.length && /[\uDC00-\uDFFF]/.test(text[end])) end++
    var candidate = before.slice(0, start) + value + before.slice(end)
    if (candidate.length > maximumLength) return
    remove(start, end)
    insert(start, value)
    // Native insert/remove run the validator; restore a rejected replacement.
    if (text !== candidate) { text = before; cursorPosition = position; return }
    cursorPosition = start + value.length
    if (text !== before) keyboardEdited()
  }

  Keys.onPressed: event => {
    // Leave navigation, selection and editor shortcuts to Qt. The permanently
    // read-only native control also rejects paste(), middle-click and cut().
    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
      if (acceptableInput) { editingFinished(); accepted() }
      event.accepted = true
    } else if (!(event.modifiers & Qt.MetaModifier) &&
               (!(event.modifiers & (Qt.ControlModifier | Qt.AltModifier)) ||
                ((event.modifiers & Qt.ControlModifier) && (event.modifiers & Qt.AltModifier)))) {
      if (event.key === Qt.Key_Backspace) { replaceSelection("", 1, 0); event.accepted = true }
      else if (event.key === Qt.Key_Delete) { replaceSelection("", 0, 1); event.accepted = true }
      else if (event.text && !/[\u0000-\u001F\u007F]/.test(event.text)) { replaceSelection(event.text, 0, 0); event.accepted = true }
    }
  }
}
