from pathlib import Path
import subprocess
import re
import csv
import os

# Pasta atual
pasta = Path(".")

# Arquivo de controle
arquivo_jobs = pasta / "jobs.csv"

# Pasta para guardar logs de submissao
pasta_logs = pasta / "logs_submit"
pasta_logs.mkdir(exist_ok=True)

# Carrega jobs ja submetidos, se jobs.csv existir
jobs_existentes = {}

if arquivo_jobs.exists():

    with open(str(arquivo_jobs), "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs_existentes[row["JOB"]] = row["SLURM_JOBID"]

# Descobrir os *INCLUDES
def get_included_files(inp_files):

    included_files = set()

    include_regex = re.compile(
        r"\*INCLUDE\s*,\s*INPUT\s*=\s*(.+)",
        re.IGNORECASE
    )

    for inp in inp_files:

        with open(str(inp), "r", errors="ignore") as f:

            for line in f:

                match = include_regex.search(line)

                if match:

                    included_name = match.group(1).strip()

                    included_files.add(
                        os.path.basename(included_name)
                    )

    return included_files

def has_step(inp_file):

    try:
        with open(str(inp_file), "r", errors="ignore") as f:

            for line in f:
                if line.strip().upper().startswith("*STEP"):
                    return True

        return False

    except Exception as e:
        print("Erro ao ler {} : {}".format(inp_file, e))
        return False


all_inps = sorted(pasta.glob("*.inp"))

included_files = get_included_files(all_inps)

loadcases = []

for inp in all_inps:

    if inp.name in included_files:
        continue

    if has_step(inp):
        loadcases.append(inp)

relatorio = []

print("Loadcases encontrados:")

for inp in loadcases:
    print(" - {}".format(inp.name))

print("\nIniciando submissao...\n")

for inp in loadcases:

    job = inp.stem

    # Evita submeter de novo se ja estiver no jobs.csv
    if job in jobs_existentes:

        print("{} ja consta no jobs.csv. Pulando submissao.".format(job))

        relatorio.append([
            job,
            jobs_existentes[job],
            "JA_EXISTIA"
        ])

        continue

    print("submetendo {}".format(inp.name))

    comando = """
/cae/sbt/submit_slurm_prod/submit.py abaqus \
-v 2019 \
-perm open \
-server MY_HPC_SERVER \
-dept MY_DEPT \
-userpgm USER_ID \
-i {}
""".format(inp.name)

    p = subprocess.Popen(
        comando,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    saida, _ = p.communicate("0\n")

    # Salva log completo da submissao
    log_file= pasta_logs / "{}_submit.log".format(job)

    with open(str(log_file), "w") as f:
        f.write(saida)

    match = re.search(
        r"SLURM_JOBID\s*=\s*(\d+)",
        saida
    )

    if match:

        jobid = match.group(1)

        print("{} -> SLURM {}".format(job, jobid))

        relatorio.append([
            job,
            jobid,             "SUBMETIDO"
        ])
    else:

        print("{} -> ERRO: SLURM_JOBID nao encontrado".format(job))

        relatorio.append([
            job,
            "",
            "ERRO_SUBMISSAO"
        ])

# Regrava jobs.csv atualizado
with open(str(arquivo_jobs), "w") as f:

    writer = csv.writer(f) 
    writer.writerow([
        "JOB",
        "SLURM_JOBID",
        "STATUS_SUBMISSAO"
    ])

    writer.writerows(relatorio)

print("\nArquivo jobs.csv atualizado.")
print("Logs salvos em: logs_submit/")