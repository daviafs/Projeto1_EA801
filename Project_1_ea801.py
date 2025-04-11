# ==========================================================================
#
#		Projeto 1
#
#		Disciplina: EA801- Laboratório Projetos Sistemas Embarcados
#
#		Título do projeto:
#		SISTEMA DE CONTROLE PWM PARA ILUMINAÇÃO LED E CLIMATIZAÇÃO EM AGRICULTURA INDOOR
#       
#		Alunos (RA):
#       Davi Alves Feitosa de Souza (256447)
#       Gabriel Martins De Andrade (216337)
#
#		Docentes: Antônio Augusto Fasolo Quevedo
#
#		Data: 10 de Junho, 2025
#
# ==========================================================================

# Importa as bibliotecas utilizadas
# Bibliotecas CircuitPhyton:
# Bundle for Version 9.x (https://circuitpython.org/libraries)
import time
import digitalio
import pwmio
import microcontroller
import analogio
import busio
import displayio
import terminalio
import neopixel
import gc
import math
from adafruit_display_text import label
from adafruit_displayio_ssd1306 import SSD1306


# ----------- Display OLED -----------
displayio.release_displays()  # Libera quaisquer recursos de display usados anteriormente
i2c = busio.I2C(scl=microcontroller.pin.PB10, sda=microcontroller.pin.PB09)  # Inicializa barramento I2C
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)  # Comunicação I2C com display SSD1306
display = SSD1306(display_bus, width=128, height=64)  # Cria objeto do display OLED
splash = displayio.Group()  # Grupo para conter elementos gráficos
display.root_group = splash  # Define grupo principal para o display
text_area = label.Label(terminalio.FONT, text="", x=0, y=4, line_spacing=1.2)  # Área de texto com fonte padrão
# y=4 para garantir a visualização de tudo no display (sem cortar o texto)
splash.append(text_area)  # Adiciona texto ao grupo

# ----------- SafeNeoPixel Wrapper -----------
# Classe para gerenciar LEDs NeoPixel com segurança e liberação de memória
class SafeNeoPixel:
    def __init__(self, pin, n, brightness=1.0, auto_write=True):
        self.pin = pin
        self.brightness = brightness
        self.auto_write = auto_write
        self._n = None
        self.pixels = None
        self.set_n(n)

    def set_n(self, new_n):
        # Libera recurso anterior (se houver), força coleta de lixo e atualiza número de LEDs
        if self.pixels:
            try:
                self.pixels.deinit()
            except Exception:
                pass
            self.pixels = None
            gc.collect()
        self._n = new_n
        self.pixels = neopixel.NeoPixel(
            self.pin, self._n,
            brightness=self.brightness,
            auto_write=self.auto_write
        )

    def fill(self, color):
        self.pixels.fill(color)

    def show(self):
        self.pixels.show()

    def set_brightness(self, value):
        self.brightness = value
        self.pixels.brightness = value

    def deinit(self):
        if self.pixels:
            try:
                self.pixels.deinit()
            except Exception:
                pass
            self.pixels = None
            gc.collect()

# ----------- Configurações LEDs RGB -----------
# Define os pinos utilizados para controle dos LEDs nas cores vermelha, verde e azul, utilizando a biblioteca `board`.
# Em seguida, configura os objetos PWMOut para cada cor com duty cycle inicial igual a zero, o que significa que os LEDs começam apagados.
# Essa configuração permite o controle fino da intensidade de cada cor individualmente, possibilitando a criação de composições luminosas variadas.
# Intensidades em formato de exibição (%) e real (número de LEDs)
intensidades_print = [0, 50, 80, 100]
intensidades = [0, 50, 200, 600]
# Diferentes composições de cor
composicoes = ["White", "Pink", "Red+Green", "Full Spectrum"]

# Cria objetos para os LEDs RGB controlados separadamente
pixels_vermelho = SafeNeoPixel(microcontroller.pin.PA05, 1, brightness=1, auto_write=True)
pixels_verde = SafeNeoPixel(microcontroller.pin.PA07, 1, brightness=1, auto_write=True)
pixels_azul = SafeNeoPixel(microcontroller.pin.PA02, 1, brightness=1, auto_write=True)

# Índices iniciais para intensidade e composição
indice_intensidade = 0
indice_composicao = 0

# ----------- Botões A e B -----------
# Controle do espectro de luz baseado nos botões pressionados
# Define os pinos utilizados pelos botões A e B e os configura como entradas com resistor pull-down interno ativado.
# Essa configuração garante que o sinal dos botões seja interpretado corretamente pelo sistema (nível baixo quando solto e alto quando pressionado),
# permitindo o uso dos botões para alterar a intensidade da luz (botão A) e mudar a composição de cores (botão B).

