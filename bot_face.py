from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
from time import sleep
import logging
import time
import psycopg2


class bot_face():
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.actions = ActionChains(self.driver)
        sleep(3)

    def remover_letra(self, string, letra_retirar):
        nova_string = ""
        for letra in string:
            if letra != letra_retirar:
                nova_string += letra
        return nova_string

    def time_out(void=None, time_out: int = 20, raise_exception: bool = True):


        """Executes a function with a timeout limit.

        :param void: (optional) Default argument, unused.
        :type void: any
        :param time_out: The timeout limit in seconds.
        :type time_out: int
        :param raise_exception: (optional) If True, a TimeoutException will be raised when the timeout is reached.
        :type raise_exception: bool
        :return: Returns the result of the executed function.
        :rtype: any

        Example:
            This decorator can be used to set a timeout limit for a function that takes too long to execute.
            >>>@time_out(time_out=30, raise_exception=True)
            >>>def slow_function():
            >>>    time.sleep(35)
            >>>
            >>>slow_function()
            TimeoutException: Timeout!"""
    

        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                # print("Time out value: {}".format(time_out))
                contadortime_out = 0
                ret = False
                error = None
                while contadortime_out < time_out:
                    try:
                        ret = func(*args, **kwargs)
                        break
                    except Exception as e:
                        logging.exception(e) # serve para salvar o erro no log
                        error = e
                        time.sleep(1)
                    contadortime_out += 1
                if contadortime_out >= time_out and raise_exception:
                    raise error
                return ret

            return inner_wrapper

        return wrapper

    def login_facebook(self):
        script_pass = f"""
                    document.getElementById('pass').value='{self.cred_senha}'
                    """

        script_username = f"""
                            document.getElementById('email').value='{self.cred_usuario}'
                            """   

        script_login = f"""
                            document.getElementById('loginbutton').click()
                        """
        
        self.driver.get('https://www.facebook.com/login/web/')
        self.driver.maximize_window()
        


        self.driver.execute_script(script_username)

        self.driver.execute_script(script_pass)

        self.driver.execute_script(script_login)

        self.driver.implicitly_wait(10)

    @time_out(time_out=10, raise_exception=True)
    def search_keyword(self):
        sleep(4)
        self.driver.get('https://www.facebook.com/search/posts?q='+self.keyword)

    @time_out(time_out=10, raise_exception=False)
    def getting_information(self, n_posts=20):
        """
        Informações importantes para o desenvolvimento do código:
        class do usuario do post, tempo de publicação ou anuncio: x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1nxh6w3 x1sibtaa xo1l8bm xi81zsa x1yc453h
        """

        self.post_links = list()
        sleep(10)
        n_scroll = 0

        while True:
            script_n_posts = f""" 
                                var n_posts = document.getElementsByClassName('x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z').length
                                return n_posts
                              """
            
            n_posts_browser = self.driver.execute_script(script_n_posts)
            print('n_posts_browser: ', n_posts_browser)

            if n_posts_browser >= n_posts:
                break

            elif n_scroll > 50:
                print(f"foram encontrados o total de {n_posts_browser} posts de {n_posts}")
                break

            else:
                n_scroll += 1
                self.driver.execute_script("window.scrollBy(0,6150)")
                sleep(1)

        print('n_scroll: ', n_scroll)

        self.driver.execute_script("window.scrollBy(0,6150)")

        script = f""" 
                    var results = document.getElementsByClassName('x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm')
                    return results
                  """
        
        self.driver.execute_script("window.scrollBy(0,-"+ str(n_scroll*6150) +")")

        elements = self.driver.execute_script(script)
        elements = elements[:n_posts]

        for element in elements:
            try:
                href = element.get_attribute('href')
                if '#' in href:
                    element.click()
                    href = element.get_attribute('href')
                else: continue
                
            except:
                self.driver.execute_script("window.scrollBy(0,1150)")
                sleep(1)
                element.click()
                sleep(1)
                href = element.get_attribute('href')

            if href not in self.post_links:
                self.post_links.append(href)

        print('numero de self.post_links: ', len(self.post_links))
        
    @time_out(time_out=10, raise_exception=False)
    def take_screenshot(self, publication_links):
        for i,link in enumerate(publication_links):
            self.driver.get(link)
            sleep(2)
            self.driver.save_screenshot('imgs/'+str(i)+'.png')

    def conecta_db(self):
        con = psycopg2.connect(host='dev.danillodars.com.br', 
                                database='infoverse',
                                user='infoverse', 
                                password=')IU+#8Jf{TM8ec5L{94a[6Z@}rk0R7P$')
        return con
        
    def retorna_pesquisa_avulsa(self):
        con = self.conecta_db()
        cursor = con.cursor()

        sql = """SELECT id, id_usuario, id_credencial, data_pesquisa, rede_social, status, palavra_chave, filtro, filtro_avancado, ano_referencia, publicacoes_de, localizacao_marcada
                FROM pesquisa_avulsa
                WHERE status IS NULL OR status = False;"""
        
        cursor.execute(sql)
        rows = cursor.fetchall()

        cursor.close()
        con.close()

        return rows
    
    def set_status_pesquisa_avulsa(self, id):
        con = self.conecta_db()
        cursor = con.cursor()

        sql3 = """UPDATE pesquisa_avulsa
                SET status=true
                WHERE id ="""+ str(id) +""";"""
        
        cursor.execute(sql3)
        con.commit()

        cursor.close()
        con.close()

    def retorna_credencial(self, credencial_id):
        con = self.conecta_db()
        cursor = con.cursor()

        sql3 = """SELECT id, descricao, usuario, senha
        FROM bot_credencial_facebook WHERE id ="""+ str(credencial_id) +""";"""

        cursor.execute(sql3)
        row3 = cursor.fetchall()

        cursor = cursor.close()
        con = con.close()

        return row3
    
    def verificando_busca_avulsa(self):
        rows = self.retorna_pesquisa_avulsa()

        for row in rows:
            id, id_usuario, id_credencial, date_search, rede_social, status, keyword, filtro, filtro_avancado, ano_referencia, publicacoes_de, localizacao_marcada = row

            row2 = self.retorna_credencial(id_credencial)
            _, _, cred_usuario, cred_senha = row2[0]

            self.id = id
            self.id_usuario = id_usuario
            self.id_credencial = id_credencial
            self.date_search = date_search
            self.status = status
            self.keyword = keyword
            self.filtro = filtro
            self.cred_usuario = cred_usuario
            self.cred_senha = cred_senha

            if len(row) != 0:
                print('busca encontrada')
                try:
                    self.main()
                except:
                    self.main()

            else:
                print('nenhuma busca encontrada')
                break

            self.set_status_pesquisa_avulsa(id)

    def main(self):
        bot.login_facebook()
        bot.search_keyword()
        bot.getting_information()
        bot.take_screenshot()
        bot.inserir_db()
        
    def inserir_db(self):
        for i,link in enumerate(self.post_links):
            publication_id = self.remover_letra(self.link, '/')
            publication_id = self.remover_letra(self.link, ':')

            sql = """
            INSERT into contigencia (link_publication, publication_id, id_pesquisa_avulsa) 
            values('%s','%s', '%s');
            """ % (link, publication_id, self.id)

            con = self.conecta_db()
            cursor = con.cursor()

            cursor.execute("""SELECT publication_id FROM pesquisa_bot_twitter WHERE publication_id = '"""+ str(publication_id) +"""';""")
            linhas = cursor.fetchall()

            cursor.close()
            con.close()
            
            # Conte o número de linhas retornadas
            numero_de_linhas = len(linhas)

            if numero_de_linhas == 0:
                try:
                    con = self.conecta_db()
                    cursor = con.cursor()

                    cursor.execute(sql)
                    con.commit()

                    cursor.close()
                    con.close()


                    with open('imgs/'+str(i)+'.png', 'rb') as file:
                        print('caminho: ', 'imgs/'+str(i)+'.png')
                        
                        imagem_bytes = file.read()

                    # data_bin = (psycopg2.Binary(imagem_bytes),)

                    data = (publication_id, psycopg2.Binary(imagem_bytes))

                    sql2 = """
                            INSERT INTO pesquisa_screenshot (publication_id, bytea) 
                            VALUES (%s, %s);
                            """
                    print('data_bin: ',data)

                    con = self.conecta_db()
                    cursor = con.cursor()

                    cursor.execute(sql2, data)
                    con.commit()

                    cursor.close()
                    con.close()

                except (Exception, psycopg2.DatabaseError) as error:
                    print("Error: %s" % error)
                    con.rollback()
                    cursor.close()
                    con.close()

                    return 1


if __name__ == '__main__':
    global precessando 
    processando = False

    bot = bot_face()
    
    while True:
        if not processando:
            try:
                processando = True
                bot.verificando_busca_avulsa()
                processando = False
            except:
                processando = True
                bot.verificando_busca_avulsa()
                processando = False





# Do whatever you want on Twitter here

# Close the browser when you're done
# driver.quit()
