import pdfplumber
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
# Custom exception for fatal validation errors
class FatalValidationError(Exception):
    pass

# Global variables to store results
g_non_fatal_errors = []
g_fatal_error_message = None


def validar_linha(linha):
    """
    Valida a linha de acordo com as regras:
      - Deve ter no mínimo 5 tokens.
      - Token1 (código): deve ser um número (várias sequências de dígitos separadas por pontos são permitidas)
      - Token2 (classificação): mesmo formato que o código
      - Token3: flag (não validada)
      - Descrição: composta por todos os tokens do token4 até o penúltimo;
          * deve conter pelo menos uma letra;
          * não deve conter tokens suspeitos de terem sido "grudados" (por exemplo, contendo uma mistura de letras e dígitos com tamanho elevado).
      - Último token: não é validado.
    Retorna (True, "") se válida ou (False, mensagem_de_erro) se inválida.
    """
    tokens = linha.split() # Divide a linha em tokens
    # Verifica se a linha tem o número mínimo de tokens
    if len(tokens) < 5:
        return False, "Número incorreto de tokens (esperado no mínimo 5 tokens)"
    
    codigo = tokens[0]
    classificacao = tokens[1]
    description_tokens = tokens[3:-1]  # Descrição vai do 4º token até o penúltimo

    if not description_tokens:
        return False, "Descrição ausente (deve conter pelo menos um token com letra)"
    
    description = " ".join(description_tokens)

    if not re.fullmatch(r'\d+(?:\.\d+)*', codigo):
        return False, "Código inválido (deve ser um número, podendo conter várias sequências separadas por pontos)"
    
    if not re.fullmatch(r'\d+(?:\.\d+)*', classificacao):
        return False, "Classificação inválida (deve ser um número, podendo conter várias sequências separadas por pontos)"
    
    if not re.search(r'[A-Za-z]', description):
        return False, "Descrição inválida (deve conter pelo menos uma letra)"
    
    for token in description_tokens:
        if re.fullmatch(r'[A-Za-z0-9]+', token) and re.search(r'[A-Za-z]', token) and re.search(r'\d', token) and len(token) > 8:
            return False, f"Descrição possivelmente contém informação grudada (token suspeito: '{token}')"
    
    return True, ""

def verificar_pdf(nome_arquivo, progress_label):
    global g_non_fatal_errors, g_fatal_error_message
    g_non_fatal_errors = [] # Reset errors for this run
    g_fatal_error_message = None # Reset fatal error for this run
    linha_global = 0
    try:
        with pdfplumber.open(nome_arquivo) as pdf:
            total_paginas = len(pdf.pages)
            for num_pagina, pagina in enumerate(pdf.pages, start=1):
                progress_label.config(text=f"Processando página {num_pagina}/{total_paginas}...")
                root.update_idletasks()

                texto = pagina.extract_text()
                if not texto:
                    continue
                for linha in texto.split('\n'):
                    linha_global += 1
                    linha = linha.strip()
                    if not linha or not linha[0].isdigit():
                        continue
                    valida, motivo = validar_linha(linha)
                    if not valida:
                        if motivo.startswith("Descrição possivelmente contém informação grudada"):
                            g_non_fatal_errors.append({ # Store in global list
                                "pagina": num_pagina,
                                "linha_global": linha_global,
                                "conteudo": linha,
                                "motivo": motivo
                            })
                        else:
                            error_message = (f"Erro fatal de validação na Página {num_pagina}, Linha {linha_global}:\n"
                                             f"Conteúdo: {linha}\n"
                                             f"Motivo: {motivo}")
                            raise FatalValidationError(error_message) # Raise fatal error
        progress_label.config(text="Processamento concluído.")
        return "success" if not g_non_fatal_errors else "non_fatal_errors" # Return status
    except FatalValidationError as fve:
        g_fatal_error_message = str(fve) # Store fatal error message
        messagebox.showerror("Erro Fatal de Validação", g_fatal_error_message)
        progress_label.config(text="Processamento interrompido por erro fatal.")
        return "fatal_error" # Return status
    except Exception as e:
        g_fatal_error_message = f"Erro inesperado ao processar o PDF:\n{str(e)}" # Store unexpected error
        messagebox.showerror("Erro Inesperado", g_fatal_error_message)
        progress_label.config(text="Processamento interrompido por erro inesperado.")
        return "fatal_error" # Return status (treat as fatal for export)

