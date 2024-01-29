import logging
import time
import psycopg2
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By

from time import sleep
from tqdm import tqdm

class bot_face():
    def __init__(self, cred_login, cred_senha, headless=False):
        options = webdriver.FirefoxOptions()

        if headless: options.add_argument("-headless")

        self.driver = webdriver.Firefox(options=options)

        self.cred_login = cred_login
        self.cred_senha = cred_senha
        # print(cred_login)
        # print(cred_senha)
        sleep(3)

    def print_status(self, func):
        def wrapper(*args, **kwargs):
            print(f'Executando {func.__name__}...')
            try:
                ret = func(*args, **kwargs)
                print(f'{func.__name__} executado com sucesso!')
            
            except Exception as e:
                print(f'Erro ao executar {func.__name__}')
                raise(e)
            
            return ret
        return wrapper

    def login(self):
        try:
            print('Fazendo login no Facebook...')
            script_pass = f""" document.getElementById('pass').value='{self.cred_senha}' """
            script_username = f""" document.getElementById('email').value='{self.cred_login}' """   
            script_login = f""" document.getElementById('loginbutton').click() """
            
            self.driver.get('https://www.facebook.com/login/web/')
            self.driver.maximize_window()
            
            self.driver.execute_script(script_username)
            self.driver.execute_script(script_pass)
            self.driver.execute_script(script_login)
            sleep(5)

            return 'Login feito com sucesso'

        except Exception as e:
            print('Erro no login')
            return 'Erro no login'

    def search_keyword(self, keyword):
        try:
            if not (self.check_page('https://www.facebook.com/?sk=welcome') or self.check_page('https://www.facebook.com/')):
                raise Exception('Não foi possível fazer login no Facebook.')

            print(f'Pesquisando por: {keyword}...')
            sleep(4)
            self.driver.get('https://www.facebook.com/search/posts?q='+keyword)

            self.check_criminal_question()


            if not self.check_page('https://www.facebook.com/search/posts?q='+keyword):
                raise Exception('Não foi possível fazer a pesquisa no Facebook.')
            
        except Exception as e:
            print('Erro na pesquisa')
            raise(e)

    def get_post_links(self, n_posts=20):
        try:
            print('Obtendo links dos posts...')
            self.post_links = list()
            sleep(10)
            n_scroll = 0

            while True:
                script_n_posts = f""" 
                                    var n_posts = document.getElementsByClassName('x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z').length
                                    return n_posts
                                """
                
                n_posts_browser = self.driver.execute_script(script_n_posts)

                if n_posts_browser >= n_posts:
                    n_posts_browser = n_posts
                    print(f"foram encontrados o total de {n_posts_browser} posts de {n_posts}")
                    break

                elif n_scroll > 50:
                    print(f"foram encontrados o total de {n_posts_browser} posts de {n_posts}")
                    
                    break

                else:
                    n_scroll += 1
                    self.driver.execute_script("window.scrollBy(0,6150)")
                    sleep(1)

            if n_posts_browser == 0:
                print('Nenhum post encontrado')
                raise Exception('Nenhum post encontrado')

            # self.driver.execute_script("window.scrollBy(0,6150)")

            script = f""" 
                        var results = document.getElementsByClassName('x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm')
                        return results
                    """
            
            elements = self.driver.execute_script(script)
            elements = elements[:n_posts_browser]
            
            self.driver.execute_script("window.scrollBy(0,-"+ str(n_scroll*6150) +")")


            for element in tqdm(elements):
                try:
                    href = element.get_attribute('href')
                    if '#' in href:
                        element.click()
                        href = element.get_attribute('href')
                    else: pass
                    
                except:
                    self.driver.execute_script("window.scrollBy(0,1150)")
                    sleep(1)
                    element.click()
                    sleep(1)
                    href = element.get_attribute('href')

                if href not in self.post_links:
                    self.post_links.append(href)

                if len(self.post_links) == n_posts:
                    break

            print('numero de post_links: ', len(self.post_links))

        except Exception as e:
            print('Erro ao obter links dos posts')
            raise(e)
        
    def get_data(self):
        return self.data
    
    def get_information(self):
        try:
            print('Tirando screenshots...')

            info = list()

            for i,link in enumerate(tqdm(self.post_links)):
                self.driver.get(link)
                sleep(2)
                self.driver.save_screenshot('imgs/'+str(i)+'.png')

                info.append([link, link])

            self.data = pd.DataFrame(info, columns=['link', 'publication_id'])
        
        except Exception as e:
            print('Erro ao tirar screenshots')
            raise(e)

    def check_page(self, page: str):
        url_atual = self.driver.current_url
        page = page.replace(' ', '%20')

        if url_atual == page:
            return True
        
        else:
            print(f'url atual: {url_atual}, url esperada: {page}')
            self.driver.save_screenshot('imgs/error_screenshot.png')

            return False

    def check_criminal_question(self):
        try:
            xpath_question = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div/div/div/div/div/div/div[3]/a/div'
            xpath_question_continue = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[3]/div[1]/a/span'

            try:
                element = self.driver.find_element(by=By.XPATH, value=xpath_question)
                question = True

            except:
                question = False

            print('Verificando se há pergunta criminal...')

            if question:
                print('Pergunta encontrada!')
                element.click()
                sleep(2)
                self.driver.find_element(by=By.XPATH, value=xpath_question_continue).click()
                sleep(2)
                
        except Exception as e:
            print(f'Erro ao verificar se há pergunta criminal: {e}')
            raise(e)

    def result_is_empty(self):
        pass


