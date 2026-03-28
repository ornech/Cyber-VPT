#!/usr/bin/env python3
import os
import sys
import re
import json
import argparse
import requests

API_URL = "https://api.github.com"


def parse_repo(repo_arg: str):
    s = repo_arg.strip()

    m = re.match(r"^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", s)
    if m:
        return m.group(1), m.group(2)

    if "/" in s and "github.com" not in s:
        owner, repo = s.split("/", 1)
        return owner.strip(), repo.strip()

    raise ValueError("Format attendu: owner/repo ou https://github.com/owner/repo")


def github_headers(token: str):
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "todo-to-issues-script",
    }


def fetch_existing_issue_titles(owner, repo, token):
    headers = github_headers(token)
    titles = set()
    page = 1

    while True:
        r = requests.get(
            f"{API_URL}/repos/{owner}/{repo}/issues",
            headers=headers,
            params={"state": "all", "per_page": 100, "page": page},
            timeout=30,
        )

        if r.status_code == 401:
            raise RuntimeError("401 Unauthorized: token absent/invalide.")
        if r.status_code == 403:
            raise RuntimeError("403 Forbidden: rate limit ou droits insuffisants.")
        if r.status_code == 404:
            raise RuntimeError("404 Not Found: repo inexistant ou token sans accès.")

        r.raise_for_status()
        data = r.json()
        if not data:
            break

        for it in data:
            if "pull_request" in it:
                continue
            titles.add(it.get("title", "").strip())

        page += 1

    return titles


def create_issue(owner, repo, token, title, body):
    headers = github_headers(token)

    r = requests.post(
        f"{API_URL}/repos/{owner}/{repo}/issues",
        headers=headers,
        json={"title": title, "body": body},
        timeout=30,
    )

    if r.status_code == 401:
        raise RuntimeError("401 Unauthorized: token absent/invalide.")
    if r.status_code == 403:
        raise RuntimeError("403 Forbidden: rate limit ou droits insuffisants.")
    if r.status_code == 404:
        raise RuntimeError("404 Not Found: repo inexistant ou token sans accès.")
    if r.status_code == 422:
        raise RuntimeError(f"422 Unprocessable Entity: {r.text}")

    r.raise_for_status()
    return r.json()


def parse_todo_md(path: str):
    """
    Règle:
    - chaque sous-section ### devient une issue
    - les lignes - [ ] deviennent la checklist de l'issue
    - les sections sans ### sont ignorées
    """
    h2_re = re.compile(r"^##\s+(.*)")
    h3_re = re.compile(r"^###\s+(.*)")
    unchecked_re = re.compile(r"^\s*-\s+\[\s\]\s+(.*)")
    checked_re = re.compile(r"^\s*-\s+\[[xX]\]\s+(.*)")

    current_h2 = None
    current_h3 = None
    current_items = []

    groups = []

    def flush():
        nonlocal current_h3, current_items
        if current_h3 and current_items:
            groups.append(
                {
                    "section": current_h2,
                    "subsection": current_h3,
                    "items": current_items[:],
                }
            )
        current_h3 = None
        current_items = []

    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")

            m2 = h2_re.match(line)
            if m2:
                flush()
                current_h2 = m2.group(1).strip()
                continue

            m3 = h3_re.match(line)
            if m3:
                flush()
                current_h3 = m3.group(1).strip()
                continue

            if checked_re.match(line):
                continue

            m_unchecked = unchecked_re.match(line)
            if m_unchecked and current_h3:
                current_items.append(m_unchecked.group(1).strip())

    flush()
    return groups


def build_issue_title(group, prefix):
    # Exemple: [TODO] 1.1 — Vector5D
    return f"{prefix} {group['subsection']}".strip()


def build_issue_body(group, source_path):
    lines = []
    lines.append("## Source")
    lines.append(f"- Fichier: `{source_path}`")
    if group["section"]:
        lines.append(f"- Section: `{group['section']}`")
    lines.append(f"- Sous-section: `{group['subsection']}`")
    lines.append("")
    lines.append("## Tâches")
    for item in group["items"]:
        lines.append(f"- [ ] {item}")
    lines.append("")
    lines.append("## Critère de clôture")
    lines.append("- Toutes les cases de cette sous-section sont traitées.")
    lines.append("- Les décisions structurantes sont tracées si nécessaire.")
    lines.append("- Les tests ou validations attendus existent lorsque le sujet l'exige.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/repo ou https://github.com/owner/repo")
    parser.add_argument("--todo", default="TODO.md", help="chemin vers TODO.md")
    parser.add_argument("--prefix", default="[TODO]", help="préfixe des titres d'issues")
    parser.add_argument("--dry-run", action="store_true", help="n'envoie rien à GitHub")
    parser.add_argument("--skip-existing", action="store_true", help="ignore les titres déjà présents")
    parser.add_argument("--dump-json", help="écrit aussi les groupes extraits dans un JSON")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN non défini (ex: export GITHUB_TOKEN='ghp_...')")

    if not os.path.isfile(args.todo):
        sys.exit(f"Fichier introuvable: {args.todo}")

    try:
        owner, repo = parse_repo(args.repo)
    except ValueError as e:
        sys.exit(str(e))

    groups = parse_todo_md(args.todo)
    if not groups:
        sys.exit("Aucune sous-section ### avec tâches non cochées détectée.")

    if args.dump_json:
        with open(args.dump_json, "w", encoding="utf-8") as f:
            json.dump(groups, f, indent=2, ensure_ascii=False)

    existing_titles = set()
    if args.skip_existing:
        existing_titles = fetch_existing_issue_titles(owner, repo, token)

    created = 0
    skipped = 0

    for group in groups:
        title = build_issue_title(group, args.prefix)
        body = build_issue_body(group, args.todo)

        if args.skip_existing and title in existing_titles:
            print(f"SKIP  {title} (déjà existante)")
            skipped += 1
            continue

        if args.dry_run:
            print("=" * 80)
            print(title)
            print(body)
            print()
            created += 1
            continue

        issue = create_issue(owner, repo, token, title, body)
        print(f"OK    #{issue['number']} {issue['title']}")
        created += 1

    print(f"\nRésumé: {created} issues traitées, {skipped} ignorées.")


if __name__ == "__main__":
    main()