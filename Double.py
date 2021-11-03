from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Access import Access
from datetime import datetime
import logging
import time 

class Double:

    def process(self):
        try:
            driverBlaze = webdriver.Chrome(executable_path=r"/var/www/html/robotBlaze/driver/chromedriver")
            retBlaze = self.initBlaze(driverBlaze)
            if retBlaze == 0:
                raise Exception("Erro no processo do site Blaze")
            
            driverTelegram = webdriver.Chrome(executable_path=r"/var/www/html/robotBlaze/driver/chromedriver")
            retTelegram = self.initTelegram(driverTelegram)
            if retTelegram == False:
                raise Exception("Erro no processo do site Telegram")

            retLoop = self.loop(driverBlaze, driverTelegram)
            if retLoop == False:
                raise Exception("Erro Loop")

            return True
        except Exception as error:
            print('Erro Método process: ', error)
            return False

    def initBlaze(self, driver):
        try:
            if driver == '':
                raise Exception ('Driver não fornecido no método initBlaze')

            retGet = driver.get("https://blaze.com/pt/games/double")
            if retGet == False:
                raise Exception('Erro ao tentar abrir o site da Blaze')
            wait = WebDriverWait(driver, 30)

            retLogin = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'link')))
            if retLogin == False:
                raise Exception('Não identificado o botão de Login Blaze')
            retLogin.click()
            
            login = wait.until(EC.presence_of_element_located((By.NAME, 'username')))
            if login == False:
                raise Exception('Não identificado o campo Login no site Blaze')
            login.send_keys(Access.login())

            senha = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
            if senha == False:
                raise Exception('Não identificado o campo Senha no site Blaze')
            senha.send_keys(Access.password() + Keys.RETURN)
            
            campoAposta = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'input-field')))
            if campoAposta == False:
                raise Exception('Erro ao fazer login no site Blaze')

            return True
        except Exception as error:
            print('Erro Método initBlaze: ', error)
            return False

    def initTelegram(self, driver):
        try:
            if driver == '':
                raise Exception ('Driver não fornecido no método initTelegram')
            
            retGet = driver.get("https://web.telegram.org/k/")
            if retGet == False:
                raise Exception('Erro ao tentar abrir o site do Telegram')
            wait = WebDriverWait(driver, 30)

            retAberturaChatVip = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="folders-container"]/div/div[1]/ul/li[1]')))
            if retAberturaChatVip == False:
                raise Exception('Não efetuado LOGIN no Telegram')
            retAberturaChatVip.click()

            return True
        except Exception as error:
            print('Erro Método initTelegram: ', error)
            return False

    def loop(self, driverBlaze, driverTelegram):
        try:
            logging.basicConfig(filename='apostasRealizadas.txt', level=logging.ERROR)
            logging.error(';'+str('valorAPosta')+';'+ str('corAposta')+';'+ str('brancoAposta')+';'+ str('winAposta')+';'+ str('contadorAposta')+';'+ str('Data/Hora'))

            if driverBlaze == '' :
                raise Exception ('Driver Blaze não fornecido no método loop')
            elif driverTelegram == '' :
                raise Exception ('Driver Telegram não fornecido no método loop') 

            valorAPostaInicial = 0.02
            valorAPosta = valorAPostaInicial
            timestampAnterior = ''
            contadorAposta = 1
            aguardarLoss = True

            while(True):
                time.sleep(3)
                if aguardarLoss == True:
                    retFirstLoss = self.waitingFirstLoss(driverBlaze, driverTelegram)
                    print('Saiu do aguardo First Loss')
                    if retFirstLoss == False:
                        raise Exception('Erro ao tentar identificar o Primeiro Loss')  
                
                aguardarLoss = False
                print('Procurando ultima mensagem Telegram')
                retMsg = self.getLastMessage(driverTelegram)
                erro = retMsg[0]
                if erro == True:
                    raise Exception('Erro ao buscar ultima mensagem')
                corAposta = retMsg[1]
                brancoAposta = retMsg[2]
                numJogadaAnterior = retMsg[3]
                corJogadaAnterior = retMsg[4]
                timestamp = retMsg[5]
                
                if erro == True:
                    raise Exception('Erro ao tentar identificar os dados do Telegram. Array: ', retMsg)
                elif corAposta == '' or corAposta != 'VERMELHO' and corAposta != 'PRETO':
                    raise Exception('Erro ao tentar identificar a cor da Aposta')
                elif brancoAposta != True and brancoAposta != False:
                    raise Exception('Erro ao tentar identificar o branco ')
                elif numJogadaAnterior == '' or not isinstance(numJogadaAnterior, int):
                    raise Exception('Erro ao tentar identificar o Numero da Jogada Anterior')
                elif corJogadaAnterior == '' or corJogadaAnterior != 'red' and corJogadaAnterior != 'black' and corJogadaAnterior != 'white':
                    raise Exception('Erro ao tentar identificar a Cor da Jogada Anterior')
                elif timestamp == '' or not timestamp.isdigit():
                    raise Exception('Erro ao tentar identificar o Timestamp da mensagem')
                
                if timestamp == timestampAnterior or timestamp < timestampAnterior:
                    continue
                timestampAnterior = timestamp

                for i in [1, 2, 3]: 
                    if winAposta == True:
                        continue

                    newRetAposta = self.bet(driverBlaze, valorAPosta, str(corAposta), brancoAposta, int(ultimoNumBlaze), str(ultimaCorBlaze))
                    erroAposta = newRetAposta[0]
                    if erroAposta == True:
                        raise Exception('Erro na aposta. Dados: ', retMsg)
                    winAposta = newRetAposta[1]
                    ultimaCorBlaze = newRetAposta[2]
                    ultimoNumBlaze = newRetAposta[3]
                    logging.error(';'+str(valorAPosta)+';'+ str(corAposta)+';'+ str(brancoAposta)+';'+ str(winAposta)+';'+ str(contadorAposta) +';'+ str(datetime.today()))

                    if i > 1:
                        print('INICIADO MARTINGALE: ', i)
                        contadorAposta = int(contadorAposta) + int(1)
                        valorAPosta = float(valorAPosta) * 2

                    if winAposta == True or i == 3:
                        valorAPosta = valorAPostaInicial
                        contadorAposta = 1  
                                             
                aguardarLoss = True

            return True
        except Exception as error:
            print('Erro Método loop: ', error)
            return False

    def getLastMessage(self, driver):
        try:
            if driver == '':
                raise Exception ('Driver não fornecido no método getLastMessage')

            wait = WebDriverWait(driver, 30)
            xpathChatGeral = '//*[@id="column-center"]/div/div/div[3]/div/div'
            chat = wait.until(EC.presence_of_element_located((By.XPATH, xpathChatGeral)))
            if chat == False:
                raise Exception('Não foi possível identificar as mensagens do CHAT VIP')
            
            grupoData = chat.find_elements_by_class_name('bubbles-date-group')
            # print('quantidade grupoData:')
            qtdeGrupoData = len(grupoData) 
            # xpathGrupo = xpathChatGeral + '/div[' + str(qtdeGrupoData) + ']'
            xpathGrupo = xpathChatGeral + '/div'
            # print('xpathGrupo')
            # print(xpathGrupo)
            grupoChat = wait.until(EC.presence_of_element_located((By.XPATH, xpathGrupo)))
            if grupoChat == False:
                raise Exception('Erro ao identificar o Grupo de Data da última mensagem')
            
            divs = grupoChat.find_elements_by_class_name('message')
            contador = int(len(divs)) + int(2)
            # print('contadorDivsMessage')
            # print(contador)
            xpathDiv = xpathGrupo + '/div['+str(contador)+']'
            divPaiUltimaMensagem = wait.until(EC.presence_of_element_located((By.XPATH, xpathDiv)))
            if divPaiUltimaMensagem == False:
                raise Exception('Não foi possível identificar a DIV PAI da última mensagem')
            
            xpathMessage = xpathDiv + str('/div/div/div[2]')
            # print('XpathMessage')
            # print(xpathMessage)
            div = wait.until(EC.presence_of_element_located((By.XPATH, xpathMessage)))
            if div == False:
                raise Exception('Não foi possível ler a mensagem  CHAT VIP')
            text = div.text
            # print('text: ')
            # print(text)
            numCaracterJogoAnterior = text.find('após o ')
            deCaracterJogoAnterior = int(numCaracterJogoAnterior) + 7
            ateCaracterJogoAnterior = text.find(']') + 1
            jogadaAnterior = text[deCaracterJogoAnterior:ateCaracterJogoAnterior]
            numJogadaAnterior = int(jogadaAnterior[0:2])
            comecoStringCor = jogadaAnterior.find('[') + 1
            fimStringCor = jogadaAnterior.find(']')
            stringCor = str(jogadaAnterior[comecoStringCor:fimStringCor])
            if stringCor == 'RED':
                corJogadaAnterior = 'red'
            elif stringCor == 'PRETO':
                corJogadaAnterior = 'black'
            elif stringCor == 'BRANCO':
                corJogadaAnterior = 'white'
            else:
                raise Exception('Erro ao identificar Cor Pedra Anterior: ', stringCor)

            numCaracterBranco = text.find('BRANCO:')
            deCaracterBranco = int(numCaracterBranco) + 8
            ateCaracterBranco = deCaracterBranco + 4
            porcentagemBranco = text[deCaracterBranco:ateCaracterBranco].replace(',', '.')
            branco = False
            if float(porcentagemBranco) > 0:
                branco = True

            img = wait.until(EC.presence_of_element_located((By.XPATH, xpathMessage+'/img[2]')))
            if img == False:
                raise Exception('Erro ao tentar identificar a imagem da mensagem')
            src = img.get_attribute("src")
            emoji = src[44:]
            cor = ''
            if emoji == '1f534.png':
                cor = 'VERMELHO'
            elif emoji == '26ab.png':
                cor = 'PRETO'
            elif emoji == '26aa.png':
                cor = 'BRANCO'

            if cor == '':
                raise Exception('Erro ao identificar a cor. Emoji embasado: ', emoji)

            timestamp = divPaiUltimaMensagem.get_attribute("data-timestamp")
            if timestamp == False:
                raise Exception('Erro ao tentar identificar o timestamp da mensagem')

            #RETORNO = [Erro (true ou false), Cor, Branco(true ou false), numJogadaAnterior, corJogadaAnterior, IdentificadorMensagem (timestamp)]
            return [False, cor, branco, numJogadaAnterior, corJogadaAnterior, timestamp]
        except Exception as error:
            print('Erro Método getLastMessage: ', error)
            return [True]

    def bet(self, driver, valorAposta, corAposta, brancoAposta, numJogadaAntTelegram, corJogadaAntTelegram):
        try:
            if driver == '':
                raise Exception ('Driver não fornecido no método bet')
            elif valorAposta == '' or not isinstance(valorAposta, float):
                raise Exception ('Valor inválido para apostar: ', valorAposta)
            elif corAposta == '' or corAposta != 'VERMELHO' and corAposta != 'PRETO':
                raise Exception('Cor inválida: ', corAposta)
            elif brancoAposta != True and brancoAposta != False:
                raise Exception('Situação inválida para o Branco: ', brancoAposta)
            elif numJogadaAntTelegram == '' or not isinstance(numJogadaAntTelegram, int):
                raise Exception('Numero da Jogada Anterior inválido: ', numJogadaAntTelegram)
            elif corJogadaAntTelegram == '' or corJogadaAntTelegram != 'red' and corJogadaAntTelegram != 'black' and corJogadaAntTelegram != 'white':
                raise Exception('Cor da Jogada Anterior inválido: ', corJogadaAntTelegram)

            wait = WebDriverWait(driver, 30)

            retLastBet = self.getLastBet(driver)
            erroBet = retLastBet[0]
            if erroBet == True:
                raise Exception('Erro ao tentar buscar ultima aposta Blaze')
            ultimaCorBlaze = retLastBet[1]
            ultimoNumBlaze = retLastBet[2]
            
            if str(corJogadaAntTelegram) != str(ultimaCorBlaze):
                print("Cor Rodada Anterior Telegram: " + corJogadaAntTelegram + " diferente da cor Blaze: " + ultimaCorBlaze)
                return None

            if int(numJogadaAntTelegram) != int(ultimoNumBlaze) and str(corJogadaAntTelegram) != 'white':
                print('Número Rodada Anterior Telegram: '+ str(numJogadaAntTelegram) + ' diferente do Número Blaze: ' + str(ultimoNumBlaze))
                return None

            quantia = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'input-field')))
            if quantia == False:
                raise Exception('Não identificado o campo Quantia no site Blaze')
            quantia.send_keys(valorAposta)

            if corAposta == 'VERMELHO':
                corAposta = 'red'
                xpathCor = '//*[@id="roulette-controller"]/div[1]/div[1]/div[2]/div/div[1]'
            elif corAposta == 'PRETO':
                corAposta = 'black'
                xpathCor = '//*[@id="roulette-controller"]/div[1]/div[1]/div[2]/div/div[3]'
            else:
                raise Exception('Erro ao identificar a cor da Aposta')
            
            print('---------------NEW BET---------------')
            print('ValorAposta: ', valorAposta)
            print('CorAposta: ', corAposta)
            print('BrancoAposta: ', brancoAposta)
            print('numJogadaAntTelegram: ', numJogadaAntTelegram)
            print('corJogadaAntTelegram: ', corJogadaAntTelegram)

            botaoCor = wait.until(EC.element_to_be_clickable((By.XPATH, xpathCor)))
            if botaoCor == False:
                raise Exception('Erro ao identificar o botao da cor ', corAposta)
            botaoCor.click()

            botaoComecarJogo = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="roulette-controller"]/div[1]/div[2]/button')))
            if botaoComecarJogo == False:
                raise Exception('Erro ao identificar o botao Começar Jogo ')
            # botaoComecarJogo.click()

            if brancoAposta == True:
                aguardarBotao = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="roulette-controller"]/div[1]/div[2]/button')))
                if aguardarBotao == False:
                    raise Exception('Erro ao aguardar o botao Começar Jogo')

                quantia.send_keys(0.01)
                botaoCorBranco = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="roulette-controller"]/div[1]/div[1]/div[2]/div/div[2]')))
                if botaoCorBranco == False:
                    raise Exception('Erro ao identificar o botao da Cor Branco')
                botaoCorBranco.click()
                # botaoComecarJogo.click()

            print('Feito Aposta')     
            print('Analisando WIN')       

            newRetLastBet = self.getLastBet(driver, True)
            erroNewBet = newRetLastBet[0]
            if erroNewBet == True:
                raise Exception('Erro ao tentar buscar ultima aposta Blaze para consultar WIN')
            newUltimaCorBlaze = newRetLastBet[1]
            newUltimoNumBlaze = newRetLastBet[2]

            win = False
            if str(newUltimaCorBlaze) == str(corAposta):
                win = True

            if str(newUltimaCorBlaze) == 'white' and brancoAposta == True:
                win = True

            # return [Erro (true ou false), Win (true ou false), ultimaCorBlaze, ultimoNumBlaze]
            print('Resultado - WIN: ' + str(win) + ' | Cor: ' + str(newUltimaCorBlaze) + ' | Num: ' + str(newUltimoNumBlaze))
            return [False, win, newUltimaCorBlaze, newUltimoNumBlaze]
        except Exception as error:
            print('Erro Método bet: ', error)
            return [True]

    def getLastBet(self, driver, aguardar = False):
        try:
            wait = WebDriverWait(driver, 30)
        
            if aguardar == True:
                print('Entrou no aguardar True')
                newStyleTemporizador = str('display: flex;')
                while (newStyleTemporizador != 'display: none;'):
                    divPai = wait.until(EC.presence_of_element_located((By.ID, 'roulette-timer')))
                    divTemporizadorBlaze = divPai.find_element_by_class_name('progress-bar')
                    if divTemporizadorBlaze == False:
                        raise Exception('Não identificado div do Temporizador Blaze para analise de WIN')
                    newStyleTemporizador = divTemporizadorBlaze.get_attribute("style")
                    if newStyleTemporizador != 'display: none;':
                        time.sleep(2)

            print('Saiu do aguardar True')
            styleTemporizador = str('display: none;')
            while (styleTemporizador != 'display: flex;'):
                divPai = wait.until(EC.presence_of_element_located((By.ID, 'roulette-timer')))
                divTemporizadorBlaze = divPai.find_element_by_class_name('progress-bar')
                if divTemporizadorBlaze == False:
                    raise Exception('Não identificado div do Temporizador Blaze')
                styleTemporizador = divTemporizadorBlaze.get_attribute("style")
                if styleTemporizador != 'display: flex;':
                    time.sleep(2)

            xpathUltJogBlaze = '//*[@id="roulette-recent"]/div/div[1]/div[1]/div/div'
            divUltCorBlaze = wait.until(EC.presence_of_element_located((By.XPATH, xpathUltJogBlaze)))
            if divUltCorBlaze == False:
                raise Exception('Não identificado a div da Cor última jogada')
            ultimaCorBlaze = divUltCorBlaze.get_attribute("class")
            ultimaCorBlaze = ultimaCorBlaze[7:]

            ultimoNumBlaze = 1
            if ultimaCorBlaze != 'white':
                divUltNumBlaze = wait.until(EC.presence_of_element_located((By.XPATH, xpathUltJogBlaze+'/div')))
                if divUltNumBlaze == False:
                    raise Exception('Erro ao identificar a div do Num última jogada')

                ultimoNumBlaze = divUltNumBlaze.text

            # return [Erro (true ou false), UltimaCor, UltimoNumero]
            return [False, str(ultimaCorBlaze), ultimoNumBlaze]
        except Exception as error:
            print('Erro Método getLastBet: ', error)
            return [True]
        

    def waitingFirstLoss(self, driverBlaze, driverTelegram):
        try:
            print('Iniciando WaitingFirstLoss')
            timestampAnterior = ''
            bet = True
            while(bet == True):
                time.sleep(3)
                print('Buscando Mensagem Telegram')
                retMsg = self.getLastMessage(driverTelegram)
                erro = retMsg[0]
                if erro == True:
                    raise Exception('Erro ao buscar ultima mensagem')
                corAposta = retMsg[1]
                brancoAposta = retMsg[2]
                numJogadaAnterior = retMsg[3]
                corJogadaAnterior = retMsg[4]
                timestamp = retMsg[5]
                
                if erro == True:
                    raise Exception('Erro ao tentar identificar os dados do Telegram. Array: ', retMsg)
                elif corAposta == '' or corAposta != 'VERMELHO' and corAposta != 'PRETO':
                    raise Exception('Erro ao tentar identificar a cor da Aposta')
                elif brancoAposta != True and brancoAposta != False:
                    raise Exception('Erro ao tentar identificar o branco ')
                elif numJogadaAnterior == '' or not isinstance(numJogadaAnterior, int):
                    raise Exception('Erro ao tentar identificar o Numero da Jogada Anterior')
                elif corJogadaAnterior == '' or corJogadaAnterior != 'red' and corJogadaAnterior != 'black' and corJogadaAnterior != 'white':
                    raise Exception('Erro ao tentar identificar a Cor da Jogada Anterior')
                elif timestamp == '' or not timestamp.isdigit():
                    raise Exception('Erro ao tentar identificar o Timestamp da mensagem')
                
                if timestamp == timestampAnterior or timestamp < timestampAnterior:
                    print('Timestamp igual ao anterior.... Refazendo busca!')
                    continue
                timestampAnterior = timestamp

                if corAposta == 'VERMELHO':
                    corAposta = 'red'
                elif corAposta == 'PRETO':
                    corAposta = 'black'
                else:
                    raise Exception('Erro ao identificar a cor da Aposta')

                print('Cor para apostar: ', str(corAposta))

                print('Iniciando Busca da ultima Aposta')
                retLastBet = self.getLastBet(driverBlaze, True)
                erroNewBet = retLastBet[0]
                if erroNewBet == True:
                    raise Exception('Erro ao tentar buscar ultima aposta Blaze para consultar Entrada')
                ultimaCorBlaze = retLastBet[1]
                ultimoNumBlaze = retLastBet[2]

                if str(corJogadaAnterior) != str(ultimaCorBlaze):
                    print("Cor Rodada Anterior Telegram: " + corJogadaAnterior + " diferente da cor Blaze: " + ultimaCorBlaze)
                    continue 

                if int(numJogadaAnterior) != int(ultimoNumBlaze) and str(numJogadaAnterior) != 'white':
                    print('Número Rodada Anterior Telegram: '+ str(numJogadaAnterior) + ' diferente do Número Blaze: ' + str(ultimoNumBlaze))
                    continue 
                
                win = False
                if str(ultimaCorBlaze) == str(corAposta):
                    win = True

                if str(ultimaCorBlaze) == 'white' and brancoAposta == True:
                    win = True
                
                print('Resultado - WIN: ' + str(win) + ' | Cor: ' + str(ultimaCorBlaze) + ' | Num: ' + str(ultimoNumBlaze))   

                if win == True:
                    continue

                for i in [1, 2]:
                    print('Iniciando Martingale ', str(i))
                    if win == True:
                        continue
                    
                    print('Iniciando Busca da ultima Aposta')
                    retLastBet = self.getLastBet(driverBlaze, True)
                    erroNewBet = retLastBet[0]
                    if erroNewBet == True:
                        raise Exception('Erro ao tentar buscar ultima aposta Blaze para consultar Entrada')
                    ultimaCorBlaze = retLastBet[1]
                    ultimoNumBlaze = retLastBet[2]

                    if str(ultimaCorBlaze) == str(corAposta):
                        win = True

                    if str(ultimaCorBlaze) == 'white' and brancoAposta == True:
                        win = True

                    print('Resultado - WIN: ' + str(win) + ' | Cor: ' + str(ultimaCorBlaze) + ' | Num: ' + str(ultimoNumBlaze))   

                if win == False:
                    bet = False

            return True
        except Exception as error:
            print('Erro Método waitingFirstLoss: ', error)
            return False
        