# Configura botão A para controle da intensidade
botao_a = digitalio.DigitalInOut(microcontroller.pin.PB12)
botao_a.direction = digitalio.Direction.INPUT
botao_a.pull = digitalio.Pull.UP

# Configura botão B para controle da composição de cor
botao_b = digitalio.DigitalInOut(microcontroller.pin.PA15)
botao_b.direction = digitalio.Direction.INPUT
botao_b.pull = digitalio.Pull.UP

# Flags para evitar múltiplas leituras seguidas do botão
botao_a_controlado = False
botao_b_controlado = False

# ----------- PWM Buzzers -----------
# Define os pinos conectados aos buzzers (ventilador e exaustor simulados) e cria objetos PWMOut para controlar suas frequências.
# A frequência de cada buzzer é ajustada dinamicamente com base nas leituras do joystick, simulando a variação de rotação de ventiladores conforme a temperatura e a umidade do ambiente.

# Duty cycle fixo (usado aqui como ventiladores ou exaustores simulados com PWM)
DUTY = int(65535 * 0.0005)

# Listas de frequências possíveis
freqs_esquerda = list(range(8, 15))     # Ventilador - PA09
freqs_direita = list(range(1, 8))       # Exaustor - PA01

# Índices iniciais das frequências
indice_esquerda = 0
indice_direita = 0

# Inicializa PWM com frequência inicial
buzzer_esquerda = pwmio.PWMOut(microcontroller.pin.PA09, frequency=freqs_esquerda[indice_esquerda], duty_cycle=DUTY)
buzzer_direita = pwmio.PWMOut(microcontroller.pin.PA01, frequency=freqs_direita[indice_direita], duty_cycle=DUTY)

# ----------- Joystick -----------
# Configura os canais analógicos utilizados para leitura dos eixos X e Y do joystick.
# Esses eixos simulam sensores ambientais: o eixo Y representa a temperatura, e o eixo X representa a umidade.
# Os valores lidos são usados para alterar a frequência dos buzzers, permitindo uma simulação interativa do controle ambiental.

# Pinos analógicos para leitura do joystick
vrx = analogio.AnalogIn(microcontroller.pin.PA06)  # Vertical
vry = analogio.AnalogIn(microcontroller.pin.PB01)  # Horizontal

# Função ler_valor(adc):
# Realiza a leitura de um canal analógico e converte o valor lido (de 0 a 65535) para uma escala de 0 a 1023.
# Essa conversão facilita o controle proporcional da intensidade ou posição em outras partes do sistema, como o joystick.
def ler_valor(adc):
    return int((adc.value * 1023) / 65535)

MARGEM = 100  # Margem de deslocamento mínimo do joystick

# ----------- Atualiza LEDs ----------
# Função calcular_e_atualizar_n():
# Calcula o número total de LEDs que devem ser ativados com base na variável 'intensidade'.
# A função distribui esse total proporcionalmente entre as cores vermelho, verde e azul de acordo com a composição escolhida.
# Em seguida, ativa os LEDs correspondentes, simulando diferentes combinações espectrais de luz.
def calcular_e_atualizar_n(composicoes, indice_composicao, intensidades, indice_intensidade):
    n_total = intensidades[indice_intensidade]

    if composicoes[indice_composicao] == "White":
        r, g, b = 40, 30, 30
    elif composicoes[indice_composicao] == "Pink":
        r, g, b = 55, 0, 45
    elif composicoes[indice_composicao] == "Red+Green":
        r, g, b = 88, 10, 2
    else:  # Full Spectrum
        r, g, b = 70, 15, 15

    soma = r + g + b
    
    # Calcula número proporcional de LEDs por cor
    pixels_vermelho.set_n(math.floor(n_total * (r / soma)))  #ativa luz vermelha
    pixels_verde.set_n(math.floor(n_total * (g / soma))) 	 #ativa luz verde
    pixels_azul.set_n(math.floor(n_total * (b / soma)))		 #ativa luz azul

# ----------- Display -----------
# Função atualizar_display():
# Atualiza o display OLED com as informações atuais do sistema, como intensidade da luz, composição de cor, temperatura simulada,
# umidade simulada e frequências dos "ventiladores" (buzzers).
# Essa visualização em tempo real auxilia no monitoramento e controle do ambiente simulado.
def atualizar_display(composicoes, indice_composicao, intensidades, indice_intensidade):
    linha1 = f"Intensidade: {intensidades_print[indice_intensidade]}%"
    linha2 = f"Cor: {composicoes[indice_composicao]}"
    linha3 = f"Temp: {temperature}°C  |  RH: {humidity}%"
    linha4 = f"Ventilador: {freqs_esquerda[indice_esquerda]}Hz"
    linha5 = f"Exaustor: {freqs_direita[indice_direita]}Hz"
    text_area.text = f"{linha1}\n{linha2}\n{linha3}\n{linha4}\n{linha5}"
    display.refresh()  # Força atualização do display

