def teste1(numero):
    try:
        print('Número passado: ', str(numero))
        number = numero
        teste2(number)
        return [False]
    except Exception as error:
        print('Erro')
        return [True]

def teste2(numero):
    try:

        # return [Erro]
        return [False]
    except Exception as error:
        print('Erro')
        return [True]
    
print(teste1(2))
        