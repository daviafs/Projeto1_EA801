# Projeto1_EA801

Projeto para a disciplina EA801- Laboratório Projetos Sistemas Embarcados

Curso: Bacharelado em Engenharia Elétrica (FEEC-UNICAMP)

Alunos (RA): 
Davi Alves Feitosa de Souza (256447)
Gabriel Martins De Andrade (216337)

Docente responsável: Antônio Augusto Fasolo Quevedo
Data: 10 de Junho, 2025

## Descrição:
Título: SISTEMA DE CONTROLE PWM PARA ILUMINAÇÃO LED E CLIMATIZAÇÃO EM AGRICULTURA INDOOR
Linguagem: MicroPython
Plataforma: ThonnyIDE
MCU: STM32F411 BlackPill
Bibliotecas CircuitPhyton: Bundle for Version 9.x (https://circuitpython.org/libraries)
	
## Objetivo do Projeto

O objetivo do projeto consistiu em desenvolver um software de controle via PWM para aplicações de iluminação LED e climatização, em estufas por exemplo, garantindo o controle de temperatura e umidade relativa baseado em ventoinhas. A proposta é simular as condições de um ambiente controlado para cultivo de plantas, com funcionalidades que permitem ajustes interativos e monitoramento em tempo real. Para isso, o projeto contou com o uso da placa BitDogLab, o microcontrolador STM32F411 BlackPill, e a linguagem de programação CircuitPython, para simular as variáveis monitoradas por sistema de controle ambiental para cultivo de plantas em ambientes fechados. Com isso, a partir do código desenvolvido, buscou-se garantir as seguintes funcionalidades para o sistema:

1. Ajuste do espectro de luz e sua intensidade com base na quantidade de luz que atingem a planta, simulada a partir da interação do usuário com os botões da placa;

2. Emulação de um sensor através do joystick para fornecer a informação analógica das variáveis simulando a temperatura e umidade relativa; 

3. Ajuste da velocidade da ventoinha para ventilação e exaustão a partir das mudanças nas variáveis de temperatura e umidade relativa;

4. Apresentação dos valores das variáveis emuladas e status do sistema via display.

## Fluxograma




## Imagens de funcionamento
