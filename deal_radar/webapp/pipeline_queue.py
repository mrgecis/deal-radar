#!/usr/bin/env python3
"""
Pipeline Queue Manager – Background task execution für Company-Addition.
Managed: CSV-Upload, Datenvalidierung, Pipeline-Triggering mit Status-Tracking.
"""

import os
import sys
import csv
import json
import threading
import subprocess
import time
from datetime import datetime
from pathlib import Path
from enum import Enum

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
COMPANIES_FILE = os.path.join(DATA_DIR, 'companies.csv')
SRC_DIR = os.path.join(BASE_DIR, 'src')
VENV_PYTHON = os.path.join(BASE_DIR, '..', '.venv', 'bin', 'python')

# Python fallback
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

# OpenAI für Firmenerkennung
try:
    from openai import OpenAI
    openai_client = OpenAI()
except:
    openai_client = None

# ── Pipeline Steps ────────────────────────────────────────────────────────────
PIPELINE_STEPS = [
    ('01_discover_ir', '01_discover_ir.py', 'Discovering IR URLs...'),
    ('02_pdf_links', '02_collect_pdf_links.py', 'Collecting PDF links...'),
    ('03_download', '03_download_pdfs.py', 'Downloading PDFs...'),
    ('04_extract', '04_extract_text.py', 'Extracting text...'),
    ('05_scan', '05_scan_reports.py', 'Scanning for signals...'),
    ('06_score', '06_score_and_export.py', 'Scoring reports...'),
    ('07_index', '07_build_index.py', 'Building search index...'),
]


class TaskStatus(Enum):
    """Status für Background-Tasks."""
    PENDING = "pending"
    VALIDATING = "validating"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """Einzelne Background-Task."""
    def __init__(self, task_type, data):
        self.id = f"{task_type}_{int(time.time()*1000)}"
        self.type = task_type  # 'add_company_csv' or 'add_company_manual'
        self.data = data  # CSV content or company dict
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self.current_step = None
        self.steps_completed = []
        self.error = None
        self.companies_added = []
        self.log = []

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'status': self.status.value,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'current_step': self.current_step,
            'steps_completed': self.steps_completed,
            'progress': len(self.steps_completed) / len(PIPELINE_STEPS),
            'error': self.error,
            'companies_added': self.companies_added,
            'log': self.log[-50:] if self.log else [],  # Letzter 50 logs
        }


