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


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def update_record(data):
    conn = get_db()
    cur = conn.cursor()
    print(
        f'''question: {data['question']}, answer: {data['answer']}, link: {data['link']}, id: {data['id']},
         orig_question: {data['orig_question']}, orig_answer: {data['orig_answer']},
                 data['orig_link']'''
    )
    cur.execute(f'''UPDATE public."QTable" 
                        SET "Question"=%s, "Answer"=%s, "link"=%s
                        WHERE id=%s AND "Question"=%s AND "Answer"=%s AND "link"=%s''',
                (data['question'], data['answer'], data['link'], data['id'], data['orig_question'], data['orig_answer'],
                 data['orig_link']))
    conn.commit()
    cur.execute(f'''UPDATE public."QTable_temp" 
                        SET "Question"=%s, "Answer"=%s, "link"=%s
                        WHERE id=%s AND "Question"=%s AND "Answer"=%s AND "link"=%s''',
                (data['question'], data['answer'], data['link'], data['id'], data['orig_question'], data['orig_answer'],
                 data['orig_link']))
    conn.commit()


    cur.execute(f'''
                UPDATE public."QEmbeddings"
                SET "Question" = %s, "Embeddings"= %s
                WHERE  "Question" = %s
                ''', (data['question'], json.dumps(emb.get_embeddings(data['question'])), data['orig_question']))
    conn.commit()
    cur.execute(f'''
                UPDATE public."QEmbeddings_temp"
                SET "Question" = %s, "Embeddings"= %s
                WHERE  "Question" = %s
                ''', (data['question'], json.dumps(emb.get_embeddings(data['question'])), data['orig_question']))
    conn.commit()




def delete_data(Qtable, QEmbeddings, data):
    conn = get_db()
    cur = conn.cursor()

     # Delete record from main table
    cur.execute(f'''DELETE FROM public."{Qtable}" 
    WHERE id=%s AND "Question"=%s AND "Answer"=%s AND "link"=%s''',
                (data['id'], data['orig_question'], data['orig_answer'], data['orig_link']))
    conn.commit()

    # Delete record from temp table
    cur.execute(f'''DELETE FROM public."{QEmbeddings}" 
    WHERE "Question" = %s''', (data['orig_question'],))
    conn.commit()


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
    print(df)
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


def insert_into_db(question, ans="", link=""):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f'''
                INSERT INTO public."QTable_temp" ("Question","Answer", "link")
                VALUES (%s,%s, %s) 
                ''', (question, ans, link))
        conn.commit()

        cur.execute(f'''
                INSERT INTO public."QEmbeddings_temp" ("Question", "Embeddings")
                VALUES (%s, %s) 
                ''', (question, json.dumps(emb.get_embeddings(question))))
        conn.commit()
        flash("Запись добавлена", "flash-success")
    except Exception as e:
        conn.rollback()
        flash(f"Запись не добавлена. Ошибка: {e}", "flash-error")
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
    app.cli.add_command(create_emb_db) #create-emb-db
    app.cli.add_command(check_db_acccess) #check-db-access
    app.cli.add_command(merge_tables) #merge-temp-tables
    app.cli.add_command(clean_tables) #clean-temp-tables
