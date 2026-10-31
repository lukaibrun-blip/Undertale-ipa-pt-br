# Undertale PT-BR para iOS

Este repositório organiza a validação de uma localização brasileira para o port de Undertale para iOS. Ele não distribui o jogo nem inclui arquivos de jogo.

## Estado

- O app analisado nesta conversa usa o identificador com.jockeholm.undertale e a versão 2.0.0.
- O pacote iOS guarda o recurso do jogo em Payload/UNDERTALE.app/games/game.ios. Um arquivo data.win de PC não deve ser tratado como substituto direto.
- Ainda não foi verificado um recurso game.ios PT-BR compatível com esta versão.

## Verificador de entradas

O script tools/validate_inputs.py verifica a estrutura básica do IPA, o identificador/versão do app e os marcadores iniciais do arquivo candidato. O marcador FORM/GEN8, sozinho, não confirma plataforma, versão nem idioma.

Ele não traduz, altera, descriptografa, assina ou recompila o jogo. Qualquer alteração no conteúdo do app invalida a assinatura existente; este projeto não tenta contornar proteção de plataforma.

Uso local:

~~~bash
python3 tools/validate_inputs.py --ipa /caminho/para/app.ipa --game-ios /caminho/para/game.ios
~~~

A versão esperada pode ser informada com --expected-version; o identificador pode ser informado com --expected-bundle-id.

## GitHub Actions

O workflow executa testes automatizados do verificador com arquivos de teste sintéticos. Ele não baixa, armazena, assina nem publica IPA ou recursos do jogo.

Não envie IPA, data.win, game.ios, certificados, perfis de provisionamento ou chaves para este repositório público. Para qualquer build pessoal, use uma cópia do app que você tem direito de modificar e uma assinatura própria válida.
