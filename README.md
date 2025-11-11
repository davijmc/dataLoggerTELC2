# 📡 Data Logger TELC2

Sistema completo de captura, processamento e decodificação de sinais de controle remoto infravermelho (IR) via comunicação serial. Este projeto implementa um data logger que captura sinais analógicos de um conversor A/D, processa os dados e decodifica comandos do protocolo NEC IR para controlar ações no computador.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura do Sistema](#-arquitetura-do-sistema)
- [Requisitos](#-requisitos)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Descrição Detalhada dos Arquivos](#-descrição-detalhada-dos-arquivos)
- [Fluxo de Dados](#-fluxo-de-dados)
- [Como Usar](#-como-usar)
- [Configuração](#-configuração)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Visão Geral

Este projeto foi desenvolvido para a disciplina TELC2 e implementa um sistema completo de:

- **Captura de dados seriais** com trigger automático baseado em threshold
- **Conversão analógico-digital** e binarização inteligente de sinais
- **Decodificação de protocolo NEC IR** (controle remoto) com validação
- **Aplicações práticas**: controle de teclado, mouse e debugger visual
- **Visualização gráfica** dos sinais capturados em tempo real

O sistema funciona como um intermediário entre um hardware de captura (STM32F401 via serial) e aplicações que executam ações no computador baseadas nos comandos decodificados do controle remoto.

### Fluxo Geral do Sistema

```
Hardware (STM32F401) → Serial (COM6) → serialRead.py → conversorAD.py → decodificador.py → Aplicação (Keyboard/Mouse/Debugger)
```

### 📊 Fluxograma do App Debugger

O `app_Debugger.py` é a aplicação principal para visualização e análise de sinais IR. Abaixo está o fluxograma completo do seu funcionamento:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        INÍCIO DO APLICATIVO                             │
│                    python app_Debugger.py                               │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   build_gui()        │
                    │  Inicializa Tkinter  │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
    ┌───────────────────────┐    ┌────────────────────────┐
    │  Cria Interface GUI   │    │  Configura Gráficos    │
    │  - Campos de entrada  │    │  - Raw data plot       │
    │  - Área de log        │    │  - Binary data plot    │
    │  - Botões (Start/Stop)│    │  - Matplotlib canvas   │
    └──────────┬────────────┘    └───────────┬────────────┘
               │                             │
               └──────────────┬──────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │   app.mainloop()     │
                    │  Interface ativa     │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
    ┌──────────────────────┐    ┌──────────────────────┐
    │  Usuário configura   │    │  Usuário clica       │
    │  parâmetros:         │    │  "Clear Log"         │
    │  - Serial Port       │    │                      │
    │  - Baud Rate         │    │  → Limpa log         │
    │  - Trigger Value     │    │  → Reseta gráficos   │
    │  - Capture Length    │    └──────────────────────┘
    └──────────┬────────────┘
               │
               ▼
    ┌───────────────────────┐
    │  Usuário clica        │
    │  "Start Capture"      │
    └──────────┬────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  on_start()                          │
    │  - Valida parâmetros                 │
    │  - Desabilita botão Start            │
    │  - Habilita botão Stop               │
    │  - Limpa capture_stop_event          │
    │  - Cria thread de captura (daemon)   │
    └──────────┬───────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────┐
    │  THREAD PRINCIPAL (UI)               │  ┌──────────────────────────────┐
    │  Continua responsiva                 │  │  THREAD DE CAPTURA           │
    │  - Interface interativa              │  │  (capture_thread)            │
    │  - Aguarda eventos                   │  └──────────┬───────────────────┘
    └──────────────────────────────────────┘             │
                                                         ▼
                                            ┌──────────────────────────────┐
                                            │  capture_thread()            │
                                            │  append_log("Iniciando...")  │
                                            └──────────┬───────────────────┘
                                                       │
                                                       ▼
                                            ┌──────────────────────────────┐
                                            │  LOOP CONTÍNUO               │
                                            │  while not stop_event:       │
                                            └──────────┬───────────────────┘
                                                       │
                                    ┌──────────────────┴──────────────────┐
                                    │                                     │
                                    ▼                                     ▼
                    ┌──────────────────────────┐    ┌──────────────────────────┐
                    │  Aguarda trigger         │    │  stop_event.is_set()?    │
                    │  serialRead.r_serial()   │    │                          │
                    │  (BLOQUEANTE)            │    │  → Se SIM: sai do loop   │
                    └──────────┬───────────────┘    │  → Se NÃO: continua      │
                               │                    └──────────┬───────────────┘
                               │                               │
                               ▼                               │
                    ┌──────────────────────────┐               │
                    │  Dados capturados        │               │
                    │  - data: lista uint8     │               │
                    │  - duracao: tempo        │               │
                    └──────────┬───────────────┘               │
                               │                               │
                               ▼                               │
                    ┌──────────────────────────┐               │
                    │  conversorAD.ad(data)    │               │
                    │  → bin_data              │               │
                    └──────────┬───────────────┘               │
                               │                               │
                               ▼                               │
                    ┌──────────────────────────┐               │
                    │  decodificador.nec_      │               │
                    │  decoder(bin_data, fs)   │               │
                    │  → address, command,     │               │
                    │     status, edges, bits  │               │
                    └──────────┬───────────────┘               │
                               │                               │
                               ▼                               │
                    ┌──────────────────────────┐               │
                    │  append_log()            │               │
                    │  - Status decodificação  │               │
                    │  - Número de edges       │               │
                    │  - Bits detectados       │               │
                    │  - Endereço e comando    │               │
                    └──────────┬───────────────┘               │
                               │                               │
                               ▼                               │
                    ┌──────────────────────────┐               │
                    │  root.after(0, lambda:   │               │
                    │    update_plots(data,    │               │
                    │              bin_data))  │               │
                    │  (Thread-safe UI update) │               │
                    └──────────┬───────────────┘               │
                               │                               │
                               └────────┬──────────────────────┘
                                        │
                                        ▼
                            ┌───────────────────────────┐
                            │  update_plots()           │
                            │  - Atualiza gráfico raw   │
                            │  - Atualiza gráfico binary│
                            │  - canvas.draw_idle()     │
                            └──────────┬────────────────┘
                                       │
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                     │
                    ▼                                     ▼
    ┌──────────────────────────┐    ┌──────────────────────────┐
    │  Volta ao início do loop │    │  Usuário clica "Stop"    │
    │  (nova captura)          │    │                          │
    └──────────────────────────┘    │  → on_stop()             │
                                    │  → capture_stop_event    │
                                    │    .set()                │
                                    └──────────┬───────────────┘
                                               │
                                               ▼
                                    ┌──────────────────────────┐
                                    │  Thread termina          │
                                    │  - finally:              │
                                    │    → Reabilita Start     │
                                    │    → Desabilita Stop     │
                                    └──────────┬───────────────┘
                                               │
                                               ▼
                                    ┌──────────────────────────┐
                                    │  Interface volta ao      │
                                    │  estado inicial          │
                                    │  (aguardando Start)      │
                                    └──────────────────────────┘
```

#### 🔑 Pontos-Chave do Fluxograma

1. **Inicialização**: GUI é criada com todos os componentes (campos, log, gráficos, botões)
2. **Threading**: Aplicação usa duas threads:

   - **Thread Principal**: Interface gráfica (Tkinter mainloop)
   - **Thread de Captura**: Processamento de dados (não bloqueia UI)
3. **Loop de Captura**: Thread secundária executa loop contínuo até `stop_event` ser setado
4. **Processamento em Pipeline**:

   - Captura serial → Conversão A/D → Decodificação NEC → Log e Visualização
5. **Thread-Safety**: Atualizações de UI são feitas via `root.after()` para garantir segurança
6. **Controle de Estado**: Botões são habilitados/desabilitados conforme estado da captura
7. **Tratamento de Erros**: Try-except na thread de captura evita travamento da aplicação

---

## 🏗️ Arquitetura do Sistema

O sistema é composto por três camadas principais:

1. **Camada de Captura** (`serialRead.py`): Interface com hardware via serial
2. **Camada de Processamento** (`conversorAD.py`, `decodificador.py`): Processamento de sinais e decodificação
3. **Camada de Aplicação** (`app_*.py`): Interface com usuário e execução de ações

Cada camada é independente e pode ser testada separadamente, facilitando debug e manutenção.

---

## 🔧 Requisitos

### Dependências Python (Python 3.7+)

**Instalação via requirements.txt (Recomendado)**:

```bash
pip install -r requirements.txt
```

**Instalação manual**:

```bash
pip install pyserial numpy matplotlib pyautogui
```

**Nota sobre tkinter**: O `tkinter` geralmente vem incluído com Python. Se não estiver disponível:

- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Fedora**: `sudo dnf install python3-tkinter`
- **macOS/Windows**: Geralmente já incluído

### Bibliotecas Necessárias

- `pyserial` - Comunicação serial com hardware
- `numpy` - Processamento numérico e operações vetoriais
- `matplotlib` - Visualização de gráficos e sinais
- `pyautogui` - Automação de teclado/mouse para aplicações
- `tkinter` - Interface gráfica (geralmente incluído no Python)

### Hardware

- **Microcontrolador**: STM32F401 configurado para capturar sinais IR e enviar dados via serial
- **Porta serial**: Configurada (padrão: COM6 no Windows)
- **Baud rate**: 2000000 bps (2 Mbps) para alta velocidade de transmissão
- **Conversor A/D**: Integrado no STM32F401, amostragem contínua

---

## 📁 Estrutura do Projeto

```
dataLoggerTELC2/
│
├── 📄 app_Keyboard.py          # Aplicação: controle de teclado via IR
├── 📄 app_Mouse.py             # Aplicação: controle de mouse via IR
├── 📄 app_Debugger.py          # Aplicação: debugger visual com GUI
├── 📄 serialRead.py            # Módulo: leitura serial com trigger
├── 📄 plotTeste.py             # Módulo: plotagem de dados
├── 📄 decodificador.py         # Módulo: decodificador NEC IR
├── 📄 conversorAD.py           # Módulo: conversão A/D e binarização
├── 📄 detectorJanelaSinal.py   # Módulo: detecção de janelas de sinal
├── 📄 old.py                   # Versão legada (referência)
├── 📄 dados.txt                # Arquivo de dados capturados
├── 📄 requirements.txt         # Dependências Python do projeto
└── 📄 README.md                # Este arquivo
```

---

## 📝 Descrição Detalhada dos Arquivos

### 🔹 `serialRead.py`

**Função Principal**: Módulo responsável pela leitura de dados seriais com sistema de trigger baseado em máquina de estados.

#### Lógica e Algoritmo

Este módulo implementa uma **máquina de estados finita (FSM)** com dois estados principais:

1. **Estado IDLE**: Aguarda continuamente por um valor que ative o trigger
2. **Estado TRIGGERED**: Captura dados após o trigger ser detectado

#### Fluxo Detalhado

```
1. Inicialização:
   - Abre porta serial com timeout de 1 segundo
   - Configura buffer otimizado (rx_size=16000, tx_size=16000)
   - Limpa buffer de entrada
   - Inicializa estado = 'IDLE'

2. Loop Principal:
   while True:
     - Lê todos os bytes disponíveis (ser.in_waiting)
     - Para cada byte recebido:
       if estado == 'IDLE':
         - Verifica se valor < TRIGGER_VALUE
         - Se sim: muda para 'TRIGGERED', inicia captura, registra tempo
       elif estado == 'TRIGGERED':
         - Adiciona valor à lista de captura
         - Verifica se len(captura) >= CAPTURE_LENGTH
         - Se sim: calcula duração, retorna dados
```

#### Características Técnicas

- **Leitura não-bloqueante**: Usa `ser.in_waiting` para ler apenas bytes disponíveis
- **Buffer otimizado**: 16KB de buffer para alta taxa de transmissão (2 Mbps)
- **Trigger inteligente**: Detecta quando sinal cai abaixo do threshold (indicando início do pulso IR)
- **Captura fixa**: Após trigger, captura exatamente `CAPTURE_LENGTH` amostras
- **Medição de tempo**: Calcula duração real da captura para análise de frequência

#### Função Principal

```python
r_serial(port, baud, TRIGGER_VALUE, CAPTURE_LENGTH)
```

**Parâmetros**:

- `port` (str): Porta serial (ex: 'COM6' no Windows, '/dev/ttyUSB0' no Linux)
- `baud` (int): Taxa de transmissão em bps (ex: 2000000)
- `TRIGGER_VALUE` (int): Valor de threshold para trigger (0-255, padrão: 200)
- `CAPTURE_LENGTH` (int): Número de amostras a capturar após trigger (padrão: 8500)

**Retorno**:

- `data` (list): Lista de valores uint8 capturados
- `duracao` (float): Tempo de captura em segundos (precisão de microssegundos)

#### Decisões de Design

- **Por que trigger < threshold?**: Sinais IR começam com um pulso de sincronização que geralmente tem amplitude menor que o ruído de fundo
- **Por que 8500 amostras?**: Baseado na duração típica de um frame NEC IR (~103ms a 82.3kHz)
- **Por que buffer de 16KB?**: Permite armazenar múltiplas capturas sem perda de dados na alta velocidade

#### Tratamento de Erros

- `KeyboardInterrupt`: Permite interrupção limpa pelo usuário (Ctrl+C)
- `StopIteration`: Tratado silenciosamente (não esperado no fluxo normal)
- `finally`: Garante fechamento da porta serial mesmo em caso de erro

---

### 🔹 `conversorAD.py`

**Função Principal**: Conversão de sinal analógico (uint8) para sinal digital binário (0 ou 1) através de normalização e binarização adaptativa.

#### Lógica e Algoritmo

Este módulo implementa um algoritmo de **binarização adaptativa** que funciona em duas etapas:

**Etapa 1: Normalização e Inversão**

```
1. Calcula estatísticas do sinal:
   signal_max = max(signal)
   signal_min = min(signal)
   avg = (signal_max + signal_min) / 2  # Ponto médio
   delta = signal_max - signal_min      # Amplitude total

2. Normaliza e inverte cada amostra:
   Para cada s em signal:
     normalized = (s - avg) / delta + 0.5  # Normaliza para [0, 1]
     inverted = -1 * normalized + 1        # Inverte o sinal
```

**Etapa 2: Binarização**

```
1. Recalcula estatísticas do sinal invertido:
   signal_max = max(signal_inverted)
   signal_min = min(signal_inverted)
   avg = (signal_max + signal_min) / 2

2. Binariza baseado na nova média:
   Para cada s em signal_inverted:
     if s > avg: signal_bin = 1
     else: signal_bin = 0
```

#### Por que Inverter o Sinal?

Sinais IR capturados via A/D geralmente têm:

- **Nível alto** quando não há sinal IR (ruído de fundo)
- **Nível baixo** quando há pulso IR (sinal modulado)

A inversão garante que:

- `1` = presença de pulso IR
- `0` = ausência de pulso IR

#### Características Técnicas

- **Adaptativo**: Não requer threshold fixo, adapta-se ao sinal
- **Robusto**: Funciona mesmo com offset DC variável
- **Simples**: Algoritmo O(n) com apenas duas passadas pelo sinal

#### Função Principal

```python
ad(signal)
```

**Parâmetros**:

- `signal` (list): Lista de valores analógicos uint8 (0-255)

**Retorno**:

- `signal_bin` (list): Lista binária (0 ou 1) com mesmo comprimento

#### Exemplo de Transformação

```
Entrada:  [200, 150, 100, 180, 120, 190]
          ↓ Normalização e Inversão
Intermediário: [0.2, 0.6, 1.0, 0.3, 0.8, 0.25]
          ↓ Binarização (threshold = 0.5)
Saída:    [0, 1, 1, 0, 1, 0]
```

---

### 🔹 `decodificador.py`

**Função Principal**: Decodificador completo do protocolo NEC IR que extrai endereço e comando de um sinal binário, com validação de integridade.

#### Protocolo NEC IR

O protocolo NEC IR transmite dados em um frame de 32 bits:

- **Bits 0-15**: Endereço (16 bits, LSB primeiro)
- **Bits 16-23**: Comando (8 bits, LSB primeiro)
- **Bits 24-31**: Comando invertido (8 bits, para validação)

#### Lógica e Algoritmo

**Etapa 1: Detecção de Edges**

```python
# Calcula diferença entre amostras consecutivas
signal_diff = np.diff([0] + signal)

# Encontra transições
rising_edges = índices onde signal_diff > 0   # 0 → 1
falling_edges = índices onde signal_diff < 0  # 1 → 0
```

**Etapa 2: Decodificação de Bits**

O protocolo NEC codifica bits pela **duração do espaço** entre pulsos:

- **Bit 0**: Espaço de ~562µs entre rising edges
- **Bit 1**: Espaço de ~1687µs entre rising edges

```python
Para cada par de edges consecutivos:
  space_duration = (rising_edge[i+1] - falling_edge[i]) / fs
  
  if space_duration ≈ 562µs (com tolerância 20%):
    bit = 0
  elif space_duration ≈ 1687µs (com tolerância 20%):
    bit = 1
```

**Etapa 3: Extração de Dados**

```python
if len(bits) == 32:
  address_bits = bits[0:16]
  command_bits = bits[16:24]
  inv_command_bits = bits[24:32]
  
  # Converte bits para inteiro (LSB primeiro)
  address = bits_to_int(address_bits)
  command = bits_to_int(command_bits)
  inv_command = bits_to_int(inv_command_bits)
```

**Etapa 4: Validação**

```python
# Verifica se comando invertido é complemento do comando
if (command ^ 0xFF) == inv_command:
  status = 2  # ✅ Validação passou
else:
  status = 1  # ❌ Validação falhou
```

#### Função Principal

```python
nec_decoder(signal, fs)
```

**Parâmetros**:

- `signal` (list/array): Sinal binário (0 ou 1)
- `fs` (float): Frequência de amostragem em Hz (ex: 82333)

**Retorno**:

- `decoded_address` (int): Endereço decodificado (16 bits)
- `decoded_command` (int): Comando decodificado (8 bits)
- `status` (int): Status da decodificação (0-3)
- `r_edg` (int): Número de rising edges detectados
- `f_edg` (int): Número de falling edges detectados
- `bits` (list): Lista de bits detectados (pode ter menos de 32)

#### Status de Decodificação

| Status | Significado        | Descrição                                            |
| ------ | ------------------ | ------------------------------------------------------ |
| `0`  | Não realizada     | Não houve tentativa de decodificação                |
| `1`  | Validação falhou | 32 bits detectados, mas comando invertido não confere |
| `2`  | ✅ Sucesso         | 32 bits detectados e validação passou                |
| `3`  | Bits insuficientes | Menos de 32 bits detectados                            |

#### Tolerâncias do Protocolo

- `T_bit_off`: 562µs ± 20% (450µs - 674µs) para bit 0
- `T_bit_on`: 1687µs ± 20% (1350µs - 2024µs) para bit 1
- `T_tolerance`: 0.2 (20% de tolerância)

#### Características Técnicas

- **Robusto a ruído**: Tolerância de 20% compensa variações de clock
- **Validação de integridade**: Verifica comando invertido para detectar erros
- **Detecção de edges**: Usa numpy para eficiência em sinais grandes
- **LSB primeiro**: Protocolo NEC transmite bits menos significativos primeiro

#### Tratamento de Primeiro Edge

O código ignora o primeiro rising edge e falling edge, pois geralmente correspondem ao pulso de sincronização inicial, não a dados.

---

### 🔹 `plotTeste.py`

**Função Principal**: Módulo simples para visualização rápida de dados ADC em gráfico.

#### Lógica

Cria um gráfico de linha simples mostrando valores ADC vs. índice da amostra.

#### Função Principal

```python
pltTeste(data)
```

**Parâmetros**:

- `data` (list): Lista de valores a plotar

**Características**:

- Gráfico de linha com matplotlib
- Grid habilitado para leitura fácil
- Labels em português (Número da linha, Valor ADC)
- Bloqueia execução até fechar a janela (`plt.show()`)

#### Uso

Principalmente para debug rápido e visualização de sinais capturados.

---

### 🔹 `app_Debugger.py`

**Função Principal**: Aplicação GUI completa para debug, visualização e análise de sinais IR em tempo real.

#### Arquitetura da Aplicação

A aplicação usa **threading** para separar a interface gráfica (thread principal) da captura de dados (thread secundária), evitando travamentos da UI.

#### Estrutura da Interface

```
┌─────────────────────────────────────────────────────────┐
│              Data Logger TELC2                          │
├──────────────────┬──────────────────────────────────────┤
│  Configuração    │  Gráficos                            │
│                  │                                      │
│  Serial Port     │  ┌────────────────────────────────┐  │
│  Baud Rate       │  │   Raw data (gráfico linha)     │  │
│  Trigger Value   │  └────────────────────────────────┘  │
│  Capture Length  │                                      │
│                  │  ┌────────────────────────────────┐  │
│  ┌────────────┐  │  │ Binary data (gráfico step)     │  │
│  │    Log     │  │  └────────────────────────────────┘  │
│  │            │  │                                      │
│  │  [scroll]  │  │                                      │
│  └────────────┘  │                                      │
│                  │                                      │
│  [Start] [Stop]  │                                      │
│  [Clear]         │                                      │
└──────────────────┴──────────────────────────────────────┘
```

#### Lógica e Fluxo

**Inicialização**:

```python
1. Cria janela Tkinter (1300x530 pixels)
2. Configura layout em duas colunas
3. Cria campos de entrada para parâmetros
4. Cria área de log com scroll
5. Cria dois gráficos matplotlib (raw e binary)
6. Cria botões de controle
```

**Captura Contínua**:

```python
def capture_thread():
  while not stop_event.is_set():
    1. Chama serialRead.r_serial() (bloqueante)
    2. Converte dados com conversorAD.ad()
    3. Decodifica com decodificador.nec_decoder()
    4. Atualiza log com resultados
    5. Atualiza gráficos via root.after() (thread-safe)
    6. Repete até stop_event ser setado
```

**Thread-Safety**:

- `root.after(0, callback)`: Agenda atualização de UI na thread principal
- `log.after(0, lambda: ...)`: Atualiza log de forma thread-safe
- `capture_stop_event`: Event para comunicação entre threads

#### Funcionalidades Detalhadas

1. **Configuração Dinâmica**: Todos os parâmetros podem ser alterados via interface
2. **Captura Contínua**: Loop infinito até clicar Stop
3. **Visualização Dupla**:
   - **Raw data**: Gráfico de linha dos dados brutos
   - **Binary data**: Gráfico step dos dados binarizados
4. **Log Detalhado**: Mostra status, edges, bits, endereço e comando
5. **Clear**: Limpa log e reseta gráficos

#### Tratamento de Erros

- Validação de parâmetros antes de iniciar captura
- Try-except na thread de captura para não travar UI
- Fallback se decodificador retornar formato diferente

#### Decisões de Design

- **Threading**: Necessário porque `r_serial()` é bloqueante
- **Dois gráficos**: Permite comparar sinal antes e depois da binarização
- **Step plot para binary**: Melhor visualização de sinais digitais
- **Log com scroll**: Histórico completo de todas as capturas

---

### 🔹 `app_Keyboard.py`

**Função Principal**: Aplicação que controla o teclado do computador baseado em comandos IR decodificados.

#### Lógica e Fluxo

```python
Loop Infinito:
  1. Aguarda trigger e captura dados (serialRead.r_serial)
  2. Converte para binário (conversorAD.ad)
  3. Decodifica protocolo NEC (decodificador.nec_decoder)
  4. Mapeia comando para ação:
     - 0x0  → Nenhuma ação (mantém ação anterior)
     - 0x8  → Ação 1 (Enter)
     - 0x12 → Ação 2 (W)
     - 0x18 → Ação 3 (S)
     - 0x14 → Ação 4 (A)
     - 0x16 → Ação 5 (D)
  5. Executa ação no teclado (pyautogui.press)
  6. Repete
```

#### Mapeamento de Comandos

| Comando IR | Ação  | Tecla | Uso Típico                   |
| ---------- | ------- | ----- | ----------------------------- |
| `0x0`    | Nenhuma | -     | Mantém estado anterior       |
| `0x8`    | Enter   | Enter | Confirmação/Seleção       |
| `0x12`   | W       | W     | Movimento para frente (jogos) |
| `0x18`   | S       | S     | Movimento para trás (jogos)  |
| `0x14`   | A       | A     | Movimento esquerda (jogos)    |
| `0x16`   | D       | D     | Movimento direita (jogos)     |

#### Características

- **Loop contínuo**: Fica aguardando comandos indefinidamente
- **Mapeamento fixo**: Comandos hardcoded (pode ser personalizado)
- **Sem validação de status**: Executa ação mesmo se decodificação falhar (pode melhorar)
- **Print de debug**: Mostra comando recebido e ação executada

#### Aplicação Prática

Ideal para:

- Controle de jogos via controle remoto
- Apresentações controladas por IR
- Automação de tarefas repetitivas

---

### 🔹 `app_Mouse.py`

**Função Principal**: Aplicação que controla o mouse do computador baseado em comandos IR decodificados.

#### Lógica e Fluxo

Similar ao `app_Keyboard.py`, mas executa ações de mouse:

```python
Loop Infinito:
  1. Aguarda trigger e captura dados
  2. Converte para binário
  3. Decodifica protocolo NEC
  4. Mapeia comando para ação de mouse:
     - 0x0  → Nenhuma ação
     - 0x8  → Clique esquerdo
     - 0x12 → Move para cima (10px)
     - 0x18 → Move para baixo (10px)
     - 0x14 → Move para esquerda (10px)
     - 0x16 → Move para direita (10px)
  5. Executa ação (pyautogui)
  6. Repete
```

#### Mapeamento de Comandos

| Comando IR | Ação   | Função pyautogui  | Descrição                  |
| ---------- | -------- | ------------------- | ---------------------------- |
| `0x0`    | Nenhuma  | -                   | Mantém estado               |
| `0x8`    | Clique   | `leftClick()`     | Clique esquerdo do mouse     |
| `0x12`   | Cima     | `moveRel(0, -10)` | Move 10 pixels para cima     |
| `0x18`   | Baixo    | `moveRel(0, 10)`  | Move 10 pixels para baixo    |
| `0x14`   | Esquerda | `moveRel(-10, 0)` | Move 10 pixels para esquerda |
| `0x16`   | Direita  | `moveRel(10, 0)`  | Move 10 pixels para direita  |

#### Características

- **Movimento relativo**: Usa `moveRel()` para movimento incremental
- **Incremento fixo**: 10 pixels por comando (pode ser ajustado)
- **Sistema de coordenadas**: Y diminui para cima (padrão de tela)

#### Aplicação Prática

Ideal para:

- Controle de cursor em apresentações
- Navegação em interfaces touchless
- Acessibilidade para usuários com limitações motoras

---

### 🔹 `detectorJanelaSinal.py`

**Função Principal**: Script para detectar e extrair frames de sinal digital baseado em padrão de sincronização.

#### Lógica e Algoritmo

Implementa uma **máquina de estados** para detectar frames:

**Estados**:

1. `WAITING_SYNC_RISING_EDGE`: Aguarda borda de subida (nível baixo → alto)
2. `WAITING_SYNC_FALLING_EDGE`: Aguarda borda de descida (nível alto → baixo)

**Algoritmo**:

```python
Para cada amostra i no sinal:
  if estado == WAITING_SYNC_RISING_EDGE:
    if signal[i] == 1:  # Detectou nível alto
      i_start = i
      estado = WAITING_SYNC_FALLING_EDGE
  
  elif estado == WAITING_SYNC_FALLING_EDGE:
    if signal[i] == 0:  # Detectou nível baixo
      i_end = i
      duracao_pulso = i_end - i_start
  
      # Valida se duração está dentro da tolerância
      erro = abs(duracao_pulso - sync_high_duration) / sync_high_duration
      if erro < sync_high_duration_max_error:
        # Frame válido encontrado!
        frames.append([i_start, i_end + Frame_size])
        i = i_end + Frame_size  # Pula para depois do frame
  
      estado = WAITING_SYNC_RISING_EDGE
```

#### Parâmetros

- `Frame_size`: 5200 amostras (tamanho esperado de um frame)
- `sync_high_duration`: 736 amostras (duração do pulso de sincronização)
- `sync_high_duration_max_error`: 0.1 (10% de tolerância)

#### Visualização

Após detectar frames, cria subplots mostrando cada frame extraído:

- Um subplot por frame
- Gráfico de linha com grid
- Título mostra índices do frame

#### Uso

Processa arquivo de sinal digital pré-capturado (`sinDig.txt`) e extrai múltiplos frames para análise.

---

### 🔹 `app_old.py`

**Função Principal**: Versão legada do código de leitura serial, mantida como referência histórica.

#### Diferenças da Versão Atual

| Característica      | Versão Antiga (`old.py`)      | Versão Atual (`serialRead.py`) |
| -------------------- | -------------------------------- | --------------------------------- |
| **Trigger**    | Valor <= 200                     | Valor < 200                       |
| **Captura**    | Baseada em tempo (90ms)          | Baseada em número de amostras    |
| **Salvamento** | Salva em arquivo automaticamente | Retorna dados para processamento  |
| **Leitura**    | 1 byte por vez                   | Lê todos os bytes disponíveis   |
| **Buffer**     | Padrão do sistema               | Otimizado (16KB)                  |

#### Lógica Antiga

```python
1. Lê 1 byte por vez
2. Se valor <= 200:
   - Inicia captura baseada em tempo
   - Captura por exatamente 90ms
   - Salva todos os valores em arquivo
   - Para
```

#### Por que Foi Substituído?

- **Captura baseada em tempo**: Inconsistente com frequências variáveis
- **Leitura byte-a-byte**: Muito lenta para 2 Mbps
- **Salvamento automático**: Menos flexível que retornar dados
- **Sem controle de buffer**: Pode perder dados em alta velocidade

---

## 🔄 Fluxo de Dados

### Fluxo Completo do Sistema

```
┌─────────────┐
│  STM32F401  │  Captura sinal IR via A/D
│  (Hardware) │  Amostragem contínua @ 82.3kHz
└──────┬──────┘
       │ Serial (COM6, 2 Mbps)
       ▼
┌─────────────┐
│serialRead.py│  Máquina de estados:
│             │  1. IDLE: aguarda trigger
│             │  2. TRIGGERED: captura 8500 amostras
└──────┬──────┘
       │ Lista de uint8 (0-255)
       ▼
┌─────────────┐
│conversorAD  │  Processamento:
│    .py      │  1. Normalização
│             │  2. Inversão
│             │  3. Binarização
└──────┬──────┘
       │ Lista binária (0 ou 1)
       ▼
┌─────────────┐
│decodificador│  Decodificação NEC:
│    .py      │  1. Detecção de edges
│             │  2. Decodificação de bits
│             │  3. Extração de dados
│             │  4. Validação
└──────┬──────┘
       │ (address, command, status)
       ▼
┌─────────────┐
│  Aplicação  │  Executa ação:
│  (app_*.py) │  - Keyboard: pressiona tecla
│             │  - Mouse: move/clica
│             │  - Debugger: mostra gráficos
└─────────────┘
```

### Exemplo de Dados em Cada Etapa

**1. Saída do Hardware (serialRead)**:

```
[200, 195, 180, 150, 120, 100, 80, 150, 180, 200, ...]
```

**2. Após conversorAD**:

```
[0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, ...]
```

**3. Após decodificador**:

```
address = 0x0000
command = 0x12
status = 2 (✅ válido)
```

**4. Ação executada**:

```
app_Keyboard: pressiona tecla 'W'
app_Mouse: move mouse 10px para cima
```

---

## 🚀 Como Usar

### 1. Configuração Inicial

1. **Conecte o hardware**: STM32F401 à porta serial do computador
2. **Identifique a porta**:
   - Windows: Gerenciador de Dispositivos → Portas (COM e LPT)
   - Linux: `ls /dev/tty*` ou `dmesg | grep tty`
3. **Configure no código**: Altere `SERIAL_PORT` se necessário (padrão: `COM6`)
4. **Verifique baud rate**: Deve corresponder ao configurado no STM32 (padrão: `2000000`)

### 2. Executar Aplicações

#### Debugger Visual (Recomendado para começar)

```bash
python app_Debugger.py
```

**Passos**:

1. Abre interface gráfica
2. Configure parâmetros se necessário
3. Clique em "Start Capture"
4. Aponte controle remoto e pressione botão
5. Observe gráficos e log
6. Clique "Stop Capture" para parar

#### Controle de Teclado

```bash
python app_Keyboard.py
```

**Passos**:

1. Execute o script
2. Aponte controle remoto
3. Pressione botões mapeados
4. Teclas serão pressionadas automaticamente
5. Pressione Ctrl+C para sair

#### Controle de Mouse

```bash
python app_Mouse.py
```

**Passos**:

1. Execute o script
2. Aponte controle remoto
3. Pressione botões mapeados
4. Mouse será controlado automaticamente
5. Pressione Ctrl+C para sair

### 3. Teste de Módulos Individuais

#### Teste de Captura Serial

```python
import serialRead as sr

data, duracao = sr.r_serial('COM6', 2000000, 200, 8500)
print(f"Capturados {len(data)} valores em {duracao:.3f}s")
print(f"Primeiros valores: {data[:10]}")
```

#### Teste de Conversão A/D

```python
import conversorAD as cvad

# Sinal simulado
signal = [200, 150, 100, 180, 120, 190, 110, 170]
bin_signal = cvad.ad(signal)
print(f"Original: {signal}")
print(f"Binário:  {bin_signal}")
```

#### Teste de Decodificação

```python
import decodificador as dec

# Sinal binário simulado (32 bits NEC)
bin_data = [0, 1, 0, 1, 1, 0, 0, 1, ...]  # 32 bits
fs = 82333
address, command, status, r_edg, f_edg, bits = dec.nec_decoder(bin_data, fs)

if status == 2:
    print(f"✅ Endereço: {hex(address)}, Comando: {hex(command)}")
else:
    print(f"❌ Decodificação falhou (status: {status})")
```

---

## ⚙️ Configuração

### Parâmetros Principais

| Parâmetro         | Valor Padrão | Descrição                     | Impacto                                 |
| ------------------ | ------------- | ------------------------------- | --------------------------------------- |
| `SERIAL_PORT`    | `'COM6'`    | Porta serial do dispositivo     | Crítico: deve corresponder ao hardware |
| `BAUD_RATE`      | `2000000`   | Taxa de transmissão em bps     | Crítico: deve corresponder ao STM32    |
| `TRIGGER_VALUE`  | `200`       | Valor de threshold para trigger | Ajuste se trigger não funciona         |
| `CAPTURE_LENGTH` | `8500`      | Número de amostras a capturar  | Ajuste se sinal for mais longo          |
| `fs`             | `82333`     | Frequência de amostragem (Hz)  | Crítico para decodificação correta   |

### Ajuste de Parâmetros

#### Para melhorar a captura:

1. **Trigger não detectado**:

   - Diminua `TRIGGER_VALUE` (ex: 150 ou 180)
   - Verifique se sinal está chegando (use debugger)
2. **Captura incompleta**:

   - Aumente `CAPTURE_LENGTH` (ex: 10000 ou 12000)
   - Verifique duração do sinal no debugger
3. **Dados corrompidos**:

   - Verifique baud rate (deve ser exato)
   - Verifique qualidade do cabo USB
   - Reduza baud rate se necessário (ex: 115200)

#### Para melhorar a decodificação:

1. **Status 3 (bits insuficientes)**:

   - Aumente `CAPTURE_LENGTH`
   - Verifique se `fs` está correto
   - Verifique se sinal está completo
2. **Status 1 (validação falhou)**:

   - Ajuste `fs` (pode estar ligeiramente errado)
   - Verifique qualidade do sinal (ruído)
   - Ajuste tolerâncias em `decodificador.py` se necessário
3. **Bits incorretos**:

   - Verifique `fs` com mais precisão
   - Use debugger para visualizar sinal binário
   - Ajuste `T_tolerance` em `decodificador.py`

### Cálculo de Frequência de Amostragem

Se você souber a duração real da captura:

```python
fs = len(data) / duracao
```

Exemplo:

- `len(data) = 8500` amostras
- `duracao = 0.103` segundos
- `fs = 8500 / 0.103 ≈ 82524` Hz

---

## 📊 Exemplos de Uso

### Exemplo 1: Captura e Visualização Completa

```python
import serialRead as sr
import plotTeste as plt
import conversorAD as cvad

# Captura dados
print("Aguardando trigger...")
data, duracao = sr.r_serial('COM6', 2000000, 200, 8500)
print(f"Capturados {len(data)} valores em {duracao:.6f}s")
print(f"Frequência de amostragem estimada: {len(data)/duracao:.2f} Hz")

# Converte para binário
bin_data = cvad.ad(data)
print(f"Sinal binarizado: {sum(bin_data)} bits '1' de {len(bin_data)} total")

# Visualiza dados brutos
plt.pltTeste(data)
```

### Exemplo 2: Decodificação Completa com Validação

```python
import serialRead as sr
import conversorAD as cvad
import decodificador as dec

# Captura
data, duracao = sr.r_serial('COM6', 2000000, 200, 8500)

# Processa
bin_data = cvad.ad(data)
fs = len(data) / duracao  # Calcula fs real
print(f"Frequência de amostragem: {fs:.2f} Hz")

# Decodifica
address, command, status, r_edg, f_edg, bits = dec.nec_decoder(bin_data, fs)

# Resultado
print(f"\n=== Resultado da Decodificação ===")
print(f"Rising edges: {r_edg}")
print(f"Falling edges: {f_edg}")
print(f"Bits detectados: {len(bits)}")

if status == 2:
    print(f"✅ COMANDO VÁLIDO")
    print(f"Endereço: 0x{address:04X} ({address})")
    print(f"Comando:  0x{command:02X} ({command})")
    print(f"Bits: {bits}")
elif status == 1:
    print(f"⚠️  Validação falhou (comando invertido não confere)")
elif status == 3:
    print(f"❌ Bits insuficientes ({len(bits)}/32)")
else:
    print(f"❌ Decodificação não realizada")
```

### Exemplo 3: Controle Personalizado com Múltiplos Comandos

```python
import serialRead as sr
import conversorAD as cvad
import decodificador as dec
import pyautogui as pag
import time

# Mapeamento personalizado
COMANDOS = {
    0x0:  lambda: None,  # Nenhuma ação
    0x8:  lambda: pag.press('space'),
    0x12: lambda: pag.press('w'),
    0x18: lambda: pag.press('s'),
    0x14: lambda: pag.press('a'),
    0x16: lambda: pag.press('d'),
    0x15: lambda: pag.hotkey('ctrl', 'c'),  # Novo comando
    0x17: lambda: pag.hotkey('ctrl', 'v'),  # Novo comando
}

print("Sistema de controle IR iniciado. Pressione Ctrl+C para sair.")
fs = 82333

while True:
    try:
        # Captura e processa
        data, _ = sr.r_serial('COM6', 2000000, 200, 8500)
        bin_data = cvad.ad(data)
        address, command, status, _, _, _ = dec.nec_decoder(bin_data, fs)
    
        # Executa ação se válido
        if status == 2 and command in COMANDOS:
            print(f"Comando recebido: 0x{command:02X}")
            COMANDOS[command]()
        elif status == 2:
            print(f"Comando desconhecido: 0x{command:02X}")
    
        # Pequeno delay para evitar múltiplas execuções
        time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nSistema encerrado.")
        break
    except Exception as e:
        print(f"Erro: {e}")
        time.sleep(1)
```

### Exemplo 4: Análise Estatística de Múltiplas Capturas

```python
import serialRead as sr
import conversorAD as cvad
import decodificador as dec

fs = 82333
sucessos = 0
falhas = 0
comandos = {}

print("Iniciando análise estatística (10 capturas)...")

for i in range(10):
    data, duracao = sr.r_serial('COM6', 2000000, 200, 8500)
    bin_data = cvad.ad(data)
    address, command, status, _, _, _ = dec.nec_decoder(bin_data, fs)
  
    if status == 2:
        sucessos += 1
        if command in comandos:
            comandos[command] += 1
        else:
            comandos[command] = 1
        print(f"Captura {i+1}: ✅ Comando 0x{command:02X}")
    else:
        falhas += 1
        print(f"Captura {i+1}: ❌ Status {status}")

print(f"\n=== Estatísticas ===")
print(f"Sucessos: {sucessos}/10 ({sucessos*10}%)")
print(f"Falhas: {falhas}/10 ({falhas*10}%)")
print(f"\nComandos recebidos:")
for cmd, count in comandos.items():
    print(f"  0x{cmd:02X}: {count} vezes")
```

---

## 🔍 Troubleshooting

### Problema: Trigger não detectado

**Sintomas**: Programa fica travado em "Aguardando trigger..."

**Possíveis causas**:

1. `TRIGGER_VALUE` muito alto
2. Sinal não está chegando na serial
3. Hardware não está transmitindo

**Soluções**:

- Diminua `TRIGGER_VALUE` (ex: 150, 180)
- Verifique conexão serial
- Use debugger para ver se há dados chegando
- Verifique se STM32 está configurado corretamente

### Problema: Decodificação falha (status 1 ou 3)

**Sintomas**: Status 1 (validação falhou) ou 3 (bits insuficientes)

**Possíveis causas**:

1. `fs` incorreto
2. `CAPTURE_LENGTH` muito pequeno
3. Sinal com muito ruído
4. Tolerâncias muito restritivas

**Soluções**:

- Calcule `fs` real: `fs = len(data) / duracao`
- Aumente `CAPTURE_LENGTH` (ex: 10000)
- Use debugger para visualizar qualidade do sinal
- Ajuste `T_tolerance` em `decodificador.py` (ex: 0.25 para 25%)

### Problema: Porta serial não encontrada

**Sintomas**: Erro `SerialException` ou `FileNotFoundError`

**Soluções**:

- **Windows**: Verifique no Gerenciador de Dispositivos → Portas (COM e LPT)
- **Linux**: Use `ls /dev/tty*` ou `dmesg | grep tty`
- Verifique se cabo USB está conectado
- Verifique se drivers estão instalados
- Tente outra porta (COM7, COM8, etc.)

### Problema: Dados corrompidos

**Sintomas**: Valores inconsistentes, decodificação sempre falha

**Possíveis causas**:

1. Baud rate incorreto
2. Buffer overflow
3. Cabo USB de baixa qualidade
4. Interferência eletromagnética

**Soluções**:

- Verifique baud rate no código e no STM32 (devem ser idênticos)
- Reduza baud rate temporariamente para testar (ex: 115200)
- Use cabo USB de qualidade
- Verifique se há fontes de interferência próximas
- Aumente buffer size se necessário

### Problema: Aplicação não responde (app_Keyboard/Mouse)

**Sintomas**: Programa trava após algumas execuções

**Possíveis causas**:

1. Loop infinito sem tratamento de erro
2. Serial não fecha corretamente
3. pyautogui bloqueado

**Soluções**:

- Adicione tratamento de exceções no loop
- Verifique se serial fecha no `finally`
- Adicione delays entre comandos
- Use threading para não bloquear

### Problema: Gráficos não atualizam (app_Debugger)

**Sintomas**: Gráficos ficam vazios ou não mudam

**Possíveis causas**:

1. Thread não está atualizando UI corretamente
2. Dados vazios sendo passados
3. Matplotlib não está redesenhand

**Soluções**:

- Verifique se `root.after()` está sendo usado
- Verifique se dados não estão vazios no log
- Force redraw com `canvas.draw()` ao invés de `draw_idle()`
- Verifique se thread está rodando (veja log)

---

## 📚 Referências

- **Protocolo NEC IR**: Protocolo de comunicação infravermelho usado em controles remotos. Especificação inclui duração de pulsos, estrutura de frames e codificação de bits.
- **Serial Communication**: Comunicação assíncrona via porta serial. Padrão RS-232 com configurações de baud rate, paridade e bits de stop.
- **Signal Processing**: Processamento e binarização de sinais analógicos. Técnicas de normalização, threshold adaptativo e detecção de edges.
- **STM32F401**: Microcontrolador ARM Cortex-M4 usado no hardware de captura. Suporta ADC de alta velocidade e comunicação serial.

---

## 👨‍💻 Autores

Projeto desenvolvido para a disciplina **TELC2**

**Equipe**:

- Davi Cunha
- Fábio Poncio
- Luigi Nery

---

## 📄 Licença

Este projeto é para fins educacionais.

---

## 🔄 Histórico de Versões

- **v1.0** (2025): Versão inicial com captura serial e decodificação NEC
- **v1.1** (2025): Adicionado app_Debugger com GUI
- **v1.2** (2025): Melhorias em serialRead com buffer otimizado

---

**Última atualização**: 2025
