# MangoMagic 7.1 technical notes

This page records release provenance and implementation details for maintainers. Product descriptions and everyday assistant replies use MangoMagic 7.1 by ManyMangoes.

## For developers

- Model identifier: `mangomagic/mangomagic-7.1` (the normal `latest` tag; no `v0.1` suffix).
- Base: `glm-5.3-flash:cloud`.
- `MangoMagic_7.1.Modelfile` contains the public instructions.
- `configure-chatgpt.js` verifies the actual cloud backend and thinking routing, then brands the supported `model_catalog_json` entry. It uses built-in macOS JavaScript, preserves other models and does not modify credentials or app binaries.
- Build releases with `python3 build-model.py`, then `ollama push mangomagic/mangomagic-7.1`. The builder preserves live capabilities, model family and context using Ollama's create API. Creating this cloud alias using only a Modelfile drops that metadata in Ollama 0.34.0.
- Run installer tests with `python3 -m unittest discover -s tests -p 'test_*.py'`; run catalogue tests with `node tests/test_catalog.js`.

[GLM capabilities](https://ollama.com/library/glm-5.3-flash) · [ChatGPT catalogue configuration](https://learn.chatgpt.com/docs/config-file/config-reference)


## Customisation and attribution

MangoMagic 7.1 adds ManyMangoes' sales and communication instructions to the declared upstream model. This release does not include weight fine-tuning on private conversations. It retains the actual model family, capabilities, context metadata and routing. Branding must never change technical identifiers, erase required licence notices or imply that ManyMangoes trained the underlying foundation model.

When a user explicitly asks about architecture, training or provenance, answer accurately. Keep technical context out of unsolicited introductions and sales copy.