def execute_sql(sql, data = None, fetch=False):
    try:
        con = conecta_db()
        cursor = con.cursor()

        if fetch:
            cursor.execute(sql)
            rows = cursor.fetchall()
            con.commit()
            cursor.close()
            con.close()

            return rows
        
        cursor.execute(sql, data)
        con.commit()

        cursor.close()
        con.close()

    except (Exception, psycopg2.DatabaseError) as error:
                    print("Error: %s" % error)
                    con.rollback()
                    cursor.close()
                    con.close()
                    raise(error)

def conecta_db():
    con = psycopg2.connect(host='db.infoverse.com.br', 
                            database='infoverse',
                            user='infoverse', 
                            password='fMCTSepyEXpH')
    return con
        
def retorna_pesquisa_avulsa():
    sql = """SELECT id, id_usuario, id_credencial, data_pesquisa, rede_social, status, palavra_chave, filtro, filtro_avancado, ano_referencia, publicacoes_de, localizacao_marcada
            FROM pesquisa_avulsa
            WHERE status IS NULL OR status = False;"""
    
    rows = execute_sql(sql, fetch=True)

    return rows
    
def set_status_pesquisa_avulsa(id):
    sql = """UPDATE pesquisa_avulsa
            SET status=true
            WHERE id ="""+ str(id) +""";"""
    
    execute_sql(sql)

def retorna_credencial(credencial_id):
    sql = """SELECT id, descricao, usuario, senha
    FROM bot_credencial_facebook WHERE id ="""+ str(credencial_id) +""";"""

    row = execute_sql(sql, fetch=True)

    return row
    
def verificando_busca_avulsa():
    rows = retorna_pesquisa_avulsa()

    for row in rows:
        id, id_usuario, id_credencial, date_search, rede_social, status, keyword, filtro, filtro_avancado, ano_referencia, publicacoes_de, localizacao_marcada = row
        keyword = retira_acento(keyword)

        row2 = retorna_credencial(id_credencial)
        _, _, cred_usuario, cred_senha = row2[0]

        status = executar_busca(id, cred_usuario, cred_senha, keyword)
        # print('status: ', status)
        set_status_pesquisa_avulsa(id)

def executar_busca(id, cred_login, cred_senha, keyword):
    print('executando busca...')
    try:
        bot = bot_face(cred_login, cred_senha, headless=True)
        bot.login()

        sleep(5)

        bot.search_keyword(keyword)
        bot.get_post_links()
        bot.get_information()

        inserir_db(bot.get_data(), id)

    except Exception as e:
        pass
       
def inserir_db(data, id):
    print('Inserindo no banco de dados...')

    for i,link in enumerate(tqdm(data['link'])):
        try:
            publication_id = link
            publication_id = remove_especial_char(publication_id)

            sql = """
            INSERT into contigencia (link_publication, publication_id, id_pesquisa_avulsa) 
            values('%s','%s', '%s');
            """ % (data['link'][i], publication_id, id)

            linhas = execute_sql("""SELECT publication_id FROM contigencia WHERE publication_id = '"""+ str(publication_id) +"""';""", fetch=True)
            
            # Conte o número de linhas retornadas
            numero_de_linhas = len(linhas)

            if numero_de_linhas == 0:
                execute_sql(sql)

                with open('imgs/'+str(i)+'.png', 'rb') as file:
                    imagem_bytes = file.read()


                data_img = (publication_id, psycopg2.Binary(imagem_bytes))

                sql2 = """
                        INSERT INTO pesquisa_screenshot (publication_id, bytea) 
                        VALUES (%s, %s);
                        """
                execute_sql(sql2, data_img)

        except Exception as e:
            print('Erro na insersão de dados')
            raise(e)

    print('Inserido com sucesso!')

def remove_especial_char(string):
    string = string.replace('(', '')
    string = string.replace(')', '')
    string = string.replace('/', '')
    string = string.replace('.', '')
    string = string.replace('-', '')
    string = string.replace(',', '')
    string = string.replace(':', '')
    string = string.replace('!', '')
    string = string.replace('?', '')
    string = string.replace('#', '')
    string = string.replace('%', '')
    string = string.replace('&', '')
    string = string.replace('=', '')
    string = string.replace('[', '')
    string = string.replace(']', '')
    
    return string

def retira_acento(string):
    string = string.replace('á', 'a')
    string = string.replace('à', 'a')
    string = string.replace('ã', 'a')
    string = string.replace('â', 'a')
    string = string.replace('é', 'e')
    string = string.replace('ê', 'e')
    string = string.replace('í', 'i')
    string = string.replace('ó', 'o')
    string = string.replace('ô', 'o')
    string = string.replace('õ', 'o')
    string = string.replace('ú', 'u')
    string = string.replace('ü', 'u')
    string = string.replace('ç', 'c')
    string = string.replace('Á', 'A')
    string = string.replace('À', 'A')
    string = string.replace('Ã', 'A')
    string = string.replace('Â', 'A')
    string = string.replace('É', 'E')
    string = string.replace('Ê', 'E')
    string = string.replace('Í', 'I')
    string = string.replace('Ó', 'O')
    string = string.replace('Ô', 'O')
    string = string.replace('Õ', 'O')
    string = string.replace('Ú', 'U')
    string = string.replace('Ü', 'U')
    string = string.replace('Ç', 'C')

    return string


if __name__ == '__main__':
    global precessando 
    processando = False
    print('Verificando busca avulsa')
    
    while True:
        time.sleep(10)
        verificando_busca_avulsa()