def show_error_details(erros_list): # Renamed param for clarity
    window = tk.Toplevel()
    window.title("Detalhes dos Erros Não Fatais")
    window.geometry("600x400")

    st = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Helvetica", 10))
    st.pack(expand=True, fill=tk.BOTH)

    st.insert(tk.END, "Foram encontrados os seguintes erros não fatais (tokens 'grudados'):\n\n")
    for erro in erros_list:
        # Improved formatting
        info = (f"[ERRO NÃO FATAL]\n"
                f"  Página: {erro['pagina']}\n"
                f"  Linha Aprox. no PDF: {erro['linha_global']}\n"
                f"  Conteúdo: {erro['conteudo']}\n"
                f"  Motivo: {erro['motivo']}\n\n")
        st.insert(tk.END, info)

    st.configure(state='disabled')
    # Removed the save button from here

def salvar_erros(non_fatal_errors, fatal_error_message):
    if not non_fatal_errors and not fatal_error_message:
        messagebox.showwarning("Exportar Erros", "Não há erros registrados para exportar.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Arquivo de Texto", "*.txt"), ("Todos os Arquivos", "*.*")],
        title="Salvar Log de Erros",
        initialfile="erros_validacao.txt" # Suggest default name
    )
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write("Log de Erros da Validação do PDF\n")
                file.write("="*40 + "\n\n")

                if fatal_error_message:
                    file.write("[ERRO FATAL ENCONTRADO]\n")
                    file.write("-" * 25 + "\n")
                    file.write(f"{fatal_error_message}\n\n")
                    file.write("O processamento foi interrompido devido a este erro.\n")
                    file.write("Pode haver outros erros não fatais listados abaixo que ocorreram antes do erro fatal.\n\n")

                if non_fatal_errors:
                    file.write(f"[ERROS NÃO FATAIS (Tokens Grudados) - {len(non_fatal_errors)} encontrados]\n")
                    file.write("-" * 45 + "\n\n")
                    for erro in non_fatal_errors:
                        file.write(f"Página: {erro['pagina']}, Linha Aprox.: {erro['linha_global']}\n")
                        file.write(f"  Conteúdo: {erro['conteudo']}\n")
                        file.write(f"  Motivo: {erro['motivo']}\n\n")
                elif not fatal_error_message: # Only say this if no fatal error either
                     file.write("Nenhum erro não fatal (token grudado) foi encontrado.\n")


            messagebox.showinfo("Sucesso", f"Log de erros salvo com sucesso em:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo de log:\n{str(e)}")

def selecionar_arquivo():
    global g_non_fatal_errors, g_fatal_error_message # Ensure access
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    if file_path:
        # Reset errors before processing
        g_non_fatal_errors = []
        g_fatal_error_message = None
        btn_export.config(state=tk.DISABLED) # Disable export button initially

        status = verificar_pdf(file_path, progress_label)

        if status == "fatal_error":
            # Fatal error occurred, enable export
            btn_export.config(state=tk.NORMAL)
        elif status == "non_fatal_errors":
            # Non-fatal errors found, enable export and ask to view
            btn_export.config(state=tk.NORMAL)
            resposta = messagebox.askyesno("Erros Não Fatais Encontrados",
                                           f"Foram encontrados {len(g_non_fatal_errors)} erros não fatais (tokens grudados).\nDeseja ver os detalhes?")
            if resposta:
                show_error_details(g_non_fatal_errors) # Pass the global list
        elif status == "success":
            # No errors found
             messagebox.showinfo("Sucesso",
                                 "Todas as linhas válidas ou ignoradas foram processadas sem erros fatais ou não fatais reportáveis.")
             # Keep export button disabled as there's nothing to export
# Add Export Button command function (before root.mainloop)
def exportar_erros_registrados():
    # This function will call the modified salvar_erros
    salvar_erros(g_non_fatal_errors, g_fatal_error_message)


# Interface gráfica
root = tk.Tk()
root.title("Validador de Plano de Contas")
root.geometry("400x300") # Increased height slightly for new button

btn_select = tk.Button(root, text="Selecionar arquivo PDF", command=selecionar_arquivo, font=("Helvetica", 12))
btn_select.pack(pady=10)

progress_label = tk.Label(root, text="Aguardando arquivo...", font=("Helvetica", 10))
progress_label.pack(pady=5)

btn_export = tk.Button(root, text="Exportar Erros", command=exportar_erros_registrados, font=("Helvetica", 10), state=tk.DISABLED)
btn_export.pack(pady=10)

root.mainloop()