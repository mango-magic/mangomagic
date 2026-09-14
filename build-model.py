#!/usr/bin/env python3
"""Build the cloud alias with real metadata, which Modelfile FROM drops in Ollama 0.34.

Maintainer command: python3 build-model.py; ollama push mangomagic/mangomagic-7.1
Reads the live base capabilities and preserves them using Ollama's /api/create info.
"""
import json
import re
import urllib.request
from pathlib import Path

MODEL = "mangomagic/mangomagic-7.1"
BASE = "glm-5.3-flash:cloud"
API = "http://127.0.0.1:11434"


def request(path, body):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as response:
        result = json.load(response)
    if result.get("error"):
        raise RuntimeError(result["error"])
    return result


def main():
    source = Path(__file__).with_name("MangoMagic_7.1.Modelfile").read_text()
    if re.search(r"^FROM (.+)$", source, re.M).group(1) != BASE:
        raise ValueError("The Modelfile must use the verified GLM 5.3 Flash base.")
    system = re.search(r'SYSTEM """(.*?)"""', source, re.S).group(1)
    parameters = {}
    for name, value in re.findall(r"^PARAMETER (\w+) (.+)$", source, re.M):
        parameters[name] = json.loads(value)
    base = request("/api/show", {"model": BASE})
    capabilities = base.get("capabilities", [])
    if not {"completion", "vision", "thinking", "tools"}.issubset(capabilities):
        raise ValueError("The live base is missing required capabilities.")
    family = base["details"]["family"]
    if family != "glm5_next":
        raise ValueError("Unexpected base family; revalidate reasoning levels before publishing.")
    info = base["model_info"]
    context = info[family + ".context_length"]
    metadata = {"capabilities": capabilities, "model_family": family,
                "context_length": context, "base_name": BASE.removesuffix(":cloud"),
                "parameter_size": base["details"]["parameter_size"],
                "quantization_level": base["details"]["quantization_level"]}
    if family + ".embedding_length" in info:
        metadata["embedding_length"] = info[family + ".embedding_length"]
    result = request("/api/create", {"model": MODEL, "from": BASE, "system": system,
                                    "parameters": parameters, "info": metadata, "stream": False})
    if result.get("status") != "success":
        raise RuntimeError("Model creation did not report success.")
    actual = request("/api/show", {"model": MODEL})
    if not set(capabilities).issubset(actual.get("capabilities", [])):
        raise RuntimeError("The built model lost capability metadata.")
    if actual.get("system") != system or actual["details"]["family"] != family:
        raise RuntimeError("The built model did not preserve instructions and family metadata.")
    print(json.dumps({"model": MODEL, "base": BASE, "status": "verified", "info": metadata}, indent=2))


if __name__ == "__main__":
    main()
