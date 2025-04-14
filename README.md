# Validador de Plano de Contas em PDF

## Descrição

Esta ferramenta foi desenvolvida para validar a estrutura e a formatação de linhas dentro de arquivos PDF que representam um plano de contas. Ela utiliza uma interface gráfica simples para facilitar a seleção do arquivo e a visualização dos resultados.

## Funcionalidades Principais

*   **Interface Gráfica:** Permite ao usuário selecionar facilmente o arquivo PDF a ser validado.
*   **Extração de Texto:** Utiliza a biblioteca `pdfplumber` para extrair o texto das páginas do PDF.
*   **Validação Estrutural:** Verifica cada linha relevante (que começa com um dígito) de acordo com regras específicas:
    *   Número mínimo de componentes (tokens) na linha.
    *   Formato do código da conta (ex: `1`, `1.1`, `1.1.01`).
    *   Formato da classificação da conta (mesmo formato do código).
    *   Presença de letras na descrição da conta.
*   **Detecção de Erros:**
    *   **Erros Fatais:** Problemas que impedem a validação correta (ex: formato de código inválido, número incorreto de tokens, descrição sem letras). A validação é interrompida se um erro fatal for encontrado.
    *   **Erros Não Fatais:** Avisos sobre possíveis problemas que não impedem a continuação da análise, especificamente a detecção de "tokens grudados" na descrição (sequências longas de letras e números misturados, ex: `DESPESA12345COM`).
*   **Relatório de Erros:**
    *   Exibe mensagens claras sobre erros fatais.
    *   Notifica sobre a ocorrência de erros não fatais e permite visualizar os detalhes (página, linha aproximada, conteúdo e motivo).
    *   Permite exportar um log completo (erros fatais e não fatais) para um arquivo de texto (`.txt`).

## Como Usar

Existem duas formas de utilizar o validador:

### 1. Usando o Executável (Recomendado)

A maneira mais simples é utilizar o executável pré-compilado.

1.  Navegue até a pasta `dist/` neste projeto.
2.  Execute o arquivo `ValidadorPlanoContas.exe`.
3.  Na janela do aplicativo, clique no botão "Selecionar arquivo PDF".
4.  Escolha o arquivo PDF do plano de contas que deseja validar.
5.  Aguarde o processamento. Uma mensagem indicará o progresso (`Processando página X/Y...`) e o resultado final (`Processamento concluído.`, `Erro fatal...`, etc.).
6.  **Resultados:**
    *   **Sucesso:** Se nenhuma inconsistência grave for encontrada, uma mensagem de sucesso será exibida.
    *   **Erros Não Fatais:** Se apenas avisos (tokens grudados) forem encontrados, você será notificado e terá a opção de visualizar os detalhes. O botão "Exportar Erros" ficará ativo.
    *   **Erro Fatal:** Se um erro estrutural grave for encontrado, a validação para, uma mensagem de erro é exibida, e o botão "Exportar Erros" fica ativo para salvar o log contendo o erro fatal.
7.  Clique em "Exportar Erros" (se habilitado) para salvar um arquivo `.txt` com o detalhamento de todos os problemas encontrados.

### 2. Executando o Script Python Diretamente

Se preferir ou precisar executar o código fonte:

1.  **Pré-requisitos:**
    *   Tenha o [Python](https://www.python.org/) instalado (versão 3.x recomendada).
    *   Instale a biblioteca `pdfplumber` necessária. Abra seu terminal ou prompt de comando e execute:
        ```bash
        pip install pdfplumber
        ```
        *(A biblioteca `tkinter` geralmente já vem incluída na instalação padrão do Python).*
2.  **Execução:**
    *   Navegue pelo terminal até a pasta onde o arquivo `validador-de-pdf.py` está localizado.
    *   Execute o script com o comando:
        ```bash
        python validador-de-pdf.py
        ```
3.  A interface gráfica será aberta. Siga os mesmos passos 3 a 7 descritos na seção "Usando o Executável".

## Construindo o Executável (Opcional)

Caso queira gerar (ou regenerar) o arquivo `.exe` a partir do código fonte:

1.  **Pré-requisitos:**
    *   Tenha o Python e o `pip` instalados.
    *   Instale o `PyInstaller`. No terminal, execute:
        ```bash
        pip install pyinstaller
        ```
2.  **Construção:**
    *   Navegue pelo terminal até a pasta raiz do projeto (onde está o arquivo `ValidadorPlanoContas.spec`).
    *   Execute o comando:
        ```bash
        pyinstaller ValidadorPlanoContas.spec
        ```
3.  Após a conclusão, o executável `ValidadorPlanoContas.exe` estará localizado dentro da pasta `dist/`.