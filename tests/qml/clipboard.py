"""Qt 6.12 regressions; run with PySide6 and QT_QPA_PLATFORM=offscreen.

The theme stub supplies the same Controls.TextField base as Omarchy's Ui field.
The actual product KeyboardField and SettingNumber are loaded without hardware.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import unittest
from pathlib import Path
from PySide6.QtCore import QMimeData, QUrl, Qt, qVersion, QCoreApplication, QEvent
from PySide6.QtGui import QGuiApplication, QKeyEvent
from PySide6.QtQuick import QQuickView
from PySide6.QtTest import QTest

ROOT = Path(__file__).resolve().parents[2]
APP = QGuiApplication.instance() or QGuiApplication([])

class OfferedText(QMimeData):
    def __init__(self):
        super().__init__()
        self.probes = 0
    def formats(self):
        self.probes += 1
        return ['text/plain']
    def retrieveData(self, mime, preferred):
        self.probes += 1
        return 'offered clipboard text'

class ClipboardTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)
        ui = self.path / 'qs/Ui'
        ui.mkdir(parents=True)
        (ui / 'qmldir').write_text('module qs.Ui\nTextField 1.0 TextField.qml\n')
        (ui / 'TextField.qml').write_text('import QtQuick\nimport QtQuick.Controls\nTextField { property color accent: "blue"; property color foreground: "black" }')
        for name in ['KeyboardField.qml', 'SettingNumber.qml']:
            (self.path / name).write_bytes((ROOT / name).read_bytes())
        for n in range(1, 3):
            (self.path / f"Harness{n}.qml").touch()
        self.view = QQuickView()
        self.addCleanup(self.cleanup_view)
        self.sequence = 0
        self.view.engine().addImportPath(str(self.path))

    def cleanup_view(self):
        APP.clipboard().clear()
        self.view.close()
        self.view.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)

    def load(self, source):
        self.sequence += 1
        name = f"Harness{self.sequence}.qml"
        (self.path / name).write_text(source)
        self.view.setSource(QUrl.fromLocalFile(str(self.path / name)))
        self.assertEqual(self.view.status(), QQuickView.Ready, self.view.errors())
        self.view.show()
        self.view.requestActivate()
        self.field = self.view.rootObject()
        self.field.forceActiveFocus()
        APP.processEvents()
        return self.field

    def type_text(self, text):
        for character in text:
            QTest.keyClick(self.view, character)

    def offer(self):
        data = OfferedText()
        APP.clipboard().setMimeData(data)
        APP.processEvents()
        return data

    def test_editable_control_probes_clipboard_but_product_never_does(self):
        self.load('import QtQuick\nimport QtQuick.Controls\nTextField { width: 300; height: 40 }')
        self.assertGreater(self.offer().probes, 0, 'positive control must exercise Qt clipboard probe')
        # Destroy the editable positive control before observing the safe field.
        self.view.setSource(QUrl())
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        existing = self.offer()
        self.load('import QtQuick\nKeyboardField { width: 300; height: 40; text: "safe" }')
        self.assertEqual(existing.probes, 0)
        for _ in range(10):
            data = self.offer()
            self.assertEqual(data.probes, 0)
            self.assertFalse(self.field.property('canPaste'))
            QTest.keyClick(self.view, Qt.Key_V, Qt.ControlModifier)
            QTest.keyClick(self.view, Qt.Key_Insert, Qt.ShiftModifier)
            QTest.mouseClick(self.view, Qt.MiddleButton)
            QTest.keyClick(self.view, Qt.Key_X, Qt.ControlModifier)
            self.field.cut()
            self.field.paste()
            APP.processEvents()
            self.assertEqual(data.probes, 0)
            self.assertEqual(self.field.property('text'), 'safe')
            self.assertTrue(self.field.property('readOnly'))

    def test_typing_selection_delete_and_accept(self):
        f = self.load('import QtQuick\nKeyboardField { width: 300; height: 40 }')
        edits, accepts = [], []
        f.keyboardEdited.connect(lambda: edits.append(f.property('text')))
        f.accepted.connect(lambda: accepts.append(True))
        self.type_text('abc')
        self.assertEqual(f.property('text'), 'abc')
        self.assertEqual(edits, ['a', 'ab', 'abc'])
        QTest.keyClick(self.view, Qt.Key_A, Qt.ControlModifier)
        self.type_text('xy')
        self.assertEqual(f.property('text'), 'xy')
        QTest.keyClick(self.view, Qt.Key_Left)
        QTest.keyClick(self.view, Qt.Key_Delete)
        QTest.keyClick(self.view, Qt.Key_Backspace)
        self.assertEqual(f.property('text'), '')
        QTest.keyClick(self.view, Qt.Key_Return)
        self.assertEqual(accepts, [True])
        self.assertTrue(f.property('readOnly'))

    def test_numeric_validation_and_commit(self):
        f = self.load('import QtQuick\nSettingNumber { width: 300; height: 40; savedValue: 50; minimum: 0; maximum: 100 }')
        commits = []
        f.committed.connect(lambda value, complete: commits.append(value))
        QTest.keyClick(self.view, Qt.Key_A, Qt.ControlModifier)
        self.type_text('75')
        self.assertEqual(f.property('text'), '75')
        self.assertTrue(f.property('acceptableInput'))
        QTest.keyClick(self.view, Qt.Key_Return)
        self.assertEqual(commits, [75])
        QTest.keyClick(self.view, Qt.Key_A, Qt.ControlModifier)
        self.type_text('101')
        self.assertFalse(f.property('acceptableInput'))
        QTest.keyClick(self.view, Qt.Key_Return)
        self.assertEqual(commits, [75])
        data = self.offer()
        self.assertEqual(data.probes, 0)

    def test_length_unicode_and_focus_commit(self):
        f = self.load('import QtQuick\nKeyboardField { width: 300; height: 40; maximumLength: 4 }')
        self.type_text('abcde')
        self.assertEqual(f.property('text'), 'abcd')
        f.setProperty('text', 'a😀b')
        f.setProperty('cursorPosition', 3)
        QTest.keyClick(self.view, Qt.Key_Backspace)
        self.assertEqual(f.property('text'), 'ab')
        f.setProperty('text', '')
        APP.sendEvent(self.view, QKeyEvent(QEvent.KeyPress, Qt.Key_E, Qt.ControlModifier | Qt.AltModifier, 'é'))
        self.assertEqual(f.property('text'), 'é')
        finished = []
        f.editingFinished.connect(lambda: finished.append(True))
        f.setProperty('focus', False)
        APP.processEvents()
        self.assertTrue(finished)

    def test_all_product_fields_use_safe_base(self):
        self.assertNotIn('Ui.TextField {', (ROOT / 'Editor.qml').read_text())
        self.assertNotIn('Ui.TextField {', (ROOT / 'SettingNumber.qml').read_text())

if __name__ == '__main__':
    print('Qt', qVersion())
    unittest.main()
