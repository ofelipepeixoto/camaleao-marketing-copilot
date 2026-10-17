# Usar no ChatGPT

1. Criar um projeto chamado **Camaleão Marketing Copilot**.
2. Copiar o conteúdo de INSTRUCOES.md para as instruções do projeto. Adicionar os arquivos que deseja usar como fontes: este guia, docs/CONTRACT.md e um JSON de examples. Em uma conversa isolada, também é possível colar as instruções e anexar os mesmos arquivos.
3. Para cálculos reproduzíveis, disponibilizar os arquivos de src/camaleao_marketing num ambiente de código autorizado. O projeto ChatGPT por si só não acessa uma pasta do computador ou instala o repositório. Se preferir, anexar um relatório JSON já produzido pelo CLI.
4. Iniciar com uma das mensagens abaixo. Conferir a lista de arquivos lidos e se houve execução real. Não anexar dados pessoais ou credenciais.

## Primeira mensagem

> Use as instruções Camaleão Marketing Copilot. Comece pelos dados fictícios do exemplo de mídia paga. Explique CPA e ROAS, mostre os denominadores e as lacunas de medição. Não publique nem altere campanhas. Se não puder executar o motor Python, declare isso e faça somente a revisão qualitativa.

Outras opções:

- “Revise o snapshot SEO anexado e liste três prioridades. Separe o HTML observado do que depende de consultar o site real.”
- “Leia este relatório do Search Console. Mostre as fórmulas e uma hipótese testável; não estime ganhos sem medição.”
- “Prepare um briefing de conteúdo com pergunta-alvo, fontes necessárias e itens pendentes. Não invente estatísticas ou citações.”

As instruções guiam a conversa. O motor aplica seus limites em código, mas não controla outras ferramentas que o ChatGPT possua. O uso no projeto ChatGPT não foi configurado automaticamente nesta entrega; falta homologação pelo operador em uma conversa nova.

Fonte consultada em 17/10/2026: [documentação oficial de projetos](https://learn.chatgpt.com/docs/projects). Projetos reúnem arquivos e instruções; disponibilidade de ferramentas e acesso a fontes precisam ser conferidos na sessão. Nenhuma promessa de limite de arquivos, plano ou memória foi embutida aqui.
