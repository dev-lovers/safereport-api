# 🛡️ SafeReport - Backend

Este é o **backend** do projeto **SafeReport**, desenvolvido em **FastAPI**.  
O SafeReport é um aplicativo mobile que permite:

- 📍 Visualizar ocorrências criminais em tempo real
- 📲 Enviar denúncias via **Sinesp**
- 🗺️ Traçar rotas e exibir no mapa as ocorrências ao longo do percurso
- 🤖 Gerar **insights com IA** a partir dos dados coletados

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:

- [Python 3.10+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/) (gerenciador de pacotes do Python)
- [virtualenv](https://virtualenv.pypa.io/) (opcional, mas recomendado)

---

## ⚙️ Configuração do ambiente

Clone este repositório:

```bash
git clone https://github.com/dev-lovers/safereport-be.git
cd safereport-be
```

Crie e ative um ambiente virtual:

```bash
python -m venv venv
# Ativar no Linux/Mac
source venv/bin/activate
# Ativar no Windows
venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -e .
```

---

## ▶️ Rodando o projeto

Para iniciar a aplicação localmente:

```bash
uvicorn app.main:app --reload
```

- `app.main:app` → ajuste para o caminho do seu arquivo principal.
- A flag `--reload` reinicia automaticamente o servidor a cada alteração no código.

O servidor estará disponível em:  
👉 http://127.0.0.1:8000

---

## 📑 Documentação automática

O FastAPI já gera documentação interativa:

- Swagger UI: http://127.0.0.1:8000/docs
- Redoc: http://127.0.0.1:8000/redoc

---

## 🛠️ Comandos úteis

Rodar testes (se configurados):

```bash
pytest
```

Atualizar dependências:

```bash
pip freeze > requirements.txt
```

---

## 📱 Arquitetura geral

- **Frontend (Mobile):** Aplicativo SafeReport (Flutter/React Native)
- **Backend (este repositório):** FastAPI + Banco de Dados
- **Integrações externas:** Sinesp, mapas, APIs de geolocalização
- **IA/Insights:** Módulos para análise e extração de padrões a partir das ocorrências

---

## 📜 Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo `LICENSE` para mais informações.
