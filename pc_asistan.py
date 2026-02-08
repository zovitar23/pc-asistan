from __future__ import annotations
import os, webbrowser
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.utils import platform

ANDROID = platform == "android"

if ANDROID:
    from android import activity, permissions
    from jnius import autoclass

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Intent = autoclass("android.content.Intent")
    RecognizerIntent = autoclass("android.speech.RecognizerIntent")
    TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
    Locale = autoclass("java.util.Locale")


class PulseButton(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_r = 96
        self.pulse_r = self.base_r
        with self.canvas:
            Color(0.06, 0.06, 0.08, 1)
            self._bg = Rectangle(pos=self.pos, size=Window.size)
            Color(0.55, 0.20, 0.85, 0.9)
            self._core = Ellipse(pos=self._ring_pos(), size=self._ring_size())
        self.bind(pos=self._redraw, size=self._redraw)

    def _ring_pos(self):
        cx, cy = self.center
        r = self.pulse_r
        return (cx - r, cy - r)

    def _ring_size(self):
        r = self.pulse_r
        return (r * 2, r * 2)

    def _redraw(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._core.pos = self._ring_pos()
        self._core.size = self._ring_size()


class RyoseApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tts = None
        self._request_code = 1207

    def build(self):
        root = FloatLayout()
        self.label = Label(text="Dokun ve konuş", pos_hint={"center_x": 0.5, "center_y": 0.8})
        root.add_widget(self.label)

        self.pulse = PulseButton(size_hint=(1, 1))
        root.add_widget(self.pulse)

        root.bind(on_touch_down=self._on_touch)

        if ANDROID:
            self._bind_activity_result()
            permissions.request_permissions([permissions.Permission.RECORD_AUDIO])
            self._init_android_tts()

        return root

    def _on_touch(self, *_):
        if ANDROID:
            self.start_listening()

    def _bind_activity_result(self):
        activity.bind(on_activity_result=self._on_activity_result)

    def _on_activity_result(self, requestCode, resultCode, intent):
        if requestCode == self._request_code and resultCode == -1:
            results = intent.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            if results and len(results) > 0:
                text = results[0]
                self.handle_text(text)

    def _init_android_tts(self):
        def _init(dt):
            try:
                act = PythonActivity.mActivity
                self._tts = TextToSpeech(act, None)
                self._tts.setLanguage(Locale("tr", "TR"))
                self._tts.setPitch(0.9)
                self._tts.setSpeechRate(1.0)
            except Exception as e:
                print("TTS init error:", e)

        Clock.schedule_once(_init, 1.0)

    def start_listening(self):
        try:
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "tr-TR")
            PythonActivity.mActivity.startActivityForResult(intent, self._request_code)
        except Exception as e:
            print("Speech error:", e)

    def handle_text(self, text):
        t = text.lower()
        if "youtube" in t:
            self.speak("YouTube açılıyor")
            self._open_app("com.google.android.youtube", "YouTube")
        elif "instagram" in t:
            self.speak("Instagram açılıyor")
            self._open_app("com.instagram.android", "Instagram")
        else:
            self.speak("Komutu anlamadım")

    def speak(self, text):
        self.label.text = text
        if ANDROID and self._tts:
            self._tts.speak(text, TextToSpeech.QUEUE_FLUSH, None)

    def _open_app(self, pkg, name):
        try:
            pm = PythonActivity.mActivity.getPackageManager()
            intent = pm.getLaunchIntentForPackage(pkg)
            if intent:
                PythonActivity.mActivity.startActivity(intent)
            else:
                self.speak(f"{name} yüklü değil")
        except Exception as e:
            print(e)
            self.speak(f"{name} açılamadı")


if __name__ == "__main__":
    RyoseApp().run()