class PipelineQueue:
    """Manager für Background-Tasks und Pipeline-Ausführung."""
    def __init__(self):
        self.tasks = {}  # task_id -> Task
        self.current_task = None
        self.lock = threading.Lock()
        self.worker_thread = None
        self._running = False
        self._start_worker()

    def _start_worker(self):
        """Starte Worker-Thread für Task-Verarbeitung."""
        if not self._running:
            self._running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()

    def _worker_loop(self):
        """Hauptschleife für Task-Verarbeitung."""
        while self._running:
            # Nächste pending Task suchen
            with self.lock:
                pending = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
                if pending:
                    self.current_task = pending[0]

            if self.current_task:
                self._execute_task(self.current_task)
                with self.lock:
                    self.current_task = None
            else:
                time.sleep(1)

    def _execute_task(self, task: Task):
        """Führe Task aus."""
        try:
            task.status = TaskStatus.VALIDATING
            task.started_at = datetime.now().isoformat()
            task.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting task...")

            # 1. Parse und validiere Daten
            if task.type == 'add_company_csv':
                companies = self._parse_csv(task.data)
            elif task.type == 'add_company_manual':
                companies = [task.data]
            else:
                raise ValueError(f"Unknown task type: {task.type}")

            if not companies:
                raise ValueError("No valid companies found")

            task.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Parsed {len(companies)} companies")

            # 2. Zu companies.csv hinzufügen
            self._add_to_companies_csv(companies)
            task.companies_added = [c['company_id'] for c in companies]
            task.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Added to companies.csv: {', '.join(task.companies_added)}")

            # 3. Pipeline durchlaufen
            task.status = TaskStatus.RUNNING
            for step_id, script, desc in PIPELINE_STEPS:
                task.current_step = step_id
                task.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {desc}")
                self._run_pipeline_step(script, step_id, task)
                task.steps_completed.append(step_id)

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            task.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Task completed successfully!")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now().isoformat()
            task.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {str(e)}")

    def _parse_csv(self, csv_content: str):
        """Parse CSV-Daten (Format: company_id;company_name;country;website;ir_url)."""
        companies = []
        lines = csv_content.strip().split('\n')
        
        # Skip header
        if lines and lines[0].startswith('company_id'):
            lines = lines[1:]

        for line in lines:
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(';')]
            if len(parts) < 5:
                raise ValueError(f"Invalid CSV line: {line}")

            company = {
                'company_id': parts[0],
                'company_name': parts[1],
                'country': parts[2],
                'website': parts[3],
                'ir_url': parts[4] if parts[4] else '',
            }
            
            # Validierung
            if not company['company_id'] or not company['company_name']:
                raise ValueError(f"Missing required fields in: {line}")
            
            companies.append(company)

        return companies

    def _add_to_companies_csv(self, companies):
        """Füge Unternehmen zu companies.csv hinzu."""
        # Existierende Firmen laden
        existing = {}
        if os.path.exists(COMPANIES_FILE):
            with open(COMPANIES_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                existing = {row['company_id']: row for row in reader}

        # Neue Firmen hinzufügen (Duplikate überspringen)
        for company in companies:
            existing[company['company_id']] = company

        # Speichern
        os.makedirs(os.path.dirname(COMPANIES_FILE), exist_ok=True)
        with open(COMPANIES_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['company_id', 'company_name', 'country', 'website', 'ir_url'], delimiter=';')
            writer.writeheader()
            writer.writerows(existing.values())

    def _run_pipeline_step(self, script: str, step_id: str, task: Task):
        """Führe Pipeline-Schritt aus."""
        script_path = os.path.join(SRC_DIR, script)
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Pipeline script not found: {script_path}")

        # Starte Subprocess mit Filtering
        try:
            result = subprocess.run(
                [VENV_PYTHON, script_path],
                cwd=SRC_DIR,
                capture_output=True,
                text=True,
                timeout=3600,  # 1h timeout pro step
            )

            # Log stdout/stderr
            if result.stdout:
                for line in result.stdout.split('\n')[-5:]:  # Letzten 5 Zeilen
                    if line.strip():
                        task.log.append(f"  → {line}")
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"{script} failed: {error_msg[:500]}")

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"{script} timed out after 1 hour")
        except Exception as e:
            raise RuntimeError(f"Failed to run {script}: {str(e)}")

    def add_task(self, task_type: str, data) -> str:
        """Füge Task zur Queue hinzu."""
        task = Task(task_type, data)
        with self.lock:
            self.tasks[task.id] = task
        return task.id

    def get_task(self, task_id: str):
        """Hole Task-Status."""
        with self.lock:
            task = self.tasks.get(task_id)
            return task.to_dict() if task else None

    def list_tasks(self):
        """Liste alle Tasks."""
        with self.lock:
            return [t.to_dict() for t in sorted(
                self.tasks.values(), 
                key=lambda x: x.created_at, 
                reverse=True
            )[:20]]  # Neueste 20

    def cancel_task(self, task_id: str):
        """Breche Task ab."""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.CANCELLED
                return True
        return False

    def clear_old_tasks(self, keep_count=50):
        """Lösche alte Tasks."""
        with self.lock:
            if len(self.tasks) > keep_count:
                sorted_tasks = sorted(self.tasks.items(), key=lambda x: x[1].created_at, reverse=True)
                to_delete = sorted_tasks[keep_count:]
                for task_id, _ in to_delete:
                    del self.tasks[task_id]


def recognize_company_by_name(company_name: str):
    """
    Nutze OpenAI um aus einem Firmennamen die strukturierten Daten zu extrahieren.
    Gibt zurück: company_id, company_name, country, website, ir_url (falls bekannt)
    """
    if not openai_client:
        raise RuntimeError("OpenAI client not available")
    
    prompt = f"""Extract company information from this company name: "{company_name}"

Return ONLY a JSON object (no markdown, no explanation) with these fields:
{{
  "company_id": "lowercase_id_with_underscores",
  "company_name": "Official Company Name",
  "country": "ISO_COUNTRY_CODE",
  "website": "https://www.company.com",
  "ir_url": "https://investor.company.com or null if unknown"
}}

Be accurate with the official company names and websites. If unsure about ir_url, set to null."""

    try:
        response = openai_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are an expert in identifying global companies and their investor relations pages. Return only valid JSON.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            temperature=0.1,
            max_tokens=300,
        )
        
        result_text = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        result_text = result_text.strip()
        
        company_data = json.loads(result_text)
        
        # Validierung
        required = ['company_id', 'company_name', 'country', 'website']
        if not all(k in company_data for k in required):
            raise ValueError(f"Missing required fields. Got: {list(company_data.keys())}")
        
        # Standardize empty/null ir_url
        if not company_data.get('ir_url'):
            company_data['ir_url'] = ''
        
        return company_data
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to recognize company: {str(e)}")


# ── Global Instance ──────────────────────────────────────────────────────────
queue = PipelineQueue()

