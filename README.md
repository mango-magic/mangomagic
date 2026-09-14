# 🥭 MangoMagic 7.1

ManyMangoes' B2B Sales Intelligence model for ChatGPT.

## Install (one line)

Copy this into Terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/manymangoes/mangomagic/main/install.sh | bash
```

That's it. Open ChatGPT → click the model selector → choose **mangomagic/mangomagic-7.1**.

## What you get

A B2B sales model running on GLM 5.3 Flash, trained on ManyMangoes' proven sales methodology:
- Buyer-led outreach that opens with the prospect's trigger
- Evidence-based claims without invented metrics
- Objection handling that treats concerns as real
- Meeting conversion with concrete next actions

## Requirements

- ChatGPT Mac app ([download](https://chatgpt.com/download))
- Internet connection

## Manual setup

If you prefer to run commands individually:

```bash
# 1. Install Ollama (if you don't have it)
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull the model
ollama pull mangomagic/mangomagic-7.1

# 3. Add it to ChatGPT
ollama launch chatgpt --model mangomagic/mangomagic-7.1 --config
```

## Links

- [Ollama model page](https://ollama.com/mangomagic/mangomagic-7.1)
- [ManyMangoes](https://manymangoes.com)

---

Built by [ManyMangoes](https://manymangoes.com). B2B sales intelligence, without the hype.
