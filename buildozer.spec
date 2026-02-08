[app]
title = PC Asistan
package.name = pcasistan
package.domain = org.pcasistan
source.dir = .
version = 0.1
requirements = python3,kivy,pyjnius,android
permissions = RECORD_AUDIO,INTERNET,MODIFY_AUDIO_SETTINGS
orientation = portrait
fullscreen = 1

[app:android]
accept_sdk_license = True
android.api = 31
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
