# YouTube to MP3 Downloader

Um aplicativo de desktop simples em Python que permite baixar e converter vídeos do YouTube em arquivos MP3, utilizando `yt-dlp` para o download e `moviepy` para a conversão de áudio. A interface gráfica foi desenvolvida usando `Tkinter`.

## Funcionalidades

- **Download de Áudio do YouTube**: Baixa o áudio dos vídeos do YouTube e o converte para MP3.
- **Escolha de Qualidade de Áudio**: Opções de qualidade de áudio (alta, média e baixa).
- **Interface Gráfica**: Interface intuitiva com suporte para até 5 URLs de vídeos por vez.
- **Configurações de Usuário**: Salva automaticamente as preferências de qualidade e o último diretório de salvamento.
- **Barra de Progresso**: Indica o progresso geral do download.
- **Log de Erros**: Armazena erros no processo de download em um arquivo de log.

## Pré-requisitos

Certifique-se de ter as seguintes bibliotecas instaladas:

```bash
pip install yt-dlp moviepy clipboard