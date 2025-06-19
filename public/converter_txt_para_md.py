import re

def format_line(line):
    line = line.strip()
    if not line:
        return ""

    # Remove rodapés e cabeçalhos específicos
    if "Diretoria Parlamentar / Secretaria Adjunta de Consolidação de Legislação" in line or \
       "Diretoria Parlamentar / Secretaria de Consolidação de Legislação" in line:
        return ""
    # Remove linhas que contêm apenas números (número da página)
    if re.match(r"^\d+\s*$", line):
        return ""
    # Remove o caractere de quebra de página
    if line == "\x0c":
        return ""

    return line

def txt_to_markdown(input_path, output_path):
    try:
        with open(input_path, 'r', encoding='utf-8') as f_in:
            lines = f_in.readlines()

        markdown_content = []
        current_block = []

        for line in lines:
            processed_line = format_line(line)
            
            if not processed_line: # Linha vazia ou removida
                if current_block: # Se há conteúdo no bloco atual, adicione-o ao markdown
                    markdown_content.append(" ".join(current_block).strip())
                    current_block = []
                markdown_content.append("") # Adiciona uma linha vazia para separar blocos
                continue

            # Detecta início de novos blocos (títulos, artigos, incisos, parágrafos especiais)
            is_new_block_start = False
            if processed_line.startswith("CAPÍTULO") or processed_line.startswith("Seção"):
                if current_block:
                    markdown_content.append(" ".join(current_block).strip())
                    current_block = []
                markdown_content.append(f"\n## {processed_line}\n")
                is_new_block_start = True
            elif re.match(r"^Art\. \d+º", processed_line):
                if current_block:
                    markdown_content.append(" ".join(current_block).strip())
                    current_block = []
                markdown_content.append(f"\n### {processed_line}\n")
                is_new_block_start = True
            elif re.match(r"^[IVXLCDM]+ –", processed_line) or re.match(r"^[a-z]\) ", processed_line):
                if current_block:
                    markdown_content.append(" ".join(current_block).strip())
                    current_block = []
                markdown_content.append(f"- {processed_line}")
                is_new_block_start = True
            elif processed_line.startswith("Parágrafo único.") or re.match(r"^§ \d+º", processed_line):
                if current_block:
                    markdown_content.append(" ".join(current_block).strip())
                    current_block = []
                markdown_content.append(f"\n**{processed_line}**\n")
                is_new_block_start = True
            
            if not is_new_block_start:
                current_block.append(processed_line)
        
        # Adicionar o último bloco, se houver
        if current_block:
            markdown_content.append(" ".join(current_block).strip())

        final_content = "\n".join(markdown_content)
        # Limpeza final de múltiplas quebras de linha
        final_content = re.sub(r'\n{3,}', '\n\n', final_content)

        with open(output_path, 'w', encoding='utf-8') as f_out:
            f_out.write(final_content)
        print(f"Arquivo Markdown gerado: {output_path}")

    except FileNotFoundError:
        print(f"Erro: Arquivo de entrada não encontrado em {input_path}")
    except Exception as e:
        print(f"Ocorreu um erro durante a conversão: {e}")

# Lista de arquivos para converter
files_to_convert = [
    "Resolução1771-SecretariadePolíciaLegislativa",
    "Resoluçãonº1.007",
    "RESOLUÇÃONº1.073",
    "RegimentoInternoAlego-RESOLUÇÃON°1.218"
]

input_dir = "/home/ubuntu/upload/"
output_dir = "/home/ubuntu/markdown_output/"

import os
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for file_name in files_to_convert:
    txt_input_path = os.path.join(input_dir, file_name + ".txt")
    md_output_path = os.path.join(output_dir, file_name + ".md")
    print(f"Convertendo {txt_input_path} para {md_output_path}...")
    txt_to_markdown(txt_input_path, md_output_path)

print("Conversão de todos os arquivos concluída.")


