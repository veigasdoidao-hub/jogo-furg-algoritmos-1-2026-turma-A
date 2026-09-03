# pegking-jogo-furg-algoritmos-1-2026-turma-A

Pegking tem como proposta reimaginar algumas propostas apresentadas pelo jogo peggle
Pegking é um jogo de quebra-cabeça e arcade , que mistura mecânicas de pachinko e pinball.
O objetivo é disparar uma quantidade limitada de esferas a partir de um canhão no topo da tela para acertar e eliminar pinos coloridos (com foco principal nos pinos laranjas) espalhados pelo cenário antes que as bolinhas acabem.

Ciência

Mecânica Clássica e Gravidade: Assim que disparada, a esfera é atraída para baixo por uma aceleração gravitação simulada.

Conservação de Energia e Colisões: A energia cinética do lançamento se converte parcialmente em energia potencial e é transferida a cada impacto com os pinos por meio de colisões elásticas e inelásticas. 

Trajetórias Parabólicas: O movimento da bolinha descreve curvas com base na gravidade e na velocidade inicial.

Tecnologia

Motor de Física 2D: O jogo depende de um physics engine para calcular a detecção de colisões (hitboxes circulares), forças e atritos em tempo real.

Geração de Eventos e Estado: O sistema gerencia gatilhos em tempo real, atualização da pontuação e alternância dos poderes mágicos (power-ups).

Engenharia

Design de Fases: Estruturação do espaço e posicionamento dos obstáculos para direcionar o fluxo de movimento e equilibrar a dificuldade.

Sistemas de Feedback: A engenharia de experiência interativa encadeia eventos visuais e sonoros para amplificar a sensação de recompensa a cada acerto.

Artes 

Design Visual e Personagens: Visual vibrante e divertido com instrutores alegres que reduzem a frustração da derrota.

Matemática

Geometria de Ricochete: O jogador precisa calcular mentalmente o ângulo de incidência e o ângulo de reflexão para prever onde a bola irá após o primeiro impacto.  

Probabilidade e Estatística: A trajetória exata após múltiplos impactos torna-se caótica, exigindo cálculo de risco para maximizar pontos ou garantir que a bola caia no cesto inferior.

Integração dos Conceitos no Jogo

Pegking conecta todos esses elementos de forma fluida: a Matemática e a Ciência fornecem as regras de vetor e gravidade que regem a bola; a Tecnologia e a Engenharia executam essas regras em código e estruturam os cenários; e a Arte transforma cálculos físicos abstratos em uma experiência recompensadora.
