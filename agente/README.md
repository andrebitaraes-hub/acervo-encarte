# Agente de encarte + acervo

Com isto instalado, o seu agente de encarte (Gondola) faz, para cada produto:

1. procura a foto no acervo — pelo **código de barras**, ou pelo **nome** se for produto a granel;
2. só se não achar, gera pela IA (GPT Image 2) e mostra para você aprovar;
3. no fim, devolve ao acervo as fotos novas **que você aprovar**, para o grupo todo usar.

Assim ninguém paga duas vezes pela mesma foto.

## Instalar (uma vez)

No Terminal, entre na pasta do seu agente de encarte e rode, com o nome do seu mercado:

```
cd ~/agentes-gondola/encarte
bash ~/Documents/acervo-encarte/agente/instalar.sh "Nome do Mercado"
```

Se você ainda não tem o acervo no computador, baixe antes:

```
git clone https://github.com/andrebitaraes-hub/acervo-encarte.git ~/Documents/acervo-encarte
```

Para **mandar** fotos ao acervo, precisa de uma conta no GitHub e do GitHub CLI (`gh`) logado (`gh auth login`). Só para **usar** as fotos, não precisa.

## Reinstalou o Gondola?

Reinstalar o Gondola apaga estes ajustes. É só rodar o `instalar.sh` de novo, que ele recoloca tudo.

## Como a foto chega ao acervo

Quem é dono do acervo envia direto. Os demais enviam por **proposta** (pull request): a conferência automática checa o padrão e, se a sua conta estiver na lista de confiança, a foto entra sozinha; senão, espera aprovação. As regras das fotos estão no README da raiz.
