import os
import re
import sys


EXTENSIONS = {
    '.js': 'js',
    '.jsx': 'js',
    '.ts': 'js',
    '.tsx': 'js',
    '.py': 'py',
    '.css': 'css',
    '.scss': 'css',
    '.html': 'html',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.dockerfile': 'docker',
    '.Dockerfile': 'docker',
}


PATTERNS = {
    'js': [
        
        re.compile(r'//.*?$|/\*.*?\*/', re.MULTILINE | re.DOTALL),
        
        re.compile(r'/\*.*?\*/', re.DOTALL),
    ],
    'py': [
        
        re.compile(r'
    ],
    'css': [
        re.compile(r'/\*.*?\*/', re.DOTALL),
    ],
    'html': [
        re.compile(r'<!--.*?-->', re.DOTALL),
    ],
    'yaml': [
        re.compile(r'
    ],
    'docker': [
        re.compile(r'
    ],
}

def strip_comments_from_text(text, lang):
    for pat in PATTERNS.get(lang, []):
        text = pat.sub('', text)
    return text

def process_file(path):
    _, ext = os.path.splitext(path)
    lang = EXTENSIONS.get(ext.lower())
    if not lang:
        return
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = strip_comments_from_text(content, lang)
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Stripped comments from: {path}")
    except Exception as e:
        print(f"Error processing {path}: {e}")

def walk_dir(root):
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            full_path = os.path.join(dirpath, name)
            process_file(full_path)

if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
    walk_dir(project_root)
    print('Comment stripping complete.')
