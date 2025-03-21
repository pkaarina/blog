## Blog

Um blog desenvolvido com Flask, permitindo a criação de contas, login, postagem de artigos, adição de comentários e categorização dos posts. Utiliza PostgreSQL como banco de dados.

## 📌 Tecnologias Utilizadas

🐍 Python

🌐 Flask

🗄️ PostgreSQL

🏗️ SQLAlchemy

🎨 Jinja2 (Templates)

💄 Bootstrap (para estilização)

## ✨ Funcionalidades

✅ Criar conta e logar no sistema;

✅ Criar, editar e deletar posts;

✅ Comentar em posts;

✅ Categorizar posts.

## 🚀 Instalação

Clone este repositório:

```bash
git clone https://github.com/pkaarina/blog.git
cd blog
```

Crie um ambiente virtual e ative:

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate  

# Windows
venv\Scripts\activate 
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Configure o banco de dados PostgreSQL e defina a variável de ambiente:

```bash
export DATABASE_URL="postgresql://usuario:senha@localhost:5432/nome_do_banco"
```

Execute as migrações do banco de dados:

```bash
flask db upgrade
```

Inicie o servidor:

```bash
flask run
```

## 🌍 Uso

Acesse http://127.0.0.1:5000/ no navegador para começar a usar o blog.

## 🤝 Contribuição

Sinta-se à vontade para contribuir com o projeto! Basta abrir um pull request ou relatar um problema na seção de "Issues".


🚀 