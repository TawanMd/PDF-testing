import pdfplumber
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

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
    tokens = linha.split()
    if len(tokens) < 5:
        return False, "Número incorreto de tokens (esperado no mínimo 5 tokens)"
    
    code = tokens[0]
    classification = tokens[1]
    description_tokens = tokens[3:-1]  # Descrição vai do 4º token até o penúltimo

    if not description_tokens:
        return False, "Descrição ausente (deve conter pelo menos um token com letra)"
    
    description = " ".join(description_tokens)

    if not re.fullmatch(r'\d+(?:\.\d+)*', code):
        return False, "Código inválido (deve ser um número, podendo conter várias sequências separadas por pontos)"
    
    if not re.fullmatch(r'\d+(?:\.\d+)*', classification):
        return False, "Classificação inválida (deve ser um número, podendo conter várias sequências separadas por pontos)"
    
    if not re.search(r'[A-Za-z]', description):
        return False, "Descrição inválida (deve conter pelo menos uma letra)"
    
    for token in description_tokens:
        if re.fullmatch(r'[A-Za-z0-9]+', token) and re.search(r'[A-Za-z]', token) and re.search(r'\d', token) and len(token) > 8:
            return False, f"Descrição possivelmente contém informação grudada (token suspeito: '{token}')"
    
    return True, ""

def verificar_pdf(nome_arquivo, progress_label):
    erros = []
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
                        erros.append({
                            "pagina": num_pagina,
                            "linha_global": linha_global,
                            "conteudo": linha,
                            "motivo": motivo
                        })
        progress_label.config(text="Processamento concluído.")
        return erros
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao ler o PDF:\n{str(e)}")
        return None

def show_error_details(erros):
    window = tk.Toplevel()
    window.title("Detalhes dos Erros")
    window.geometry("600x400")

    st = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Helvetica", 10))
    st.pack(expand=True, fill=tk.BOTH)

    st.insert(tk.END, "Foram encontrados os seguintes erros:\n\n")
    for erro in erros:
        info = (f"Página {erro['pagina']}, Linha {erro['linha_global']}: {erro['conteudo']}\n"
                f" Motivo: {erro['motivo']}\n\n")
        st.insert(tk.END, info)

    st.configure(state='disabled')

    # Botão para salvar log
    btn_save = tk.Button(window, text="Salvar Log de Erros", command=lambda: salvar_erros(erros), font=("Helvetica", 10))
    btn_save.pack(pady=5)

def salvar_erros(erros):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Arquivo de Texto", "*.txt")],
        title="Salvar Log de Erros"
    )
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("Erros encontrados na análise do PDF:\n\n")
            for erro in erros:
                file.write(f"Página {erro['pagina']}, Linha {erro['linha_global']}: {erro['conteudo']}\n")
                file.write(f"Motivo: {erro['motivo']}\n\n")
        messagebox.showinfo("Sucesso", "Log de erros salvo com sucesso.")

def selecionar_arquivo():
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    if file_path:
        erros = verificar_pdf(file_path, progress_label)
        if erros is not None:
            if erros:
                resposta = messagebox.askyesno("Erros encontrados",
                                               "Foram encontrados erros em algumas linhas.\nDeseja ver os detalhes?")
                if resposta:
                    show_error_details(erros)
            else:
                messagebox.showinfo("Sucesso",
                                    "Todas as linhas possuem código e descrição conforme o esperado.")

# Interface gráfica
root = tk.Tk()
root.title("Validador de Plano de Contas")
root.geometry("400x250")

btn = tk.Button(root, text="Selecionar arquivo PDF", command=selecionar_arquivo, font=("Helvetica", 12))
btn.pack(expand=True, pady=10)

progress_label = tk.Label(root, text="Aguardando arquivo...", font=("Helvetica", 10))
progress_label.pack()

root.mainloop()