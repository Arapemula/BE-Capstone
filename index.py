import sys
import os

# Tambahkan root ke sys.path agar import 'src.xxx' bisa ditemukan Vercel
sys.path.insert(0, os.path.dirname(__file__))

from src.app import app
