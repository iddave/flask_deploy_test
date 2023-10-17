import json
import sqlite3

import click
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
from flask import current_app, g, flash
from model import embeddings as emb
import io


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
               database="qspro",
               user="qspro",
               password="P@ssw0rd",
               host="192.168.3.106",
               port="5432",
               options='-c client_encoding=utf8')
    return g.db


def close_db(e = None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    conn = get_db()

    with conn.cursor() as cur:
        with current_app.open_resource('commands.sql') as f:
            cur.execute(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def get_df(table='QTable'):
    conn = get_db()
    cur = conn.cursor()
    # cur.execute(f'''SELECT * FROM public."{table}" ''')

    cur.execute(f'''SELECT * FROM public."{table}"
                    UNION ALL
                    SELECT * FROM public."{table}_temp"''')

    result = cur.fetchall()

    df = pd.DataFrame(result, columns=[desc[0] for desc in cur.description])
    return df


@click.command("check-db-access")
def check_db_acccess():
    try:
        df = get_df()
        click.echo(f"Доступ есть, датафрейм(3): {df.head(3)}")
    except Exception as e:
        click.echo(f"не удалось получить таблицу: {e}")


def create_embeddings_db():
    df = get_df()
    emb_df = pd.DataFrame()
    try:
        emb_df['Question'] = df['Question']
        emb_df['Embeddings'] = df['Question'].apply(lambda x: json.dumps(emb.get_embeddings(x)))
        # print(emb_df.columns)
    except Exception as e:
        print(f"не получилось создать новый ДФ: {e}")

    # engine = create_engine(
    #     'postgresql+psycopg2://username:password@host:port/database')
    engine = create_engine("postgresql://", creator=get_db)

    # Drop old table and create new empty table
    emb_df.to_sql('QEmbeddings', engine, if_exists='replace', index=False)


@click.command('create-emb-db')
def create_emb_db():
    try:
        create_embeddings_db()
        click.echo(f"Creation successful")
    except Exception as e:
        click.echo(f"не удалось создать эмбеддинг таблицу: {e}")


def insert_into_db(question, ans="",  link=""):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f'''
                INSERT INTO public."QTable_temp" ("Question","Answer", "link")
                VALUES (%s,%s, %s) 
                ''', (question, ans,  link))
        conn.commit()

        cur.execute(f'''
                INSERT INTO public."QEmbeddings_temp" ("Question", "Embeddings")
                VALUES (%s, %s) 
                ''', (question, json.dumps(emb.get_embeddings(question))))
        conn.commit()
        flash("Запись добавлена","flash-success")
    except Exception as e:
        conn.rollback()
        flash(f"Запись не добавлена. Ошибка: {e}","flash-error")
    finally:
        cur.close()
        conn.close()


def merge_temp_tbl():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f'''
                INSERT INTO public."QTable"
                SELECT * FROM public."QTable_temp" 
                ''')
        conn.commit()

        cur.execute(f'''
                INSERT INTO public."QEmbeddings"
                SELECT * FROM public."QEmbeddings_temp" 
                ''')
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cur.close()
        conn.close()


@click.command('merge-temp-tables')
def merge_tables():
    try:
        merge_temp_tbl()
        click.echo(f"Merged successfully")
    except Exception as e:
        click.echo(f"Не удалось создать соеденить таблицы: {e}")


def clean_temp_tbl():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f'''
                TRUNCATE TABLE public."QTable_temp" 
                ''')
        conn.commit()

        cur.execute(f'''
                TRUNCATE TABLE public."QEmbeddings_temp" 
                ''')
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cur.close()
        conn.close()


@click.command('clean-temp-tables')
def clean_tables():
    try:
        clean_temp_tbl()
        click.echo(f"Cleaned successfully")
    except Exception as e:
        click.echo(f"Не удалось очистить таблицы: {e}")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_emb_db)
    app.cli.add_command(check_db_acccess)
    app.cli.add_command(merge_tables)
    app.cli.add_command(clean_tables)
