# MangoMagic 7.1

![MangoMagic 7.1 by ManyMangoes. The business AI system for the modern worker.](https://mango-magic.github.io/mangomagic/assets/mangomagic-banner.svg)

**The business AI system for the modern worker.**

MangoMagic 7.1 by ManyMangoes brings concise answers, checked work and useful agents to your ChatGPT workspace. Work across operations, finance, people, marketing, sales, delivery and technology with the files and tools your app can access.

## Install with one command

```bash
bash -c 'f=$(mktemp) || exit; trap "rm -f \"$f\"" EXIT; curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/install.sh -o "$f" && bash "$f"'
```

The installer sets up Ollama, downloads MangoMagic, checks its capabilities, registers images and thinking controls, then gracefully quits and reopens ChatGPT. Choose **MangoMagic 7.1** in the model menu.

[Simple setup page](https://mango-magic.github.io/mangomagic/) · [Model on Ollama](https://ollama.com/mangomagic/mangomagic-7.1)

## Choose how it works

| Control | What it does |
| --- | --- |
| Image upload | Read screenshots, charts and other images alongside your question. |
| Light (Low / Light in ChatGPT) | Lighter reasoning effort for everyday tasks. |
| Mango (High in ChatGPT) | High reasoning effort for complex work and decisions. |
| Super Mango (Max in ChatGPT) | Maximum reasoning effort. For long missions, use Mango Loop to create and update `project_tasks.json` until 99% complete. |

Light, Mango and Super Mango are MangoMagic's three thinking choices, mapped to the supported low, high and max settings. They are included in the model catalogue descriptions. ChatGPT controls its native slider labels; this installer cannot rename High and Max.

All three use the same MangoMagic model and token rates. More thinking may consume more tokens and time; it does not guarantee a better answer or a fixed speed/cost difference on every question. Image input is available at every level. OpenAI's separate priority speed toggle is not an Ollama feature.

Check [current Ollama usage and pricing](https://ollama.com/pricing) for cloud access. This usage is billed separately from your ChatGPT subscription.

MangoMagic adds ManyMangoes' concise Australian voice, evidence checks, task ownership and practical delegation. It adapts to your department and available tools. This is an instruction-customised model; its weights have **not** been fine-tuned on private conversations. It only has private business context that you actually provide through your app or tools.

## Requirements

- macOS and the [ChatGPT desktop app](https://chatgpt.com/download).
- Internet access and [Ollama account access/credits](https://ollama.com/pricing) for the cloud model.
- Your ChatGPT subscription and Ollama usage are separate. This installer does not purchase a plan or credits.

A first installation may require the normal macOS installation or Ollama sign-in step. The script stops with a clear error if a required step fails.

## Update or repair

Run the same install command again. It backs up the model catalogue before repairing MangoMagic's entry. It restarts ChatGPT so the app loads the changes.

For a scripted setup that must leave the app running:

```bash
bash -c 'f=$(mktemp) || exit; trap "rm -f \"$f\"" EXIT; curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/install.sh -o "$f" && bash "$f" --no-restart'
```

That option reports **restart pending**. Quit and reopen ChatGPT before checking the new controls.

[Technical release notes](TECHNICAL-NOTES.md) · [Build an actually useful assistant](https://mango-magic.github.io/mangomagic/assistant.html)

Built by [ManyMangoes](https://manymangoes.com).
