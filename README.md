# Validador de Plano de Contas em PDF

Ferramenta desktop em Python para validar automaticamente a estrutura, os códigos e a consistência de arquivos PDF de **Plano de Contas** contábeis antes da importação em sistemas ERP/contábeis.

<!-- Adicione aqui um print ou GIF curto mostrando a janela selecionando um PDF e exibindo o relatório -->
> 📸 **Demonstração:** adicione uma captura de tela da interface e de um log de validação exportado.

---

## Contexto e Impacto

A conferência manual de planos de contas em PDF com dezenas ou centenas de páginas era lenta e sujeita a falhas humanas (códigos fora do padrão, descrições corrompidas ou tokens colados na extração).

- **Resultado prático:** aplicação utilizada internamente na operação contábil, **dobrando a velocidade de conferência (+100% de produtividade)** e padronizando o diagnóstico de erros antes do processamento.
- **Usabilidade:** empacotada para rodar sem exigir terminal ou Python instalado no computador do usuário final.

---

## O que o Validador Verifica

Utilizando `pdfplumber` para extração linha a linha, o script (`validador-de-pdf.py`) analisa linhas iniciadas por dígito e separa inconsistências em dois níveis:

1. **Erros Fatais** *(interrompem a validação por comprometerem a estrutura do plano)*:
   - Número mínimo de tokens/colunas ausente na linha;
   - Formato inválido do código da conta ou da classificação contábil (ex.: `1`, `1.1`, `1.1.01`);
   - Descrição da conta sem caracteres alfabéticos.
2. **Avisos / Erros Não Fatais**:
   - Detecção de "tokens grudados" na descrição (sequências longas alfanuméricas misturadas geradas por PDFs mal formatados).
3. **Exportação de Log**:
   - Gera arquivo `.txt` detalhando página, linha aproximada, conteúdo e motivo para correção rápida.

---

## Stack Utilizada

- **Python 3**
- **pdfplumber** (extração estruturada de texto de PDF)
- **Tkinter** (interface gráfica nativa)
- **PyInstaller** (`ValidadorPlanoContas.spec` para empacotamento em executável Windows)

---

## Como Executar via Código-Fonte

1. Clone o repositório:
   ```bash
   git clone https://github.com/TawanMd/PDF-testing.git
   cd PDF-testing
   ```
2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   pip install pdfplumber
   ```
3. Execute a aplicação:
   ```bash
   python validador-de-pdf.py
   ```

### Gerar Executável Localmente (Opcional)

> [!NOTE]
> As pastas `build/`, `dist/` e arquivos `.exe` não devem ser versionados no repositório Git. Gere o executável localmente ou publique-o na aba **GitHub Releases**.

```bash
pip install pyinstaller
pyinstaller ValidadorPlanoContas.spec
```
O arquivo gerado ficará localmente em `dist/ValidadorPlanoContas.exe`.
