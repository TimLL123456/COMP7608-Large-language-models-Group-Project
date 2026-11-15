"""Download official Mini-Dev database seed layers over HTTPS without Docker."""
from __future__ import annotations

import json
import hashlib

import requests
from pathlib import Path, PurePosixPath
import re
import sys
import shutil
import tarfile
from urllib.request import urlopen

IMAGE_REPO = "3036197201/bird-mini-dev-sqlite"


def image_refs(db_ids: set[str]) -> dict[str, str]:
    """Resolve per-database reviewed-release tags to immutable image digests."""
    url = f"https://hub.docker.com/v2/repositories/{IMAGE_REPO}/tags?page_size=100"
    tags = []
    while url:
        if not url.startswith(f"https://hub.docker.com/v2/repositories/{IMAGE_REPO}/tags"):
            raise ValueError("Unexpected Docker Hub pagination URL")
        with urlopen(url, timeout=60) as response:
            page = json.load(response)
        tags.extend(page["results"])
        url = page.get("next")
    refs = {}
    for db_id in sorted(db_ids):
        matches = [t for t in tags if t["name"].startswith(f"harbor-minidev1024-r1-{db_id}-")]
        if len(matches) != 1 or not re.fullmatch(r"sha256:[0-9a-f]{64}", matches[0].get("digest", "")):
            raise ValueError(f"Cannot uniquely resolve reviewed database image: {db_id}")
        refs[db_id] = f"{IMAGE_REPO}@{matches[0]['digest']}"
    return refs


def extract_database(archive: Path, destination: Path, db_id: str) -> None:
    """Copy database and CSV descriptions only; never extract image paths or links."""
    with tarfile.open(archive) as source:
        matches = [m for m in source.getmembers() if m.isfile() and
                   (PurePosixPath(m.name).name == f"{db_id}.sqlite" or
                    str(PurePosixPath(m.name)).lstrip("./") == "opt/dii/seed.sqlite")]
        if len(matches) != 1:
            raise ValueError(f"Expected one database in image for {db_id}, got {len(matches)}")
        member = matches[0]
        folder = destination / db_id
        folder.mkdir(parents=True)
        with source.extractfile(member) as src, (folder / f"{db_id}.sqlite").open("wb") as dst:
            shutil.copyfileobj(src, dst)
        description_root = str(PurePosixPath(member.name).parent / "database_description") + "/"
        for item in source.getmembers():
            if item.isfile() and item.name.startswith(description_root) and item.name.endswith(".csv"):
                target = folder / "database_description" / PurePosixPath(item.name).name
                target.parent.mkdir(exist_ok=True)
                with source.extractfile(item) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)


class Registry:
    """Public OCI downloads; verify descriptors before interpreting their content."""

    def __init__(self):
        self.session = requests.Session()
        response = self.session.get(
            "https://auth.docker.io/token",
            params={"service": "registry.docker.io", "scope": f"repository:{IMAGE_REPO}:pull"},
            timeout=(15, 60))
        response.raise_for_status()
        self.headers = {"Authorization": "Bearer " + response.json()["token"]}
        self.base = f"https://registry-1.docker.io/v2/{IMAGE_REPO}"

    def close(self):
        self.session.close()

    @staticmethod
    def check(data: bytes, digest: str) -> None:
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest) or "sha256:" + hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("Registry content digest mismatch")

    def document(self, kind: str, digest: str) -> dict:
        headers = dict(self.headers)
        headers["Accept"] = ", ".join([
            "application/vnd.oci.image.index.v1+json",
            "application/vnd.docker.distribution.manifest.list.v2+json",
            "application/vnd.oci.image.manifest.v1+json",
            "application/vnd.docker.distribution.manifest.v2+json"])
        response = self.session.get(f"{self.base}/{kind}/{digest}", headers=headers, timeout=(15, 60))
        response.raise_for_status()
        self.check(response.content, digest)
        return response.json()

    def seed_layer(self, image_digest: str) -> tuple[str, dict]:
        manifest = self.document("manifests", image_digest)
        platform_digest = image_digest
        if "manifests" in manifest:
            candidates = [m for m in manifest["manifests"]
                          if m.get("platform", {}).get("os") == "linux"
                          and m.get("platform", {}).get("architecture") == "amd64"]
            if len(candidates) != 1:
                raise ValueError("Expected one Linux amd64 image manifest")
            platform_digest = candidates[0]["digest"]
            manifest = self.document("manifests", platform_digest)
        config = self.document("blobs", manifest["config"]["digest"])
        history = [h for h in config.get("history", []) if not h.get("empty_layer", False)]
        if len(history) != len(manifest["layers"]):
            raise ValueError("Image history and layers disagree")
        candidates = [i for i, h in enumerate(history)
                      if re.search(r"^COPY seed\.sqlite /opt/dii/seed\.sqlite(?: |$)", h.get("created_by", ""))]
        # Current reviewed images end with the seed layer. Fail on a changed layout
        # rather than ignoring later layers that could replace or delete the seed.
        if not candidates or candidates[-1] != len(history) - 1:
            raise ValueError("Unsupported reviewed image layout: expected final seed.sqlite layer")
        return platform_digest, manifest["layers"][candidates[-1]]

    def download(self, descriptor: dict, cache: Path) -> Path:
        digest = descriptor["digest"]
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError("Invalid layer digest")
        cache.mkdir(parents=True, exist_ok=True)
        target = cache / (digest.split(":")[1] + ".tar.gz")
        if target.is_file():
            from .bird import sha256_file
            if target.stat().st_size == descriptor["size"] and sha256_file(target) == digest.split(":")[1]:
                return target
        partial = target.with_suffix(".part")
        hasher = hashlib.sha256()
        size = 0
        try:
            # requests strips Authorization when following cross-host redirects.
            with self.session.get(f"{self.base}/blobs/{digest}", headers=self.headers,
                                  stream=True, timeout=(15, 120)) as response:
                response.raise_for_status()
                with partial.open("wb") as output:
                    for chunk in response.iter_content(1024 * 1024):
                        size += len(chunk)
                        if size > descriptor["size"]:
                            raise ValueError("Layer exceeds declared size")
                        hasher.update(chunk)
                        output.write(chunk)
            if size != descriptor["size"] or hasher.hexdigest() != digest.split(":")[1]:
                raise ValueError("Downloaded layer size/digest mismatch")
            partial.replace(target)
        finally:
            partial.unlink(missing_ok=True)
        return target


def fetch_databases(destination: Path, db_ids: set[str]) -> dict:
    """Fetch only database seed layers over HTTPS; no Docker daemon or root."""
    refs = image_refs(db_ids)
    registry = Registry()
    provenance = {}
    try:
        for db_id, ref in refs.items():
            print(f"Downloading and verifying {db_id} SQLite database...", file=sys.stderr, flush=True)
            platform, layer = registry.seed_layer(ref.split("@", 1)[1])
            cache = destination.parents[2] / "_downloads" / "image-layers"
            archive = registry.download(layer, cache)
            extract_database(archive, destination, db_id)
            provenance[db_id] = {"image": ref, "platform_manifest": platform,
                                 "seed_layer": layer["digest"]}
    except requests.RequestException as exc:
        raise RuntimeError("Database HTTPS download failed; check network access or registry rate limits") from exc
    finally:
        registry.close()
    return provenance
