# 📡 Data Logger TELC2

Sistema completo de captura, processamento e decodificação de sinais de controle remoto infravermelho (IR) via comunicação serial. Este projeto implementa um data logger que captura sinais analógicos de um conversor A/D, processa os dados e decodifica comandos do protocolo NEC IR para controlar ações no computador.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Requisitos](#-requisitos)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Descrição dos Arquivos](#-descrição-dos-arquivos)
- [Como Usar](#-como-usar)
- [Configuração](#-configuração)
- [Exemplos de Uso](#-exemplos-de-uso)

---

## 🎯 Visão Geral

Este projeto foi desenvolvido para a disciplina TELC2 e implementa um sistema completo de:

- **Captura de dados seriais** com trigger automático
- **Conversão analógico-digital** e binarização de sinais
- **Decodificação de protocolo NEC IR** (controle remoto)
- **Aplicações práticas**: controle de teclado, mouse e debugger visual
- **Visualização gráfica** dos sinais capturados

O sistema funciona como um intermediário entre um hardware de captura (via serial) e aplicações que executam ações no computador baseadas nos comandos decodificados do controle remoto.

---

## 🔧 Requisitos

### Dependências Python

```bash
pip install pyserial numpy matplotlib pyautogui tkinter
```

### Bibliotecas Necessárias

- `pyserial` - Comunicação serial
- `numpy` - Processamento numérico
- `matplotlib` - Visualização de gráficos
- `pyautogui` - Automação de teclado/mouse
- `tkinter` - Interface gráfica (geralmente incluído no Python)

### Hardware

- Dispositivo serial (STM32F401) configurado para capturar enviar dados  via serial
- Porta serial configurada (padrão: COM6)
- Baud rate: 2000000 bps

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
└── 📄 README.md                # Este arquivo
```

---

## 📝 Descrição dos Arquivos

### 🔹 `serialRead.py`

**Função**: Módulo principal de leitura serial com sistema de trigger.

**Características**:

- Leitura de dados uint8 via porta serial
- Sistema de estados (IDLE → TRIGGERED)
- Trigger automático quando valor < `TRIGGER_VALUE`
- Captura de `CAPTURE_LENGTH` amostras após trigger
- Buffer otimizado (rx_size=16000, tx_size=16000)

**Função Principal**:

```python
r_serial(port, baud, TRIGGER_VALUE, CAPTURE_LENGTH)
```

**Parâmetros**:

- `port`: Porta serial (ex: 'COM6')
- `baud`: Taxa de transmissão (ex: 2000000)
- `TRIGGER_VALUE`: Valor de threshold para trigger (ex: 200)
- `CAPTURE_LENGTH`: Número de amostras a capturar (ex: 8500)

**Retorno**:

- `data`: Lista de valores uint8 capturados
- `duracao`: Tempo de captura em segundos

**Estados**:

- `IDLE`: Aguardando trigger
- `TRIGGERED`: Capturando dados após trigger detectado

---

### 🔹 `conversorAD.py`

**Função**: Conversão de sinal analógico para digital (binarização).

**Processo**:

1. Normalização do sinal (0-1)
2. Inversão do sinal
3. Binarização baseada em threshold (média do sinal)

**Função Principal**:

```python
ad(signal)
```

**Parâmetros**:

- `signal`: Lista de valores analógicos (uint8)

**Retorno**:

- `signal_bin`: Lista binária (0 ou 1)

**Algoritmo**:

- Calcula média entre máximo e mínimo
- Normaliza e inverte o sinal
- Binariza usando nova média como threshold

---

### 🔹 `decodificador.py`

**Função**: Decodificador do protocolo NEC IR (controle remoto).

**Características**:

- Detecção de rising/falling edges
- Decodificação de bits baseada em duração de espaços
- Validação de comando (XOR com complemento)
- Suporte a 32 bits (16 endereço + 8 comando + 8 comando invertido)

**Função Principal**:

```python
nec_decoder(signal, fs)
```

**Parâmetros**:

- `signal`: Sinal binário (0 ou 1)
- `fs`: Frequência de amostragem em Hz (ex: 82333)

**Retorno**:

- `decoded_address`: Endereço decodificado (16 bits)
- `decoded_command`: Comando decodificado (8 bits)
- `status`: Status da decodificação (0-3)
- `r_edg`: Número de rising edges detectados
- `f_edg`: Número de falling edges detectados
- `bits`: Lista de bits detectados

**Status de Decodificação**:

- `0`: Decodificação não realizada
- `1`: Verificação de comando falhou
- `2`: Verificação de comando passou ✅
- `3`: Bits insuficientes para decodificação

**Tolerâncias**:

- `T_bit_off`: 562µs (bit 0)
- `T_bit_on`: 1687µs (bit 1)
- `T_tolerance`: 20% de tolerância

---

### 🔹 `plotTeste.py`

**Função**: Visualização gráfica simples de dados.

**Características**:

- Plot de valores ADC vs. número da linha
- Gráfico com grid e labels
- Visualização rápida para debug

**Função Principal**:

```python
pltTeste(data)
```

**Parâmetros**:

- `data`: Lista de valores a plotar

---

### 🔹 `app_Debugger.py`

**Função**: Aplicação GUI completa para debug e visualização.

**Características**:

- Interface gráfica com Tkinter
- Captura contínua com controle Start/Stop
- Visualização em tempo real de dois gráficos:
  - **Raw data**: Dados brutos capturados
  - **Binary data**: Dados binarizados
- Log detalhado de todas as operações
- Configuração de parâmetros via interface
- Threading para não bloquear a UI

**Funcionalidades**:

- ✅ Configuração de porta serial, baud rate, trigger, etc.
- ✅ Captura contínua com múltiplas leituras
- ✅ Visualização gráfica em tempo real
- ✅ Log de decodificação (endereço, comando, status)
- ✅ Botão Clear para limpar log e gráficos

**Uso**:

```bash
python app_Debugger.py
```

**Layout**:

- **Coluna Esquerda**: Parâmetros de configuração + Log
- **Coluna Direita**: Gráficos (Raw data acima, Binary data abaixo)

---

### 🔹 `app_Keyboard.py`

**Função**: Aplicação que controla o teclado via comandos IR.

**Mapeamento de Comandos**:

- `0x0`: Nenhuma ação
- `0x8`: Pressiona Enter
- `0x12`: Pressiona tecla W
- `0x18`: Pressiona tecla S
- `0x14`: Pressiona tecla A
- `0x16`: Pressiona tecla D

**Uso**:

```bash
python app_Keyboard.py
```

**Fluxo**:

1. Aguarda trigger na serial
2. Captura dados
3. Converte para binário
4. Decodifica protocolo NEC
5. Executa ação no teclado baseada no comando

**Aplicação**: Controle de jogos ou aplicações via controle remoto.

---

### 🔹 `app_Mouse.py`

**Função**: Aplicação que controla o mouse via comandos IR.

**Mapeamento de Comandos**:

- `0x0`: Nenhuma ação
- `0x8`: Clique esquerdo do mouse
- `0x12`: Move mouse para cima (10px)
- `0x18`: Move mouse para baixo (10px)
- `0x14`: Move mouse para esquerda (10px)
- `0x16`: Move mouse para direita (10px)

**Uso**:

```bash
python app_Mouse.py
```

**Fluxo**: Similar ao `app_Keyboard.py`, mas executa ações de mouse.

**Aplicação**: Controle de cursor e cliques via controle remoto.

---

### 🔹 `detectorJanelaSinal.py`

**Função**: Detector de janelas de sinal com sincronização.

**Características**:

- Detecção de frames baseada em sincronização
- Máquina de estados para detecção de bordas
- Validação de duração de pulso de sincronização
- Visualização de múltiplos frames extraídos

**Parâmetros**:

- `Frame_size`: 5200 amostras
- `sync_high_duration`: 736 amostras
- `sync_high_duration_max_error`: 10% de tolerância

**Estados**:

- `WAITING_SYNC_RISING_EDGE`: Aguardando borda de subida
- `WAITING_SYNC_FALLING_EDGE`: Aguardando borda de descida

**Uso**: Processamento de arquivos de sinal digital para extração de frames.

---

### 🔹 `old.py`

**Função**: Versão legada do código de leitura serial.

**Características**:

- Implementação anterior com captura baseada em tempo
- Salva dados em arquivo `dados.txt`
- Trigger simples baseado em valor <= 200
- Captura fixa de 90ms após trigger

**Nota**: Mantido como referência histórica. Não é usado pelas aplicações atuais.

---

## 🚀 Como Usar

### 1. Configuração Inicial

1. Conecte o hardware de captura à porta serial
2. Configure a porta serial no código (padrão: `COM6`)
3. Ajuste o baud rate se necessário (padrão: `2000000`)

### 2. Executar Aplicações

#### Debugger Visual (Recomendado para começar)

```bash
python app_Debugger.py
```

#### Controle de Teclado

```bash
python app_Keyboard.py
```

#### Controle de Mouse

```bash
python app_Mouse.py
```

### 3. Teste de Módulos Individuais

#### Plot de Dados

```python
import plotTeste as plt
data = [100, 150, 200, 180, 120]
plt.pltTeste(data)
```

#### Conversão A/D

```python
import conversorAD as cvad
signal = [100, 150, 200, 180, 120]
bin_signal = cvad.ad(signal)
```

#### Decodificação NEC

```python
import decodificador as dec
bin_data = [0, 1, 0, 1, 1, 0, ...]
fs = 82333
address, command, status, r_edg, f_edg, bits = dec.nec_decoder(bin_data, fs)
```

---

## ⚙️ Configuração

### Parâmetros Principais

| Parâmetro         | Valor Padrão | Descrição                     |
| ------------------ | ------------- | ------------------------------- |
| `SERIAL_PORT`    | `'COM6'`    | Porta serial do dispositivo     |
| `BAUD_RATE`      | `2000000`   | Taxa de transmissão em bps     |
| `TRIGGER_VALUE`  | `200`       | Valor de threshold para trigger |
| `CAPTURE_LENGTH` | `8500`      | Número de amostras a capturar  |
| `fs`             | `82333`     | Frequência de amostragem (Hz)  |

### Ajuste de Parâmetros

**Para melhorar a captura**:

- Ajuste `TRIGGER_VALUE` baseado no nível de ruído
- Aumente `CAPTURE_LENGTH` se o sinal for mais longo
- Verifique `fs` se a decodificação falhar frequentemente

**Para melhorar a decodificação**:

- Ajuste tolerâncias em `decodificador.py` se necessário
- Verifique se `fs` corresponde à frequência real de amostragem

---

## 📊 Exemplos de Uso

### Exemplo 1: Captura e Visualização

```python
import serialRead as sr
import plotTeste as plt
import conversorAD as cvad

# Captura dados
data, duracao = sr.r_serial('COM6', 2000000, 200, 8500)
print(f"Capturados {len(data)} valores em {duracao:.3f}s")

# Converte para binário
bin_data = cvad.ad(data)

# Visualiza
plt.pltTeste(data)
```

### Exemplo 2: Decodificação Completa

```python
import serialRead as sr
import conversorAD as cvad
import decodificador as dec

# Captura
data, _ = sr.r_serial('COM6', 2000000, 200, 8500)

# Processa
bin_data = cvad.ad(data)
fs = 82333
address, command, status, r_edg, f_edg, bits = dec.nec_decoder(bin_data, fs)

# Resultado
if status == 2:
    print(f"✅ Comando válido: {hex(command)}")
    print(f"Endereço: {hex(address)}")
else:
    print(f"❌ Decodificação falhou (status: {status})")
```

### Exemplo 3: Controle Personalizado

```python
import serialRead as sr
import conversorAD as cvad
import decodificador as dec
import pyautogui as pag

# Loop de controle
while True:
    data, _ = sr.r_serial('COM6', 2000000, 200, 8500)
    bin_data = cvad.ad(data)
    address, command, status, _, _, _ = dec.nec_decoder(bin_data, 82333)
  
    if status == 2:  # Comando válido
        if command == 0x8:
            pag.press('space')  # Ação personalizada
        elif command == 0x12:
            pag.hotkey('ctrl', 'c')  # Outra ação
```

---

## 🔍 Troubleshooting

### Problema: Trigger não detectado

- **Solução**: Diminua `TRIGGER_VALUE` ou verifique a conexão serial

### Problema: Decodificação falha (status 1 ou 3)

- **Solução**: Ajuste `fs` ou aumente `CAPTURE_LENGTH`

### Problema: Porta serial não encontrada

- **Solução**: Verifique a porta no Gerenciador de Dispositivos (Windows) ou `ls /dev/tty*` (Linux)

### Problema: Dados corrompidos

- **Solução**: Verifique baud rate, buffer size e qualidade da conexão

---

## 📚 Referências

- **Protocolo NEC IR**: Protocolo de comunicação infravermelho usado em controles remotos
- **Serial Communication**: Comunicação assíncrona via porta serial
- **Signal Processing**: Processamento e binarização de sinais analógicos

---

## 👨‍💻 Autor

Projeto desenvolvido para a disciplina **TELC2 - 10º Período**

---

## 📄 Licença

Este projeto é para fins educacionais.

---

**Última atualização**: 2025
