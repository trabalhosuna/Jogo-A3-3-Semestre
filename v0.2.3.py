import cv2
import mediapipe as mp
import pygame
import random
import time

"""Correção de bug, ancoragem das novas artes, adicionado sistema randomico de personagens, ajustado o limite do campo"""

class Bola:
    def __init__(self, x, y, velocidade, imagem):
        self.x = x
        self.y = y
        self.velocidade_x = velocidade
        self.velocidade_y = velocidade
        self.imagem = imagem
        self.rect = self.imagem.get_rect(center=(x, y)) #define o hitbox pelo centro da bola
        self.angulo = 0 #define o angulo de rotação inicial


    def atualizar(self):
        self.x += self.velocidade_x
        self.y += self.velocidade_y
        self.rect.center = (self.x, self.y)
        self.angulo += 10 #define o angulo de rotação

    def desenhar(self, tela):
        self.atualizar()
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo) # Faz a bola girar em seu proprio eixo
        retangulo_rotacionado = imagem_rotacionada.get_rect(center=self.rect.center)
        tela.blit(imagem_rotacionada, retangulo_rotacionado)
        
    def colide_jogador(self, jogador):
        return self.rect.colliderect(jogador.rect)

class Jogador:
    def __init__(self, x, y, imagem):
        self.x = x
        self.y = y
        self.imagem = imagem
        self.rect = self.imagem.get_rect(center=(x, y))

    def mover(self, movimento):
        self.y += movimento*1.8
        if self.y < 160:
            self.y = 160
        elif self.y > 900:
            self.y = 900
        self.rect.center = (self.x, self.y)

    def desenhar(self, tela):
        tela.blit(self.imagem, self.rect)

def jogo():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080)) #define o tamanho da tela do jogo (1920 x 1080)
    pygame.display.set_caption('Goal Rush')
    clock = pygame.time.Clock()
    FPS = 60
    fonte = pygame.font.Font(None, 36)

    #adicionando imagens aos objetos
    """Randomiza a escolha dos personagens"""
    Goleiro_1 = pygame.image.load('imagens/Goleiro1.png')
    Goleiro_2 = pygame.image.load('imagens/Goleiro2.png')
    Goleiro_3 = pygame.image.load('imagens/Goleiro3.png')
    Goleiro_4 = pygame.image.load('imagens/Goleiro4.png')
    jogador_esquerda_imagem = random.choice([Goleiro_1, Goleiro_4])
    jogador_direita_imagem = random.choice([Goleiro_2, Goleiro_3])

    bola_imagem = pygame.image.load('imagens/Bola.png')

    jogador_esquerda = Jogador(175, 360, jogador_esquerda_imagem) # define instancia jogador esq
    #jogador_esquerda.rect.inflate_ip(25, 25)
    jogador_direita = Jogador(1745, 360, jogador_direita_imagem) # define instancia jogador dir
    #jogador_direita.rect.inflate_ip(25, 25)
    speed = random.choice([-25, 25]) # define velocidade da bola e randomiza a saida
    bola_objeto = Bola(960, 540, speed, bola_imagem) # define instancia bola
    bola_objeto.rect.inflate_ip(25, 25) # aumenta o tamanho do hitbox da bola

    # Inicialize o MediaPipe Hands.
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

    y_esquerda = 0 # armazena o valor inicial da coordenada y
    y_direita = 0
    Velocidade= 1000

    rodando = True
    pontos_D = 0
    pontos_E = 0

    largura_video = 640 # largura da tela (cam)
    altura_video = 480 # altura da tela (cam)


    def desenhar_linha_vertical(image): # Função para desenhar uma linha vertical no meio do vídeo
        meio_x = largura_video // 2
        cv2.line(image, (meio_x, 0), (meio_x, altura_video), (0, 0, 255), 1) # Desenha a linha vertical, cor= (B,G,R) e espessura= 1



    while rodando: #loop principal do jogo
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        # Captura de vídeo e rastreamento de mãos
        success, image = cap.read() #verifica se recebe a imagem da cam
        if not success:
            break
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb) #recebe o processamento das maos em padrao RGB

        desenhar_linha_vertical(image) # chama a funcao para desenhar a linha vertical

        # Desenhe as landmarks da mão na imagem.
        if results.multi_hand_landmarks: #verifica se a mao foi detectada
            for hand_landmarks in results.multi_hand_landmarks: #para cada landmark em result
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS) #desenha as conexoes entre os pontos

            # Adicione a lógica para detectar a mão esquerda e direita.
            for hand_landmarks in results.multi_hand_landmarks: #para cada landmark em result
                landmark_atual = hand_landmarks.landmark[8] # 8 é o índice do landmark que representa a ponta do dedo indicador
                if landmark_atual.x < 0.5: #0.5 define o ponto medio da tela em que a coordenada da landmark pode estar
                    #esquerda
                    movimento_esquerda= (landmark_atual.y - y_esquerda) * Velocidade
                    #print(movimento_esquerda)
                    jogador_esquerda.mover(movimento_esquerda) #Move o jogador esq
                    y_esquerda = landmark_atual.y
                if landmark_atual.x > 0.5:
                    #direita
                    movimento_direita= (landmark_atual.y - y_direita) * Velocidade
                    #print(movimento_direita)
                    jogador_direita.mover(movimento_direita) #Move o jogador dir
                    y_direita = landmark_atual.y


            cv2.imshow('MediaPipe Hands', image)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        screen.fill((0, 0, 0))
        imagem_fundo = pygame.image.load('imagens/Campo.png') #imagem ao fundo do jogo
        screen.blit(imagem_fundo, (0, 0))

        jogador_esquerda.desenhar(screen)
        jogador_direita.desenhar(screen)
        bola_objeto.desenhar(screen)

        linha_campo = pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(142, 109 , 1636, 848), 3)
        if bola_objeto.rect.colliderect(linha_campo):
            if bola_objeto.rect.left <= linha_campo.left or bola_objeto.rect.right >= linha_campo.right:
                bola_objeto.velocidade_x *= -1
            if bola_objeto.rect.top <= linha_campo.top or bola_objeto.rect.bottom >= linha_campo.bottom:
                bola_objeto.velocidade_y *= -1

        if bola_objeto.colide_jogador(jogador_esquerda) or bola_objeto.colide_jogador(jogador_direita):
            bola_objeto.velocidade_x *= -1

        linha_gol_E = pygame.draw.rect(screen, (255, 10, 10), pygame.Rect(140, 400, 6, 263), 6)
        if bola_objeto.rect.colliderect(linha_gol_E):
            bola_objeto.x = (960)
            bola_objeto.y = (540)
            bola_objeto.velocidade_x *= -1
            pontos_D += 1
            
        linha_gol_D = pygame.draw.rect(screen, (255, 10, 10), pygame.Rect(1773, 400, 6, 263), 6)
        if bola_objeto.rect.colliderect(linha_gol_D):
            bola_objeto.x = (960)
            bola_objeto.y = (540)
            bola_objeto.velocidade_y *= -1
            pontos_E += 1
        
        texto_placar = fonte.render(f'Placar: {pontos_E} x {pontos_D}', True, (255, 255, 255))
        screen.blit(texto_placar, (10, 10))

        if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Verifica se a tecla pressionada é a tecla ESC
                    rodando = False
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    jogo()