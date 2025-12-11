# Fix para o Loop Infinito de Multiprocessing

## Problema

O executável estava entrando em um loop infinito ao ser executado, criando múltiplos processos e consumindo toda a memória. Isso acontecia porque:

1. O PyInstaller no Windows usa multiprocessing que reinicia o executável para criar processos filhos
2. Sem proteções adequadas, cada processo filho executava o código principal novamente
3. Cada execução criava novos processos filhos, causando um loop infinito

## Correções Aplicadas

### 1. **docling_serve_desktop_launcher.py**

- Movido `multiprocessing.freeze_support()` para dentro do bloco `if __name__ == '__main__'`
- Adicionada limpeza de argumentos do multiprocessing (`parent_pid=`, `--multiprocessing-fork`, etc.)
- Proteção do código principal com `if __name__ == '__main__'`

### 2. **hooks/runtime_hook_multiprocessing.py**

- **REMOVIDA** a limpeza de argumentos do multiprocessing deste arquivo.
- A limpeza aqui estava removendo as flags (`--multiprocessing-fork`) *antes* que `multiprocessing.freeze_support()` pudesse vê-las.
- Isso fazia com que os processos filhos fossem identificados incorretamente como processos principais, causando o loop infinito.
- Mantida apenas a configuração de `spawn` method.

### 3. **docling_serve/desktop.py**

- Adicionada configuração explícita do método de start do multiprocessing para 'spawn'
- Garantia de compatibilidade com PyInstaller frozen executables

## Como Reconstruir

```bash
# Reconstruir o executável com as correções
python build_portable.py --skip-deps

# Ou, se quiser limpar tudo primeiro
python build_portable.py --clean --skip-deps
```

## Como Testar

1. Execute o arquivo `.bat`:

   ```
   dist\DoclingServeDesktop\Start Docling Desktop.bat
   ```

2. Ou execute o `.exe` diretamente:

   ```
   dist\DoclingServeDesktop\DoclingServeDesktop.exe desktop
   ```

3. Verifique que:
   - Aparece apenas UMA mensagem "Starting Docling Serve Desktop Application"
   - O servidor inicia normalmente
   - Uma janela do navegador/pywebview abre
   - O uso de memória permanece estável

## Explicação Técnica

### Por que isso acontece?

No Windows, o multiprocessing usa o método 'spawn' que:

1. Inicia um novo processo Python
2. Reimporta o módulo principal
3. Executa a função target especificada

Sem proteções, o PyInstaller:

1. Executa o .exe principal
2. Cria um processo filho que executa o .exe novamente
3. O filho cria outro filho
4. Loop infinito

### Solução

1. **freeze_support()**: Deve estar no `if __name__ == '__main__'` para que processos filhos não executem o código principal
2. **Limpeza de argumentos**: Processos filhos recebem argumentos internos como `parent_pid=123` que precisam ser removidos
3. **Proteção do código**: Todo código que cria processos deve estar protegido por `if __name__ == '__main__'`

## Referências

- [PyInstaller Documentation - Multiprocessing](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#multi-processing)
- [Python multiprocessing with Windows and PyInstaller](https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing)
