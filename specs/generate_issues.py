#!/usr/bin/env python3
import os
import sys
import re
import argparse
import requests
from typing import List, Dict, Optional

API_URL = "https://api.github.com"


def parse_repo(repo_arg: str):
    """
    Accepte:
      - owner/repo
      - https://github.com/owner/repo
      - https://github.com/owner/repo.git
    Retourne (owner, repo)
    """
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


def fetch_existing_issue_titles(owner: str, repo: str, token: str) -> set:
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


def create_issue(owner: str, repo: str, token: str, title: str, body: str,
                 labels: Optional[List[str]] = None):
    headers = github_headers(token)
    payload = {
        "title": title,
        "body": body,
    }
    if labels:
        payload["labels"] = labels

    r = requests.post(
        f"{API_URL}/repos/{owner}/{repo}/issues",
        headers=headers,
        json=payload,
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


def parse_todo_md(path: str) -> List[Dict]:
    """
    Regroupe les tâches non cochées par sous-section ###.
    Si une section ## contient directement des tâches sans ###,
    elle devient elle-même une issue.

    Retourne une liste d'objets:
    {
      "title": "...",
      "section": "...",
      "subsection": "... or None",
      "items": ["...", "..."]
    }
    """
    h2_re = re.compile(r"^##\s+(.*)")
    h3_re = re.compile(r"^###\s+(.*)")
    unchecked_re = re.compile(r"^\s*-\s+\[\s\]\s+(.*)")
    checked_re = re.compile(r"^\s*-\s+\[[xX]\]\s+(.*)")

    current_h2 = None
    current_h3 = None

    groups: List[Dict] = []
    current_group = None

    def flush_group():
        nonlocal current_group
        if current_group and current_group["items"]:
            groups.append(current_group)
        current_group = None

    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")

            m2 = h2_re.match(line)
            if m2:
                flush_group()
                current_h2 = m2.group(1).strip()
                current_h3 = None
                continue

            m3 = h3_re.match(line)
            if m3:
                flush_group()
                current_h3 = m3.group(1).strip()
                current_group = {
                    "section": current_h2,
                    "subsection": current_h3,
                    "items": [],
                }
                continue

            m_unchecked = unchecked_re.match(line)
            if m_unchecked:
                item = m_unchecked.group(1).strip()

                if current_h3 is not None:
                    if current_group is None:
                        current_group = {
                            "section": current_h2,
                            "subsection": current_h3,
                            "items": [],
                        }
                    current_group["items"].append(item)
                elif current_h2 is not None:
                    if current_group is None:
                        current_group = {
                            "section": current_h2,
                            "subsection": None,
                            "items": [],
                        }
                    current_group["items"].append(item)
                continue

            # on ignore les tâches déjà cochées
            if checked_re.match(line):
                continue

    flush_group()

    # post-traitement du titre
    result = []
    for g in groups:
        if g["subsection"]:
            issue_title = g["subsection"]
        else:
            issue_title = g["section"] or "TODO"

        result.append({
            "title": issue_title,
            "section": g["section"],
            "subsection": g["subsection"],
            "items": g["items"],
        })

    return result


def build_issue_body(group: Dict, source_path: str, labels_hint: Optional[List[str]] = None) -> str:
    lines = []
    lines.append("## Source")
    lines.append(f"- Fichier: `{source_path}`")
    if group["section"]:
        lines.append(f"- Section: `{group['section']}`")
    if group["subsection"]:
        lines.append(f"- Sous-section: `{group['subsection']}`")
    lines.append("")
    lines.append("## Travail à réaliser")
    for item in group["items"]:
        lines.append(f"- [ ] {item}")
    lines.append("")
    lines.append("## Critère de clôture")
    lines.append("- Toutes les cases de cette issue sont traitées.")
    lines.append("- Les décisions structurantes sont tracées dans un fichier versionné si nécessaire.")
    lines.append("- Les tests ou validations minimales existent si le sujet porte sur un contrat, une formule ou un comportement.")
    if labels_hint:
        lines.append("")
        lines.append("## Étiquettes suggérées")
        for label in labels_hint:
            lines.append(f"- `{label}`")
    return "\n".join(lines)


def infer_labels(group: Dict) -> List[str]:
    text = " ".join(
        [group.get("section") or "", group.get("subsection") or "", *group.get("items", [])]
    ).lower()

    labels = ["todo"]

    if "contrat" in text:
        labels.append("contracts")
    if "mitre" in text:
        labels.append("mitre")
    if "vector" in text or "5d" in text:
        labels.append("vectorization")
    if "test" in text:
        labels.append("tests")
    if "calibration" in text or "seuil" in text:
        labels.append("calibration")
    if "baseline" in text or "matching" in text or "dtw" in text:
        labels.append("matching")
    if "archiv" in text or "mahalanobis" in text:
        labels.append("archive")
    if "corpus" in text or "données" in text:
        labels.append("dataset")
    if "traçabilité" in text or "révision" in text:
        labels.append("traceability")

    # dédoublonnage en conservant l'ordre
    seen = set()
    out = []
    for x in labels:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/repo ou https://github.com/owner/repo")
    parser.add_argument("--todo", default="TODO.md", help="chemin vers TODO.md")
    parser.add_argument("--prefix", default="[TODO]", help="préfixe du titre d'issue")
    parser.add_argument("--dry-run", action="store_true", help="n'écrit rien sur GitHub")
    parser.add_argument("--skip-existing", action="store_true", help="ignore les titres déjà présents")
    parser.add_argument("--no-labels", action="store_true", help="ne pas proposer/appliquer de labels")
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
        sys.exit("Aucune tâche non cochée détectée dans le TODO.")

    existing_titles = set()
    if args.skip_existing:
        existing_titles = fetch_existing_issue_titles(owner, repo, token)

    created = 0
    skipped = 0

    for group in groups:
        title = f"{args.prefix} {group['title']}".strip()
        labels = [] if args.no_labels else infer_labels(group)
        body = build_issue_body(group, args.todo, labels_hint=None)

        if args.skip_existing and title in existing_titles:
            print(f"SKIP  {title} (déjà existante)")
            skipped += 1
            continue

        if args.dry_run:
            print("=" * 80)
            print(title)
            print("- labels:", ", ".join(labels) if labels else "(aucun)")
            print(body)
            print()
            created += 1
            continue

        issue = create_issue(owner, repo, token, title, body, labels=labels)
        print(f"OK    #{issue['number']} {issue['title']}")
        created += 1

    print(f"\nRésumé: {created} issues traitées, {skipped} ignorées.")


if __name__ == "__main__":
    main()