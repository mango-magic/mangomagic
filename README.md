# MangoMagic 7.1

ManyMangoes' B2B sales intelligence for the ChatGPT Mac app, powered by GLM 5.3 Flash through Ollama.

## Install with one command

```bash
curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/install.sh | bash
```

The installer sets up Ollama, downloads MangoMagic, checks its capabilities, registers images and thinking controls, then gracefully quits and reopens ChatGPT. Choose **MangoMagic 7.1** in the model menu.

[Simple setup page](https://mango-magic.github.io/mangomagic/) · [Model on Ollama](https://ollama.com/mangomagic/mangomagic-7.1)

## Choose how it works

| Control | What it does |
| --- | --- |
| Image upload | Read screenshots, charts and other images alongside your question. |
| Light (Low / Light in ChatGPT) | Lighter reasoning effort for everyday tasks. |
| Mango (High in ChatGPT) | High reasoning effort for complex sales decisions. |
| Super Mango (Max in ChatGPT) | Maximum reasoning effort; replies may take longer. |

Light, Mango and Super Mango are our names for GLM's low, high and max reasoning settings. They are included in the model catalogue descriptions. ChatGPT controls its native slider labels; this installer cannot rename High and Max.

All three use the same GLM 5.3 Flash model and token prices. More thinking may consume more tokens and time; it does not guarantee a better answer or a fixed speed/cost difference on every question. Image input is available at every level. OpenAI's separate priority speed toggle is not an Ollama feature.

As checked on 14 September 2026, [Ollama lists](https://ollama.com/pricing) GLM 5.3 Flash at US$0.15 input, US$0.03 cached input and US$0.50 output per million tokens. Ollama credits cover this usage separately from your ChatGPT subscription.

MangoMagic adds ManyMangoes' direct Australian voice, buyer-led outreach, evidence discipline, objection handling and clear next actions. This is an instruction-customised model; its weights have **not** been fine-tuned on private conversations. It only has private business context that you actually provide through your app or tools.

## Requirements

- macOS and the [ChatGPT desktop app](https://chatgpt.com/download).
- Internet access and [Ollama account access/credits](https://ollama.com/pricing) for the cloud model.
- Your ChatGPT subscription and Ollama usage are separate. This installer does not purchase a plan or credits.

A first installation may require the normal macOS installation or Ollama sign-in step. The script stops with a clear error if a required step fails.

## Update or repair

Run the same install command again. It backs up the model catalogue before repairing MangoMagic's entry. It restarts ChatGPT so the app loads the changes.

For a scripted setup that must leave the app running:

```bash
curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/install.sh | bash -s -- --no-restart
```

That option reports **restart pending**. Quit and reopen ChatGPT before checking the new controls.

## For developers

- Model identifier: `mangomagic/mangomagic-7.1` (the normal `latest` tag; no `v0.1` suffix).
- Base: `glm-5.3-flash:cloud`.
- `MangoMagic_7.1.Modelfile` contains the public instructions.
- `configure-chatgpt.js` verifies the actual cloud backend and thinking routing, then brands the supported `model_catalog_json` entry. It uses built-in macOS JavaScript, preserves other models and does not modify credentials or app binaries.
- Build releases with `python3 build-model.py`, then `ollama push mangomagic/mangomagic-7.1`. The builder preserves live capabilities, model family and context using Ollama's create API. Creating this cloud alias using only a Modelfile drops that metadata in Ollama 0.34.0.
- Run installer tests with `python3 -m unittest discover -s tests -p 'test_*.py'`; run catalogue tests with `node tests/test_catalog.js`.

[GLM capabilities](https://ollama.com/library/glm-5.3-flash) · [ChatGPT catalogue configuration](https://learn.chatgpt.com/docs/config-file/config-reference)

Built by [ManyMangoes](https://manymangoes.com).
