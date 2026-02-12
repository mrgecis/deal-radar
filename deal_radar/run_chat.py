#!/usr/bin/env python3
"""
Einfacher Wrapper um den Chat mit .env zu starten
"""
import os
import sys

# Laden der OpenAI API Key aus .env
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
                os.environ['OPENAI_API_KEY'] = api_key
                break

# Jetzt das Chat-Skript starten
os.chdir(os.path.dirname(__file__))
import subprocess
result = subprocess.run([sys.executable, 'src/08_chat.py'], cwd=os.path.dirname(__file__))
sys.exit(result.returncode)
