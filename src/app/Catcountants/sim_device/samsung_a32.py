"""Simulate Samsung A32"""

from os import environ

density = 2.265
dpi = 411
width, height = 412, 915
scale = .57
environ['KIVY_METRICS_FONTSCALE'] = '1'
environ['KIVY_METRICS_DENSITY'] = str(density * scale)
environ['KIVY_DPI'] = str(dpi * scale)

from kivy.core.window import Window
from kivy.metrics import dp

Window.size = (dp(width * scale), dp(height * scale))