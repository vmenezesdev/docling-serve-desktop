# Achados do Build — Docling Serve Desktop

Data: 2025-12-11

Este documento resume a análise dos arquivos de build, os erros mais frequentes observados em projetos Python empacotados com PyInstaller, padrões de projeto recomendados e um checklist pré-build acionável.

**Arquivos analisados**
- `build_portable.py` — script de automação do build (instala dependências, chama PyInstaller e cria `dist/DoclingServeDesktop`).
- `build_portable.spec` — arquivo `.spec` do PyInstaller com `hiddenimports`, `collect_data_files` e `runtime_hooks`.
- `docling_serve_desktop_launcher.py` — launcher que trata `multiprocessing`, `_MEIPASS` e limpeza de `sys.argv` antes de delegar para `docling_serve.__main__`.
- `hooks/` — contém hooks customizados (ex.: `hook-multiprocessing.py`, `runtime_hook_multiprocessing.py`).

## Erros e problemas frequentes ao empacotar com PyInstaller

- Imports faltando / `ModuleNotFoundError`.
  - Causa: imports dinâmicos, import por string, plugins e pacotes não detectados pelo analisador do PyInstaller.
  - Mitigação: usar `hiddenimports`, `collect_submodules()` no `.spec` ou escrever hooks personalizados em `hooks/`.

- Dados e modelos não incluídos (arquivos estáticos, modelos ONNX, templates).
  - Causa: arquivos não-Python checados pelo script de build não são coletados automaticamente.
  - Mitigação: `collect_data_files()` no `.spec` ou `--add-data`, e resolver recursos via `sys._MEIPASS` quando congelado.

- Dependências nativas ausentes / DLLs faltando (ONNXRuntime, PyTorch, MKL/OpenBLAS).
  - Causa: binários `.pyd`/DLLs não incluídos automaticamente ou requerem redistribuíveis do Windows.
  - Mitigação: preencher `binaries` no `.spec`, testar em máquina limpa/CI e documentar necessidade do Visual C++ Redistributable.

- Problemas com `multiprocessing` (erros `--multiprocessing-fork`, comportamento diferente em executável).
  - Mitigação: usar `multiprocessing.freeze_support()`, `multiprocessing.set_start_method('spawn')` no launcher e limpar argumentos internos do PyInstaller (como já existe em `docling_serve_desktop_launcher.py`).

- UPX e corrupção / incompatibilidades com antivírus.
  - Mitigação: testar com `--noupx`; manter opção para desativar UPX no script (`--no-upx` já suportado); em releases preferir builds sem UPX se gerar falsos-positivos.

- Tamanho do executável (modelos grandes embutidos).
  - Mitigação: não embutir modelos grandes no `.exe`; distribuir modelos ao lado do binário ou implementar download/caching no primeiro run (usar `platformdirs` para cache).

- Caminhos relativos / recursos e `sys._MEIPASS`.
  - Mitigação: resolver caminhos com `base = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))`.

- Incompatibilidades entre versões do Python e do PyInstaller.
  - Mitigação: travar versões em `requirements-build.txt` e testar matrix de versões em CI.

## Padrões de projeto recomendados

- Separação de responsabilidades: manter lógica de processamento em `docling_serve` (headless/testável) e deixar UI/launcher finos.
- Launcher mínimo: apenas setup (freeze_support, _MEIPASS, start method) e delegação para `docling_serve.__main__`.
- Externalização de recursos grandes: modelos e dados grandes fora do `.exe`, com política de download/caching.
- Hooks e coleta explícita: manter `hooks/` e usar `collect_data_files()` e `binaries` no `.spec`.
- Desenvolvimento com `--onedir` para debugging; usar `--onefile` apenas quando necessário.
- Build reprodutível: travar versões, usar venv limpo e documentar versões (Python, PyInstaller).
- CI/CD para Windows: workflow que crie venv, instale `requirements-build.txt`, gere build `--onedir`, execute smoke tests e armazene artefatos.
- Logging e modo headless: oferecer `--no-gui` e logs em arquivo para permitir testes automatizados.
- Assinatura e distribuição segura: assinar executáveis (code signing) e publicar checksums.

## Checklist pré-build (passos práticos)

1. Ambiente limpo e dependências:

   - Crie e ative um virtualenv e instale dependências de build:

   ```bat
   python -m venv env
   env\\Scripts\\activate.bat
   pip install -r requirements-build.txt
   ```

2. Validar execução local (antes do empacotamento):

   ```bat
   python -m docling_serve --help
   python docling_serve_desktop_launcher.py desktop
   ```

3. Build em modo diretório (debug) e inspeção:

   ```bat
   python -m PyInstaller --clean --log-level=DEBUG --onedir build_portable.spec
   ```

   - Verifique `dist\\DoclingServeDesktop\\` contém `DoclingServeDesktop.exe`, modelos (se aplicável), DLLs/`.pyd` necessários e assets.

4. Detectar imports faltantes:

   - Execute `DoclingServeDesktop.exe` a partir da pasta `dist` e anote `ImportError`/`ModuleNotFoundError`.
   - Corrija adicionando `hiddenimports` ou criando hooks em `hooks/`.

5. Testar resolução de recursos com `_MEIPASS` (exemplo):

   ```python
   from pathlib import Path
   base = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
   resource = base / 'models' / 'model.onnx'
   ```

6. Testar com e sem UPX; verificar comportamento contra antivírus.

7. Testar em máquina limpa / runner CI Windows; certificar inclusão de DLLs nativas ou instruções para redistribuíveis.

8. Smoke tests automatizados (ex.: `--help`, `desktop --no-gui`) com exit code 0.

9. Assinatura e publicação: assinar binário e publicar `SHA256`.

## Ações imediatas sugeridas

- Adicionar smoke tests e workflow CI (Windows) que gere `--onedir` e execute testes básicos.
- Mover modelos grandes para `dist/models/` ou implementar download/caching no primeiro run.
- Atualizar `README.md` com passos de build e versões específicas do Python/PyInstaller.
- Verificar hooks atuais em `hooks/` e complementar para pacotes detectados dinamicamente.

## Comandos úteis rápidos (Windows cmd)

```bat
python -m venv env
env\\Scripts\\activate.bat
pip install -r requirements-build.txt
python -m PyInstaller --clean --log-level=DEBUG --onedir build_portable.spec
```

## Próximos passos recomendados

- Implementar workflow GitHub Actions (`windows-latest`) que:
  - Crie venv e instale `requirements-build.txt`.
  - Rode `python -m PyInstaller --clean --log-level=DEBUG --onedir build_portable.spec`.
  - Execute smoke tests no artefato gerado.
  - Publique os artefatos do build para revisão.

- Se desejar, posso criar o workflow de CI e adicionar smoke tests ao repositório.

---
Relatório gerado automaticamente durante análise do repositório local.