# ----------- Botão -----------
# Função verificar_pressao(botao, ultima_pressao):
# Verifica se um botão foi pressionado, aplicando um tempo de debounce (200 ms)
# para evitar leituras incorretas causadas por toques rápidos ou ruído.
# Retorna True se a pressão for válida, atualizando o timestamp da última pressão.
def verificar_pressao(botao, tempo_necessario=0.2):
    tempo_inicial = time.monotonic()
    while not botao.value:
        if time.monotonic() - tempo_inicial >= tempo_necessario:
            return True
        time.sleep(0.01)
    return False

# Variáveis iniciais para emular temperatura e umidade
temperature = 15  # Temperatura inicial em graus Celsius
humidity = 20     # Umidade relativa inicial em %

# ----------- Loop Principal do programa-----------
# Executa continuamente a lógica do sistema. Lê os valores do joystick para simular temperatura (eixo Y) e umidade (eixo X),
# ajustando a frequência dos buzzers que representam ventilador e exaustor.
# Controla a intensidade dos LEDs com o botão A e alterna entre composições de cor com o botão B.
# Atualiza a iluminação e o display com as informações atuais, permitindo controle interativo do ambiente.
while True:
    # Atualiza display e LEDs a cada ciclo
    atualizar_display(composicoes, indice_composicao, intensidades_print, indice_intensidade)
    calcular_e_atualizar_n(composicoes, indice_composicao, intensidades, indice_intensidade)

    # Controle da intensidade com o botão A
    if not botao_a.value and not botao_a_controlado:
        if verificar_pressao(botao_a, 0.005):
            indice_intensidade = (indice_intensidade + 1) % len(intensidades)
            botao_a_controlado = True
    if botao_a.value and botao_a_controlado:
        botao_a_controlado = False

    # Controle da composição com o botão B
    if not botao_b.value and not botao_b_controlado:
        if verificar_pressao(botao_b, 0.005):
            indice_composicao = (indice_composicao + 1) % len(composicoes)
            botao_b_controlado = True
    if botao_b.value and botao_b_controlado:
        botao_b_controlado = False

    # Controle do ventilador com o joystick (eixo vertical)
    x = ler_valor(vrx) # Eixo X → Simula temperatura 
    if x < (512 - MARGEM) and indice_esquerda < len(freqs_esquerda) - 1:
        indice_esquerda += 1 # Aumenta a frequência do buzzer
        temperature += 5 # Aumenta a variável de temperatura em 5°C
        buzzer_esquerda.deinit()
        buzzer_esquerda = pwmio.PWMOut(microcontroller.pin.PA09, frequency=freqs_esquerda[indice_esquerda], duty_cycle=DUTY)
        time.sleep(0.2)
    elif x > (512 + MARGEM) and indice_esquerda > 0:
        indice_esquerda -= 1 # Reduz a frequência do buzzer
        temperature -= 5 # Reduz a variável de temperatura em 5°C
        buzzer_esquerda.deinit()
        buzzer_esquerda = pwmio.PWMOut(microcontroller.pin.PA09, frequency=freqs_esquerda[indice_esquerda], duty_cycle=DUTY)
        time.sleep(0.2)

    # Controle do exaustor com o joystick (eixo horizontal)
    y = ler_valor(vry) # Eixo Y → Simula umidade relativa
    if y < (512 - MARGEM) and indice_direita < len(freqs_direita) - 1:
        indice_direita += 1  # Aumenta a frequência do buzzer
        humidity += 10 # Aumenta a variável de umidade relativa em 10%
        buzzer_direita.deinit()
        buzzer_direita = pwmio.PWMOut(microcontroller.pin.PA01, frequency=freqs_direita[indice_direita], duty_cycle=DUTY)
        time.sleep(0.2)
    elif y > (512 + MARGEM) and indice_direita > 0:
        indice_direita -= 1 # Reduz a frequência do buzzer
        humidity -= 10 # Reduz a variável de umidade relativa em 10%
        buzzer_direita.deinit()
        buzzer_direita = pwmio.PWMOut(microcontroller.pin.PA01, frequency=freqs_direita[indice_direita], duty_cycle=DUTY)
        time.sleep(0.2)
    
    # Delay curto  para estabilizar leituras e evitar atualizações rápidas
    time.sleep(0.01)  
